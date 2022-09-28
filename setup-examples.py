import sys, json, urllib3

def requestToJSON(request):
    return json.loads(request.data.decode('utf-8'))

def encode(data):
    return json.dumps(data).encode('utf-8')

class Repository:
    def __init__(self, name, description, topics, hook):
        self.name = name
        self.description = description
        self.topics = topics
        self.hook = hook
    def toAPIObject(self):
        return {
            'name': self.name,
            'auto_init': True,
            'description': self.description
        }
    def toAPIHook(self):
        return {
            'active': True,
            'type': 'gitea',
            'events': ['push'],
            'config': {
                'url': self.hook,
                'content_type': 'json'
            }
        }

giteaAPI = 'http://infra-gitea-http.default.svc.cluster.local/api/v1'
argoCDHook = 'http://argocd-server.argocd.svc.cluster.local/api/webhook'
mddWebhook = 'http://on-change-webhook-eventsource-svc.mdd.svc.cluster.local/onchange'

headers = urllib3.make_headers(basic_auth='gitea-admin:password')
headers['Content-Type']='application/json'
http = urllib3.PoolManager()

repos = [
    Repository('microservice', 'A metamodel for microservices', ['version-microservice-0', 'instanceof-ecore-0'], mddWebhook),
    Repository('microservice-validator', 'A validator for microservices', ['version-ms-validator-0', 'input-microservice-0'], mddWebhook),
    Repository('microservice-analyzer', 'An analyzer for microservices', ['version-ms-analyzer-0', 'input-microservice-0'], mddWebhook),
    Repository('microservice-simulator', 'A simulator for microservices', ['version-ms-simulator-0', 'input-microservice-0'], mddWebhook),
    Repository('customer-microservice', 'A model for a customer microservice', ['version-customer-ms-0', 'instanceof-microservice-0'], mddWebhook),
    Repository('shopping-cart-microservice', 'A model for a shopping cart microservice', ['version-shopping-cart-ms-0', 'instanceof-microservice-0'], mddWebhook),
    Repository('order-microservice', 'A model for an order microservice', ['version-order-ms-0', 'instanceof-microservice-0'], mddWebhook),
    Repository('microservice-spring-boot', 'A generator for microservices to create Spring Boot applications', ['version-ms-spring-boot-0', 'instanceof-trafomm-0', 'input-microservice-0', 'output-spring-boot-0'], mddWebhook),
    Repository('microservice-dot-net', 'A generator for microservices to create Dot Net applications', ['version-ms-dot-net-0', 'instanceof-trafomm-0', 'input-microservice-0', 'output-dot-net-0'], mddWebhook),
    Repository('microservice-python', 'A generator for microservices to create Python applications', ['version-ms-python-0', 'instanceof-trafomm-0', 'input-microservice-0', 'output-python-0'], mddWebhook),
    Repository('mdd-kubernetes', 'A platform to run mdd jobs on kubernetes', [], argoCDHook)
]

for repo in repos:
    print(f'Setting up repository \'{repo.name}\'')
    request = http.request('POST', f'{giteaAPI}/user/repos', headers=headers, body=encode(repo.toAPIObject()))
    status = request.status
    if status == 201:    
        fullname = (requestToJSON(request))['full_name']
        print(f'Setting up topics for new repository \'{fullname}\'')
        request = http.request('PUT', f'{giteaAPI}/repos/{fullname}/topics', headers=headers, body=encode({'topics': repo.topics}))
        status = request.status
        if status != 204:
            print(f'Error {status}: \'{requestToJSON(request)}\'')
        print(f'Setting up hook for new repository \'{fullname}\'')
        request = http.request('POST', f'{giteaAPI}/repos/{fullname}/hooks', headers=headers, body=encode(repo.toAPIHook()))
        status = request.status
        if status != 201:
            print(f'Error {status}: \'{requestToJSON(request)}\'')
    elif status == 409:
        print(f'Repository \'{repo.name}\' already exists, skipping setup')
    else:
        print(f'Unknow error occured while creating repository \'{repo.name}\', status is {status}, reposonse is \'{requestToJSON(request)}\'')