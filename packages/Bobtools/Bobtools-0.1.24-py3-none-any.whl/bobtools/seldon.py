
from kubernetes import client, config
import yaml

config.load_incluster_config()
v1 = client.CoreV1Api()
custom_object_api = client.CustomObjectsApi()

def get_triton_deploy_template(name, modelUri=None, replicas = 1):
    if (modelUri == None): modelUri = "s3://models/{0}".format(name)
    template = {'apiVersion': 'machinelearning.seldon.io/v1',
                 'kind': 'SeldonDeployment',
                 'metadata': {'name': name},
                 'spec': {'predictors': [{'graph': {'implementation': 'TRITON_SERVER',
                     'logger': {'mode': 'all'},
                     'modelUri': modelUri,
                     'envSecretRefName': 'seldon-init-container-secret',
                     'name': name,
                     'type': 'MODEL'},
                    'name': 'default',
                    'replicas': replicas}],
                  'protocol': 'kfserving'}}
    return template

def deployment_exists(name, namespace = 'seldon'):
    try:
        resource = custom_object_api.get_namespaced_custom_object(name=name, namespace=namespace,
            group="machinelearning.seldon.io", version="v1", plural="seldondeployments")
        return True
    except:
        return False

def undeploy(name, namespace = 'seldon'):
    try:
        resource = custom_object_api.delete_namespaced_custom_object(name=name, namespace=namespace,
            group="machinelearning.seldon.io", version="v1", plural="seldondeployments",
        body=client.V1DeleteOptions())
        return resource
    except:
        pass

def deploy(name, namespace='seldon', modelUri=None, replicas = 1):
    deploy_template = get_triton_deploy_template(name, modelUri, replicas)
    if deployment_exists(name): undeploy(name)

    response = custom_object_api.create_namespaced_custom_object(namespace=namespace,
        group="machinelearning.seldon.io", version="v1", plural="seldondeployments",
        body=deploy_template)
    return response
