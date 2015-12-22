#!/usr/bin/env python
import os
import boto3
import json
import time
from botocore.exceptions import ClientError


class Beta(object):

    def __init__(self):
        self.apigw = boto3.client('apigateway')

    @staticmethod
    def enumerate_modules(project_path):
        for dirname in os.listdir(project_path):
            try:
                with open(os.path.join(project_path, dirname, 'gateway.json')) as lbd_config_file:
                    yield os.path.join(project_path, dirname), json.load(lbd_config_file)
            except IOError:
                #print ('Skipping {0}, failed to open lambda.json'.format(dirname)
                pass
            except ValueError:
                print ('Could not read json from {0}'.format(lbd_config_file))

    @staticmethod
    def check_config(gw_config):
        required_fields = {'name'}
        if required_fields.issubset(gw_config.keys()):
            return True
        print('Skipping {0}, you do not have all required field in your '
              'configuration.'.format(gw_config['name']))
        return False

    def push_single(self, module_path):
        try:
            with open(os.path.join(module_path, 'gateway.json')) as lbd_config_file:
                gw_config = json.load(lbd_config_file)
            if self.check_config(gw_config):
                if 'region' in gw_config.keys():
                    self.apigw = boto3.client('apigateway', region_name=gw_config['region'])
                self.create_gateway(gw_config)
        except IOError:
            print ('Skipping {0}, failed to open gateway.json'.format(module_path))
            pass
        except ValueError:
            print ('Could not read json from {0}/gateway.json'.format(module_path))

    def push_all(self, project_path):
        for module_path, module_config in self.enumerate_modules(project_path):
            if self.check_config(module_config):
                if 'region' in module_config.keys():
                    self.apigw = boto3.client('apigateway', region_name=module_config['region'])
                self.create_gateway(module_config)

    def create_gateway(self, gw_config):
        existing_gw = self.apigw.get_rest_apis(limit=500)

        restapi_id = next((api['id'] for api in existing_gw['items'] if api['name'] == gw_config['name']), None)

        #Backup existing api gateway
        if not restapi_id:
            restapi_id = self.apigw.create_rest_api(name=gw_config['name'],
                                                    description=gw_config.get('description'))['id']
        else:
            backup_id = self.apigw.create_rest_api(name='{0}-{1}'.format(gw_config['name'], time.time()),
                                                   cloneFrom=restapi_id)['id']

        resources = self.apigw.get_resources(restApiId=restapi_id, limit=500).get('items')

        #Cleanup old resources
        for resource in resources:
            try:
                self.apigw.delete_resource(restApiId=restapi_id, resourceId=resource['id'])
            except ClientError as e:
                if 'Root resource cannot be deleted' in e.message:
                    for method in ['GET', 'POST', 'DELETE', 'HEAD', 'OPTIONS',  'PATCH', 'PUT']:
                        try:
                            self.apigw.delete_method(restApiId=restapi_id, resourceId=resource['id'], httpMethod=method)
                        except ClientError:
                            pass

        for model in gw_config['models']:
            try:
                self.apigw.create_model(restApiId=restapi_id, name=model['name'], description=model.get('name'),
                                        schema=json.dumps(model['schema']), contentType=model['contentType'])
            except ClientError as e:
                if 'ConflictException' in e.message:
                    self.apigw.delete_model(restApiId=restapi_id, modelName=model['name'])
                    self.apigw.create_model(restApiId=restapi_id, name=model['name'], description=model.get('name'),
                                            schema=json.dumps(model['schema']), contentType=model['contentType'])
                else:
                    raise

        for resource in gw_config['resources']:
            parent_path = resource['parentPath']
            path_part = resource['pathPart']

            parent_id = next((x['id'] for x in resources if x['path'] == parent_path))

            if not parent_path == '/' and not path_part:
                resource_id = self.apigw.create_resource(restApiId=restapi_id,
                                                         parentId=parent_id, path_part=path_part)['id']
            else:
                resource_id = parent_id

            for method in resource['methods']:
                self.apigw.put_method(restApiId=restapi_id, resourceId=resource_id, httpMethod=method['httpMethod'],
                                      authorizationType=method['authorizationType'],
                                      apiKeyRequired=method.get('apiKeyRequired'),
                                      requestParameters=method.get('requestParameters', {}),
                                      requestModels=method['requestModels'])
                for response in method['methodResponse']:
                    self.apigw.put_method_response(restApiId=restapi_id, resourceId=resource_id,
                                                   httpMethod=method['httpMethod'],
                                                   statusCode=response['statusCode'],
                                                   responseParameters=response['responseParameters'],
                                                   responseModels=response['responseModels'])

            for integration in resource['integrations']:
                self.apigw.put_integration(restApiId=restapi_id, resourceId=resource_id,
                                           httpMethod=integration['httpMethod'],
                                           type=integration['type'], uri=integration['uri'],
                                           integrationHttpMethod=integration['integrationHttpMethod'])

                for response in integration['integrationResponse']:
                    self.apigw.put_integration_response(restApiId=restapi_id, resourceId=resource_id,
                                                        httpMethod=integration['httpMethod'],
                                                        statusCode=response['statusCode'],
                                                        responseParameters=response['responseParameters'],
                                                        responseTemplates=response['responseTemplates'])
