from datetime import datetime

from conftest import test_config


def test_enumerate_modules(beta, mock_aws, mocker, create_file_structure_src):
    mocker.patch.object(beta, 'apigw', new=mock_aws)
    beta.push_all(create_file_structure_src)
    for path, config in beta.enumerate_modules(create_file_structure_src):
        assert config == test_config


def test_push_all_new(beta, mock_aws, mocker, create_file_structure_src):
    mocker.patch.object(beta, 'apigw', new=mock_aws)
    beta.push_all(create_file_structure_src)

    assert beta.apigw.get_rest_apis.call_count == 1
    assert beta.apigw.create_rest_api.call_count == 1
    assert beta.apigw.delete_method.call_count == 7
    assert beta.apigw.create_model.call_count == 1
    assert beta.apigw.put_method.call_count == 1
    assert beta.apigw.put_method_response.call_count == 1
    assert beta.apigw.put_integration.call_count == 1
    assert beta.apigw.put_integration_response.call_count == 1

def test_push_all_existing(beta, mock_aws, create_file_structure_src, mocker):
    rest_apis = {
        'position': '1',
        'items': [
            {
                'id': '12345',
                'name': 'test-gateway',
                'createdDate': datetime(2015, 1, 1)
            },
        ]
    }
    mock_aws.get_rest_apis.return_value = rest_apis

    mocker.patch.object(beta, 'apigw', new=mock_aws)
    beta.push_all(create_file_structure_src)

    assert beta.apigw.get_rest_apis.call_count == 1
    assert beta.apigw.create_rest_api.call_count == 1
    assert beta.apigw.delete_method.call_count == 7
    assert beta.apigw.create_model.call_count == 1
    assert beta.apigw.put_method.call_count == 1
    assert beta.apigw.put_method_response.call_count == 1
    assert beta.apigw.put_integration.call_count == 1
    assert beta.apigw.put_integration_response.call_count == 1

