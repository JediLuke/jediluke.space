import json
import requests

api_token = 'token'
api_url_base = 'https://api.digitalocean.com/v2/'

headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}


def get_all_droplets():

    api_url = '{0}droplets'.format(api_url_base)

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


my_droplets = get_all_droplets()

if my_droplets is not None:
    print('Your droplets: ')
    for droplet, details in enumerate(my_droplets['droplets']):
        print('Droplet {}:'.format(droplet))
        for k, v in details.items():
            print('  {0}:{1}'.format(k, v))

else:
    print('[!] Request Failed')
