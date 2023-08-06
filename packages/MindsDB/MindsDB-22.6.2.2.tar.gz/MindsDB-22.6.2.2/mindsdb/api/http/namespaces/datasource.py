import os
import threading
import tempfile
import re
import multipart
import zipfile
import tarfile
import shutil
from pathlib import Path

import mysql.connector
from flask import request, send_file
from flask_restx import Resource, abort     # 'abort' using to return errors as json: {'message': 'error text'}

from mindsdb.utilities.config import Config
from mindsdb.utilities.log import log
from mindsdb.api.http.utils import http_error
from mindsdb.api.http.namespaces.configs.datasources import ns_conf
from mindsdb.api.http.namespaces.entitites.datasources.datasource import (
    put_datasource_params
)
from mindsdb.api.http.namespaces.entitites.datasources.datasource_data import (
    get_datasource_rows_params
)


def parse_filter(key, value):
    result = re.search(r'filter(_*.*)\[(.*)\]', key)
    operator = result.groups()[0].strip('_') or 'like'
    field = result.groups()[1]
    operators_map = {
        'like': 'like',
        'in': 'in',
        'nin': 'not in',
        'gt': '>',
        'lt': '<',
        'gte': '>=',
        'lte': '<=',
        'eq': '=',
        'neq': '!='
    }
    if operator not in operators_map:
        return None
    operator = operators_map[operator]
    return [field, operator, value]


@ns_conf.route('/')
class DatasourcesList(Resource):
    @ns_conf.doc('get_datasources_list')
    def get(self):
        '''List all datasets'''
        return request.default_store.get_datasets()


@ns_conf.route('/<name>')
@ns_conf.param('name', 'Datasource name')
class Datasource(Resource):
    @ns_conf.doc('get_datasource')
    def get(self, name):
        '''return datasource metadata'''
        ds = request.default_store.get_datasource(name)
        if ds is not None:
            return ds
        return '', 404

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''

        try:
            request.default_store.delete_datasource(name)
        except Exception as e:
            log.error(e)
            return http_error(
                400,
                "Error deleting datasource",
                f"There was an error while tring to delete datasource with name '{name}'"
            )
        return '', 200

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    def put(self, name):
        '''add new datasource'''
        data = {}

        def on_field(field):
            name = field.field_name.decode()
            value = field.value.decode()
            data[name] = value

        file_object = None

        def on_file(file):
            nonlocal file_object
            data['file'] = file.file_name.decode()
            file_object = file.file_object

        temp_dir_path = tempfile.mkdtemp(prefix='datasource_file_')

        if request.headers['Content-Type'].startswith('multipart/form-data'):
            parser = multipart.create_form_parser(
                headers=request.headers,
                on_field=on_field,
                on_file=on_file,
                config={
                    'UPLOAD_DIR': temp_dir_path.encode(),    # bytes required
                    'UPLOAD_KEEP_FILENAME': True,
                    'UPLOAD_KEEP_EXTENSIONS': True,
                    'MAX_MEMORY_FILE_SIZE': 0
                }
            )

            while True:
                chunk = request.stream.read(8192)
                if not chunk:
                    break
                parser.write(chunk)
            parser.finalize()
            parser.close()

            if file_object is not None and not file_object.closed:
                file_object.close()
        else:
            data = request.json

        if 'query' in data:
            integration_id = request.json['integration_id']
            integration = request.integration_controller.get(integration_id)
            if integration is None:
                abort(400, f"{integration_id} integration doesn't exist")

            if integration['type'] == 'mongodb':
                data['find'] = data['query']

            request.default_store.save_datasource(name, integration_id, data)
            os.rmdir(temp_dir_path)
            return request.default_store.get_datasource(name)

        ds_name = data['name'] if 'name' in data else name
        source = data['source'] if 'source' in data else name
        source_type = data['source_type']

        try:
            if source_type == 'file':
                file_path = os.path.join(temp_dir_path, data['file'])
                lp = file_path.lower()
                if lp.endswith(('.zip', '.tar.gz')):
                    if lp.endswith('.zip'):
                        with zipfile.ZipFile(file_path) as f:
                            f.extractall(temp_dir_path)
                    elif lp.endswith('.tar.gz'):
                        with tarfile.open(file_path) as f:
                            f.extractall(temp_dir_path)
                    os.remove(file_path)
                    files = os.listdir(temp_dir_path)
                    if len(files) != 1:
                        os.rmdir(temp_dir_path)
                        return http_error(400, 'Wrong content.', 'Archive must contain only one data file.')
                    file_path = os.path.join(temp_dir_path, files[0])
                    source = files[0]
                    if not os.path.isfile(file_path):
                        os.rmdir(temp_dir_path)
                        return http_error(400, 'Wrong content.', 'Archive must contain data file in root.')
                # TODO
                # request.default_store.save_datasource(ds_name, source_type, source, file_path)
                if data['file'] is not None:
                    file_name = Path(data['file']).name
                else:
                    file_name = Path(file_path).name
                file_id = request.default_store.save_file(ds_name, file_path, file_name=file_name)
                request.default_store.save_datasource(ds_name, source_type, source={'mindsdb_file_name': name})
            else:
                file_path = None
                request.default_store.save_datasource(ds_name, source_type, source)
        except Exception as e:
            return http_error(400, 'Error', str(e))
        finally:
            shutil.rmtree(temp_dir_path)

        return request.default_store.get_datasource(ds_name)


