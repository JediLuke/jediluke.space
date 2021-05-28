import os
import json
import click
import requests
import colorama
import digitalocean
from colorama import Fore
from colorama import init

if os.getenv('DIGITAL_OCEAN_AUTH_TOKEN'):
	api_token = os.getenv('DIGITAL_OCEAN_AUTH_TOKEN')
else:
	api_token = input ('Enter your API token: ')
#The api_url_base variable is the string that starts off every URL in the DigitalOcean API.
api_url_base = 'https://api.digitalocean.com/v2/'
#We need to set up the HTTP request headers the way the API docs describe.
#Add these lines to the file to set up a dictionary containing your request headers:
headers = {'Content-Type': 'application/json',
		   'Authorization': 'Bearer {0}'.format(api_token)}


def get_all_droplets():
	api_url = '{0}droplets'.format(api_url_base)
	response = requests.get(api_url, headers=headers)

	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))
	else:
		return 

def del_droplet(dropletId):
	droplet = digitalocean.Droplet(token=api_token,id=dropletId)

	destroyed = droplet.destroy()
	click.echo(" Success! Your droplet with an ID '{}' has been deleted.".format(dropletId))
	
def del_domain(domain_name):    
	domain = digitalocean.Domain(token=api_token, name=domain_name)

	destroyed = domain.destroy()

	if destroyed == True:
		click.echo(" Success! Your domain name '{}' has been deleted.".format(domain_name))
	else:   
		click.echo(' [!] Request failed!')

def check_droplet(droplet):
	my_droplets = get_all_droplets()
	droplet_exists = ''
	droplet_id: ''
	
	# check if the droplet already exists or not
	for droplet, details in enumerate(my_droplets['droplets']):
		for key, value in details.items():
			x = details['name']
			droplet_id = details['id']			
			if droplet == x:				
				droplet_exists = x			
				click.echo('Your droplet exists!'.format(droplet_exists))
			return droplet_id
		

@click.group()
@click.version_option(version='1.0', prog_name='Live')
def main():
	"""
	This tool helps you:

	1. Check website status.
	2. Delete a droplet. 
	3. Delete a domain name connected to a droplet.

	Use help [OPTIONS] to see how to use each command.
	Ex. live_site.py take-down --help
	"""
	pass        


@main.command()
@click.option('--url', '-u', default='http://jediluke.space', help='URL of the website.', prompt=True)
#Check status of the website
def status(url):
	"""Check the status of a website by providing a URL.

		Ex.
		live_site.py status -u http://jediluke.space
	"""
	init(autoreset=True)
	response =''

	try:    
		response = requests.get(url, timeout=5)
		if response.status_code == 200:
			click.echo(Fore.GREEN + ' HTTP status code: {} [Your website {} is up and running!]'.format(response.status_code,url))   
		else:
			click.echo(Fore.RED + ' HTTP status code: {} [Your website {} is down!]'.format(response.status_code,url))

	except Exception as e:
		click.echo(Fore.RED + ' Your website {} is down! - \n {}'.format(url,str(e)))    
	

@main.command()
#Take down the droplet
@click.option('--droplet', '-d', default='jediluke-space', help='Droplet name.', prompt=True)
@click.option('--domain-name', '-dn', default='jediluke.space', help='Domain name.', prompt=True)
def take_down(droplet, domain_name):
	"""Take down or destroy a droplet. Provide a droplet name and domanin name attached to the droplet."""

	dropletId = check_droplet(droplet)
	click.echo('>> Deleting your droplet {} with droplet id {}... '.format(droplet, dropletId))
	del_droplet(dropletId)
	click.echo('>> Deleting your domain name {}... '.format(domain_name))
	del_domain(domain_name)


if __name__ == '__main__':
	main()

