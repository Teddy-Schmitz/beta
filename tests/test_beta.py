from conftest import test_config


def test_enumerate_modules(remove_network_beta, create_file_structure_src, monkeypatch):
    beta = remove_network_beta
    for path, config in beta.enumerate_modules(create_file_structure_src):
        assert config == test_config


def test_push_all_new(remove_network_beta, create_file_structure_src):
    beta = remove_network_beta
    beta.push_all(create_file_structure_src)

    assert beta.apigw.get_rest_apis.call_count == 1
    assert beta.apigw.create_rest_api.call_count >= 1
    assert beta.apigw.delete_method.call_count == 7
    assert beta.apigw.create_model.call_count == 1
    assert beta.apigw.put_method.call_count == 1
    assert beta.apigw.put_method_response.call_count == 1
    assert beta.apigw.put_integration.call_count == 1
    assert beta.apigw.put_integration_response.call_count == 1