def analyzing_thread(name, default_store):
    try:
        from mindsdb.interfaces.storage.db import session
        default_store.start_analysis(name)
        session.close()
    except Exception as e:
        log.error(e)


@ns_conf.route('/<name>/analyze')
@ns_conf.param('name', 'Datasource name')
class Analyze(Resource):
    @ns_conf.doc('analyse_dataset')
    def get(self, name):
        analysis = request.default_store.get_analysis(name)
        if analysis is not None:
            return analysis, 200

        ds = request.default_store.get_datasource(name)
        if ds is None:
            log.error('No valid datasource given')
            abort(400, 'No valid datasource given')

        x = threading.Thread(target=analyzing_thread, args=(name, request.default_store))
        x.start()
        return {'status': 'analyzing'}, 200


@ns_conf.route('/<name>/analyze_refresh')
@ns_conf.param('name', 'Datasource name')
class Analyze2(Resource):
    @ns_conf.doc('analyze_refresh_dataset')
    def get(self, name):
        analysis = request.default_store.get_analysis(name)
        if analysis is not None:
            return analysis, 200

        ds = request.default_store.get_datasource(name)
        if ds is None:
            log.error('No valid datasource given')
            abort(400, 'No valid datasource given')

        x = threading.Thread(target=analyzing_thread, args=(name, request.default_store))
        x.start()
        return {'status': 'analyzing'}, 200


@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    def get(self, name):
        '''return data rows'''
        ds = request.default_store.get_datasource(name)
        if ds is None:
            abort(400, 'No valid datasource given')

        params = {
            'page[size]': None,
            'page[offset]': None
        }
        where = []
        for key, value in request.args.items():
            if key == 'page[size]':
                params['page[size]'] = int(value)
            if key == 'page[offset]':
                params['page[offset]'] = int(value)
            elif key.startswith('filter'):
                param = parse_filter(key, value)
                if param is None:
                    abort(400, f'Not valid filter "{key}"')
                where.append(param)

        data_dict = request.default_store.get_data(name, where, params['page[size]'], params['page[offset]'])

        return data_dict, 200


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFilesDownload(Resource):
    @ns_conf.doc('get_datasource_download')
    def get(self, name):
        '''download uploaded file'''
        ds = request.default_store.get_datasource(name)
        if not ds:
            abort(404, "{} not found".format(name))
        # force download from s3
        request.default_store.get_datasource_obj(name)
        if not os.path.exists(ds['source']):
            abort(404, "{} not found".format(name))

        return send_file(os.path.abspath(ds['source']), as_attachment=True)
