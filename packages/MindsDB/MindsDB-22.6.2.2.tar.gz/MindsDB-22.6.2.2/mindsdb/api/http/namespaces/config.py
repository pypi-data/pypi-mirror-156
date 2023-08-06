import copy
import datetime
from dateutil.parser import parse as parse_datetime
import subprocess
import os
import sys
import tempfile
import shutil
from pathlib import Path

from flask import request
from flask_restx import Resource, abort
from flask import current_app as ca
from dateutil.tz import tzlocal

from mindsdb.utilities.log import log
from mindsdb.api.http.namespaces.configs.config import ns_conf
from mindsdb.utilities.log import get_logs
from mindsdb.integrations import CHECKERS
from mindsdb.api.http.utils import http_error
from mindsdb.interfaces.stream.stream import StreamController


@ns_conf.route('/logs')
@ns_conf.param('name', 'Get logs')
class GetLogs(Resource):
    @ns_conf.doc('get_integrations')
    def get(self):
        min_timestamp = parse_datetime(request.args['min_timestamp'])
        max_timestamp = request.args.get('max_timestamp', None)
        context = request.args.get('context', None)
        level = request.args.get('level', None)
        log_from = request.args.get('log_from', None)
        limit = request.args.get('limit', None)

        logs = get_logs(min_timestamp, max_timestamp, context, level, log_from, limit)
        return {'data': logs}


@ns_conf.route('/integrations')
@ns_conf.param('name', 'List all database integration')
class ListIntegration(Resource):
    def get(self):
        return {
            'integrations': [k for k in request.integration_controller.get_all(sensitive_info=False)]
        }


@ns_conf.route('/all_integrations')
@ns_conf.param('name', 'List all database integration')
class AllIntegration(Resource):
    @ns_conf.doc('get_all_integrations')
    def get(self):
        integrations = request.integration_controller.get_all(sensitive_info=False)
        return integrations


@ns_conf.route('/integrations/<name>')
@ns_conf.param('name', 'Database integration')
class Integration(Resource):
    @ns_conf.doc('get_integration')
    def get(self, name):
        integration = request.integration_controller.get(name, sensitive_info=False)
        if integration is None:
            abort(404, f'Can\'t find database integration: {name}')
        integration = copy.deepcopy(integration)
        return integration

    @ns_conf.doc('put_integration')
    def put(self, name):
        params = {}
        params.update((request.json or {}).get('params', {}))
        params.update(request.form or {})

        if len(params) == 0:
            abort(400, "type of 'params' must be dict")

        # params from FormData will be as text
        for key in ('publish', 'test', 'enabled'):
            if key in params:
                if isinstance(params[key], str) and params[key].lower() in ('false', '0'):
                    params[key] = False
                else:
                    params[key] = bool(params[key])

        files = request.files
        temp_dir = None
        if files is not None:
            temp_dir = tempfile.mkdtemp(prefix='integration_files_')
            for key, file in files.items():
                temp_dir_path = Path(temp_dir)
                file_name = Path(file.filename)
                file_path = temp_dir_path.joinpath(file_name).resolve()
                if temp_dir_path not in file_path.parents:
                    raise Exception(f'Can not save file at path: {file_path}')
                file.save(file_path)
                params[key] = file_path

        is_test = params.get('test', False)
        if is_test:
            del params['test']
            db_type = params.get('type')
            checker_class = CHECKERS.get(db_type, None)
            if checker_class is None:
                abort(400, f"Unknown integration type: {db_type}")
            checker = checker_class(**params)
            if temp_dir is not None:
                shutil.rmtree(temp_dir)
            return {'success': checker.check_connection()}, 200

        integration = request.integration_controller.get(name, sensitive_info=False)
        if integration is not None:
            abort(400, f"Integration with name '{name}' already exists")

        try:
            if 'enabled' in params:
                params['publish'] = params['enabled']
                del params['enabled']
            request.integration_controller.add(name, params)

            model_data_arr = []
            for model in request.model_interface.get_models():
                if model['status'] == 'complete':
                    try:
                        model_data_arr.append(request.model_interface.get_model_data(model['name']))
                    except Exception:
                        pass

            if is_test is False and params.get('publish', False) is True:
                model_data_arr = []
                for model in request.model_interface.get_models():
                    if model['status'] == 'complete':
                        try:
                            model_data_arr.append(request.model_interface.get_model_data(model['name']))
                        except Exception:
                            pass

                stream_controller = StreamController(request.company_id)
                if params.get('type') in stream_controller.known_dbs and params.get('publish', False) is True:
                    stream_controller.setup(name)
        except Exception as e:
            log.error(str(e))
            if temp_dir is not None:
                shutil.rmtree(temp_dir)
            abort(500, f'Error during config update: {str(e)}')

        if temp_dir is not None:
            shutil.rmtree(temp_dir)
        return '', 200

    @ns_conf.doc('delete_integration')
    def delete(self, name):
        integration = request.integration_controller.get(name)
        if integration is None:
            abort(400, f"Nothing to delete. '{name}' not exists.")
        try:
            request.integration_controller.delete(name)
        except Exception as e:
            log.error(str(e))
            abort(500, f'Error during integration delete: {str(e)}')
        return '', 200

    @ns_conf.doc('modify_integration')
    def post(self, name):
        params = {}
        params.update((request.json or {}).get('params', {}))
        params.update(request.form or {})

        if not isinstance(params, dict):
            abort(400, "type of 'params' must be dict")
        integration = request.integration_controller.get(name)
        if integration is None:
            abort(400, f"Nothin to modify. '{name}' not exists.")
        try:
            if 'enabled' in params:
                params['publish'] = params['enabled']
                del params['enabled']
            request.integration_controller.modify(name, params)

            stream_controller = StreamController(request.company_id)
            if params.get('type') in stream_controller.known_dbs and params.get('publish', False) is True:
                stream_controller.setup(name)
        except Exception as e:
            log.error(str(e))
            abort(500, f'Error during integration modifycation: {str(e)}')
        return '', 200


