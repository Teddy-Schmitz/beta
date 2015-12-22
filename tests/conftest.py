import pytest
from botocore.exceptions import ClientError
from beta import Beta
import tempfile
import shutil
import os
import json
from datetime import datetime

test_config = {
        "name": "test-gateway",
        "description": "Test 123",
        "models": [
            {
                "name": "test-model",
                "description": "",
                "schema": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "PetsLambdaModel",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "string"
                            },
                            "price": {
                                "type": "number"
                            }
                        }
                    }
                },
                "contentType": "application/json"
            }
        ],
        "resources": [
            {
                "parentPath": "/",
                "pathPart": "",
                "methods": [
                    {
                        "httpMethod": "GET",
                        "authorizationType": "None",
                        "apiKeyRequired": "false",
                        "requestModels": {
                            "application/json": "test"
                        },
                        "methodResponse": [
                            {
                                "statusCode": "200",
                                "responseParameters": {
                                    "method.response.header.Access-Control-Allow-Origin": False
                                },
                                "responseModels": {
                                    "application/json": "Empty"
                                }
                            }
                        ]
                    }
                ],
                "integrations": [
                    {
                        "httpMethod": "GET",
                        "type": "AWS",
                        "uri": "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-1:fakearn:function:testing/invocations",
                        "integrationHttpMethod": "POST",
                        "integrationResponse": [
                            {
                                "statusCode": "200",
                                "responseParameters": {
                                    "method.response.header.Access-Control-Allow-Origin": "'*'"
                                },
                                "responseTemplates": {
                                    "application/json": "Empty"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.yield_fixture(scope='session')
def beta():
    yield Beta()


@pytest.yield_fixture()
def create_file_structure_src():
    tempdir = tempfile.mkdtemp(prefix='beta_test')
    os.makedirs(os.path.join(tempdir, 'test-gateway'))
    os.makedirs(os.path.join(tempdir, 'test-gateway', 'src'))
    with open(os.path.join(tempdir, 'test-gateway', 'gateway.json'), 'w') as f:
        f.writelines(json.dumps(test_config))

    yield tempdir

    shutil.rmtree(tempdir)

@pytest.yield_fixture()
def remove_network_beta(beta, monkeypatch, mocker):
    rest_apis = {
        'position': '1',
        'items': [
            {
                'id': '12345',
                'name': 'test2',
                'createdDate': datetime(2015, 1, 1)
            },
        ]
    }
    create_return = {
        'id': '56789',
        'name': 'test',
        'description': 'blah',
        'createdDate': datetime(2015, 11, 1)
    }

    get_resources = {
        'position': '1',
        'items': [
            {
                'id': 'asdf43',
                'path': '/',
                'resourceMethods': {
                    'string': {
                        'httpMethod': 'POST',
                        'authorizationType': 'string',
                        'apiKeyRequired': False,
                        'methodResponses': {
                            'string': {
                                'statusCode': 'string',
                                'responseParameters': {
                                    'application/json': True
                                }
                            }
                        },
                        'methodIntegration': {
                            'type': 'HTTP',
                            'httpMethod': 'GET',
                            'uri': 'https://example.com',
                            'requestTemplates': {
                                'application/json': 'model'
                            },
                            'integrationResponses': {
                                'string': {
                                    'statusCode': '200'
                                }
                            }
                        }
                    }
                }
            },
        ]
    }

    create_resource = {
        'id': 'jkl123',
        'parentId': 'asdf43',
        'pathPart': 'test',
        'path': '/test'
    }

    mock_aws = mocker.Mock()
    mock_aws.get_rest_apis.return_value = rest_apis
    mock_aws.create_rest_api.return_value = create_return
    mock_aws.get_resources.return_value = get_resources
    mock_aws.delete_resource.return_value = None
    mock_aws.delete_resource.side_effect = ClientError({'Error':
                                                        {'Code': 'ClientException',
                                                         'Message': 'Root resource cannot be deleted'}}, 'DeleteResource')
    mock_aws.delete_method.return_value = None
    mock_aws.create_model.return_value = None
    mock_aws.delete_model.return_value = None
    mock_aws.create_resource.return_value = create_resource
    mock_aws.put_method.return_value = None
    mock_aws.put_method_response.return_value = None
    mock_aws.put_integration.return_value = None
    mock_aws.put_integration_response.return_value = None

    mocker.patch.object(beta, 'apigw', new=mock_aws)

    yield beta
