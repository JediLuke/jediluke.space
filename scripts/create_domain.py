import json
import requests


api_token = '593abe7a71175fde3d50f516cd73a5bf9c1951f5423c15d9d89109a6846f731b'
api_url_base = 'https://api.digitalocean.com/v2/'
headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}

def add__new_domain(name, ip_address):

    api_url = '{0}domains'.format(api_url_base)    

    domain = {'name': name, 'ip_address': ip_address}

    response = requests.post(api_url, headers=headers, json=domain)


    if response.status_code >= 500:
        print('[!] [{0}] Server Error'.format(response.status_code))
        return None
    elif response.status_code == 404:
        print('[!] [{0}] URL not found: [{1}]'.format(response.status_code,api_url))
        return None
    elif response.status_code == 401:
        print('[!] [{0}] Authentication Failed'.format(response.status_code))
        return None
    elif response.status_code >= 400:
        print('[!] [{0}] Bad Request'.format(response.status_code))
        print(domain )
        print(response.content )
        return None
    elif response.status_code >= 300:
        print('[!] [{0}] Unexpected redirect.'.format(response.status_code))
        return None
    elif response.status_code == 201:
        domain = json.loads(response.content)
        return domain
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None


domain_name = input('Enter domain name: ')
ip = input('Enter IP Address: ')

add_response = add__new_domain(domain_name, ip)

if add_response is not None:
    print('Your new domain was added: ' )
    for k, v in add_response.items():
        print('  {0}:{1}'.format(k, v))
else:
    print('[!] Request Failed')