@ns_conf.route('/integrations/<name>/check')
@ns_conf.param('name', 'Database integration checks')
class Check(Resource):
    @ns_conf.doc('check')
    def get(self, name):
        if request.integration_controller.get(name) is None:
            abort(404, f'Can\'t find database integration: {name}')
        connections = request.integration_controller.check_connections()
        return connections.get(name, False), 200


@ns_conf.route('/vars')
class Vars(Resource):
    def get(self):
        if os.getenv('CHECK_FOR_UPDATES', '1').lower() in ['0', 'false']:
            telemtry = False
        else:
            telemtry = True

        if ca.config_obj.get('disable_mongo', False):
            mongo = False
        else:
            mongo = True

        cloud = ca.config_obj.get('cloud', False)
        local_time = datetime.datetime.now(tzlocal())
        local_timezone = local_time.tzname()

        return {
            'mongo': mongo,
            'telemtry': telemtry,
            'cloud': cloud,
            'timezone': local_timezone,
        }


@ns_conf.route('/install_options')
@ns_conf.param('dependency_list', 'Install dependencies')
class InstallDependenciesList(Resource):
    def get(self):
        return {'dependencies': ['snowflake', 'athena', 'google', 's3', 'lightgbm_gpu', 'mssql', 'cassandra', 'scylladb']}


@ns_conf.route('/install/<dependency>')
@ns_conf.param('dependency', 'Install dependencies')
class InstallDependencies(Resource):
    def get(self, dependency):
        if dependency == 'snowflake':
            dependency = ['snowflake-connector-python[pandas]', 'asn1crypto==1.3.0']
        elif dependency == 'athena':
            dependency = ['PyAthena >= 2.0.0']
        elif dependency == 'google':
            dependency = ['google-cloud-storage', 'google-auth']
        elif dependency == 's3':
            dependency = ['boto3 >= 1.9.0']
        elif dependency == 'lightgbm_gpu':
            dependency = ['lightgbm', '--install-option=--gpu', '--upgrade']
        elif dependency == 'mssql':
            dependency = ['pymssql >= 2.1.4']
        elif dependency == 'cassandra':
            dependency = ['cassandra-driver']
        elif dependency == 'scylladb':
            dependency = ['scylla-driver']
        else:
            return f'Unkown dependency: {dependency}', 400

        outs = b''
        errs = b''
        try:
            sp = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install', *dependency],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            code = sp.wait()
            outs, errs = sp.communicate(timeout=1)
        except Exception as e:
            return http_error(500, 'Failed to install dependency', str(e))

        if code != 0:
            output = ''
            if isinstance(outs, bytes) and len(outs) > 0:
                output = output + 'Output: ' + outs.decode()
            if isinstance(errs, bytes) and len(errs) > 0:
                if len(output) > 0:
                    output = output + '\n'
                output = output + 'Errors: ' + errs.decode()
            return http_error(500, 'Failed to install dependency', output)

        return 'Installed', 200
