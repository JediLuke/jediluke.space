import os
import click
import requests
import colorama
import digitalocean
from colorama import Fore
from colorama import init


@click.command()
@click.option('--status',default='http://jediluke.space',help='Check the status of your website.')
@click.option('--take-down',default='jediluke-space',help='Deletes the droplet and remove the jediluke.space domain to droplet IP mapping.')
def live(status, take_down):
    init(autoreset=True)
    response =''

    try:    
        response = requests.get(status, timeout=5)
    except Exception as e:
        click.echo(Fore.RED + ' Your website {} is down! - \n {}'.format(status,str(e)))    
    else:
        if response.status_code == 200:
            click.echo(Fore.GREEN + ' HTTP status code: {} [Your website {} is up and running!]'.format(response.status_code,status))   
        else:
            click.echo(Fore.RED + ' HTTP status code: {} [Your website {} is down!]'.format(response.status_code,status))

    domain_name = 'jediluke.space'
    droplet_name = 'jediluke-space'
    api_token = ''

    api_url_base = 'https://api.digitalocean.com/v2/'

    headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(api_token)}

    if os.getenv('DIGITAL_OCEAN_AUTH_TOKEN'):
        api_token = os.getenv('DIGITAL_OCEAN_AUTH_TOKEN')
    else:
        api_token = input ('Enter your API token: ')

    def destroy(take_down):            

        def get_all_droplets(api_url_base, headers):
            api_url = '{0}droplets'.format(api_url_base)
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                return None


        def del_droplet(api_token, droplet_id):
            droplet = digitalocean.Droplet(token=api_token,
                id=droplet_id)

            destroyed = droplet.destroy()
            if destroyed == True:
                click.echo(" Success! Your droplet with a '{}' ID has been deleted.".format(droplet_id))
            else:
                click.echo(' [!] Request failed!')

        def del_domain(domain_name):    
            domain = digitalocean.Domain(token=api_token, name=domain_name)

            domain.destroy()

            click.echo(" Success! '{}' has been deleted.".format(domain_name))      

        def check_droplet(api_url_base, headers):
            my_droplets = get_all_droplets(api_url_base, headers)
            droplet_exists = ''
            droplet_id: ''

            if my_droplets is not None:
             # check if the droplet already exists or not
                #print(' Your droplets: ')
                for droplet, details in enumerate(my_droplets['droplets']):
                    #print('  * Droplet name: ',details['name'])
                    for key, value in details.items():
                        x = details['name']
                        if droplet_name != x: continue
                        click.echo('Droplet already exists!')
                        droplet_exists = x

            # if domain exists, prompt to delete or not...
            if droplet_exists == 'jediluke-space':
                droplet_id = details['id']
                #print('  * Droplet ID: ', droplet_id)
                click.echo('>> Deleting your droplet {}... '.format(droplet_name))
                del_droplet(api_token, droplet_id)
                del_domain(domain_name)                                     

        
if __name__ == "__main__":       
    live()
