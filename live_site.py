import os
import json
import click
import requests
import colorama
import digitalocean
from colorama import Fore
from colorama import init
from pssh.clients import SSHClient


if os.getenv('DIGITAL_OCEAN_AUTH_TOKEN'):
	api_token = os.getenv('DIGITAL_OCEAN_AUTH_TOKEN')
else:
	api_token = input ('Enter your API token: ')


if os.getenv('SSH_KEY'):
	ssh_key = os.getenv('SSH_KEY')
else:
	ssh_key = input (' Enter your SSH Key path: ')

# The api_url_base variable is the string that starts off every URL in the DigitalOcean API.
api_url_base = 'https://api.digitalocean.com/v2/'
# We need to set up the HTTP request headers the way the API docs describe.
# Add these lines to the file to set up a dictionary containing your request headers:
headers = {'Content-Type': 'application/json',
		'Authorization': 'Bearer {0}'.format(api_token)}



def get_all_droplets():
	api_url = '{0}droplets'.format(api_url_base)
	response = requests.get(api_url, headers=headers)

	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))
	else:
		return None

def del_droplet(dropletId):

	droplet = digitalocean.Droplet(token=api_token,id=dropletId)

	destroyed = droplet.destroy()
	click.secho(">>> Success! Your droplet has been deleted.", fg='bright_green')
	
def del_domain(domain_name):

	domain = digitalocean.Domain(token=api_token, name=domain_name)

	destroyed = domain.destroy()

	if destroyed == True:
		click.secho(">>> Success! Your domain name '{}' has been deleted.".format(domain_name), fg='bright_green')
	else:   
		click.secho(' [!] Request failed!', fg='bright_red')


def check_droplet(droplet):
	my_droplets = get_all_droplets()
	droplet_exists = ''
	droplet_id: ''
	
	# Checks if the droplet already exists or not
	for each_droplet, details in enumerate(my_droplets['droplets']):
		for key, value in details.items():
			x = details['name']
			if droplet != x: continue
			droplet_exists = x
			return droplet_exists
	else:
		return None

# Deletes all droplets
def del_all_droplets():
	my_droplets = get_all_droplets()

	for each_droplet, details in enumerate(my_droplets['droplets']):
		for key, value in details.items():
			x = details['name']
			dropletId = details['id']
			del_droplet(dropletId)
	else:
		click.secho('All droplets have been deleted!', fg='bright_green')


def create_droplet(droplet):

	droplet = digitalocean.Droplet(token=api_token,
								  name=droplet,
								  region='nyc1',
								  image='ubuntu-20-04-x64',
								  size_slug='s-2vcpu-4gb', 
								  backups=True, 
								  ipv6=False, 
								  ssh_keys=[28355743, 29166498], #white_key & carrot_key
								  user_data='',
								  private_networking='',
								  volumes=[],
								  tags="web")
	droplet.create()
	d = droplet.__str__()      
	click.secho(">>> New droplet has been created with a Droplet ID and Droplet Name: ")
	click.secho(d,  fg='bright_green')      


def get_droplet_id():
	my_droplets = get_all_droplets()

	for each_droplet, details in enumerate(my_droplets['droplets']):
		for key, value in details.items():
			x = details['name']
			dropletId = details['id']
			return dropletId
	else:
		return None		


def get_hostname_ip(droplet):
# This function is to cycle through all the droplets and 
# get the IP Address of the droplet.
# Also checks if the droplet is up, thus returns the IP Address.  
	result = ''
	ip = ''

	click.secho(">>> Inspecting droplets...", fg='bright_yellow')   
	my_droplets = get_all_droplets()	
	
	for each_droplet, details in enumerate(my_droplets['droplets']):
		for key, value in details.items():
			if details['name'] == droplet:
				#click.echo(details['name'])                
				if key == 'networks':
					result = value      
					for key, value in result.items():
						if key == 'v4':
							v4 = value[1]
							ip = v4['ip_address']
							#click.echo(ip)
							return ip
	else:
		click.secho(">>> Your droplet {}' doesn't exist!".format(droplet), fg='bright_red')
		click.secho(">>> We can't add your data at the moment.", fg='bright_red')                     


def get_all_domains():

	api_url = '{0}domains'.format(api_url_base)

	response = requests.get(api_url, headers=headers)

	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))
	else:
		return None


def add_new_domain(domain_name, ip_address):

	api_url = '{0}domains'.format(api_url_base)    

	domain = {'name': domain_name, 'ip_address': ip_address}

	response = requests.post(api_url, headers=headers, json=domain)

	if response.status_code == 201:
		domain = json.loads(response.content)
		return domain
	else:
		click.secho('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content), fg='bright_red')
		return None
			

def check_domain(domain_name):

	my_domains = get_all_domains()
	domain_exists = ''

	# Checks if the domain name already exists or not
	for domain, details in enumerate(my_domains['domains']):
		for key, value in details.items():
			x = details['name']            
			if domain_name != x: continue
			domain_exists = x
			return domain_exists
		else:
			return None	
	else:
		return None


def will_add_domain(droplet, domain_name):
		# IP address is needed to create the domain name, so we call the function get_hostname_ip()
		ip = get_hostname_ip(droplet)
		# Just want to make sure the ip_address is a string, so I convert it anyway.
		ip_address = str(ip)  

		# This adds/creates the domain name
		new_domain = add_new_domain(domain_name, ip_address)

		if new_domain is not None:
			click.secho('>>> Your new domain name {} has been created with IP Address {}. '.format(domain_name, ip_address), fg='bright_green')
		else:
			click.secho('[!] Request Failed', fg='bright_red')


def create_domain(droplet, domain_name):

	domain_exists = check_domain(domain_name)
	click.echo(domain_exists)

	if domain_exists == domain_name:
		click.secho('>>> Your domain name {} already exists!'.format(domain_name), fg='bright_yellow')
		click.secho('>>> We are now removing it to droplet IP mapping ...', fg='bright_yellow')
		del_domain(domain_name)
		click.secho('Creating a new domain name now...', fg='bright_yellow')
		will_add_domain(droplet, domain_name)
	else:
		click.echo('...')
		will_add_domain(droplet, domain_name)


def add_new_domain_record(type, name, data, ttl, domain_name):

	api_url = '{0}domains/{1}/records'.format(api_url_base,domain_name)    

	records = {"type":type,"name":name,"data":data,"ttl":ttl}

	response = requests.post(api_url, headers=headers, json=records) 

	if response.status_code == 201:
		records = json.loads(response.content)
		return records
	else:
		click.secho('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content), fg='bright_red')
		return None                     
		

def add_domain_rec(droplet, domain_name):
	# Get the IP Address associated with jediluke.space
	ip = get_hostname_ip(droplet)
	rec_data = str(ip)

	add_response = add_new_domain_record('A','www',rec_data,1800, domain_name)

	if add_response is not None:
		click.secho('>>> Your A Record has been created... ', fg='bright_green')
		for k, v in add_response.items():
			click.secho('  {0}:{1}'.format(k, v), fg='bright_green')
	else:
		click.secho('[!] Request Failed', fg='bright_red')

def set_nginx(droplet, domain_name):

	host = get_hostname_ip(droplet)

	client = SSHClient(host, user='root', password='', pkey=ssh_key,port=22)
	click.secho('Connecting to your server...', fg='bright_yellow')

	def upload():
	# This funtion will:
	# Upload the initial files and configuration needed in setting up Nginx to the server   

		click.echo('Setting up your configuration block for {}...'.format(domain_name))
		loc_file1 = 'D:/Workbench/Luke/jediluke.space/files/jediluke.space.txt'
		rem_file1 = '/etc/nginx/jediluke.space.txt'
		loc_file2 = 'D:/Workbench/Luke/jediluke.space/files/nginx.conf'
		rem_file2 = '/etc/nginx/nginx.conf'

		upload_1 = client.copy_file(loc_file1, rem_file1)
		upload_2 = client.copy_file(loc_file2, rem_file2)

		cmd = ["sudo mv /etc/nginx/jediluke.space.txt /etc/nginx/sites-available/jediluke.space", "sudo ln -s /etc/nginx/sites-available/jediluke.space /etc/nginx/sites-enabled/", "sudo nginx -t", "sudo systemctl restart nginx"]
		# Cycle through the cmd list and run it on the server
		for command in cmd:
			x = command
			output = client.run_command(x)

	# Cycle through the cmd list and run each command to the server
	# The last command 'upload' will call upload() to upload Nginx config files
	cmd = ["sudo apt-get update", "sudo apt-get -y install nginx", "sudo ufw allow 'Nginx HTTP' ","sudo ufw status", "systemctl status nginx", "sudo mkdir -p /var/www/jediluke.space/html", "sudo chown -R root:root /var/www/jediluke.space/html", "sudo chmod -R 755 /var/www/jediluke.space", "upload"] 

	for command in cmd:
		if command != 'upload':
			x = command
			output = client.run_command(x)
			for line in output.stdout:
				click.echo(line)
			#click.echo(' Completed the command >>>{}<<<'.format(x), ' Exit code: ', output.exit_code)
		else:
			upload()
	else:
		click.secho('>>> Your Nginx setup is complete!', fg='bright_green') 


def upload_temp(droplet):

	host = get_hostname_ip(droplet)

	client = SSHClient(host, user='root', password='', pkey=ssh_key,port=22)

	loc_file = 'D:/Workbench/Luke/jediluke.space/files/index.html'
	rem_file = '/var/www/jediluke.space/html'
	upload = client.copy_file(loc_file, rem_file, recurse=True)

	# Set ownership of the directory
	cmd = ["sudo chown -R root:root /var/www/jediluke.space/html", "sudo chmod -R 755 /var/www/jediluke.space"]

	for command in cmd:
		x = command
		output = client.run_command(x)  

	path = loc_file
	# Scan the directory
	obj = os.scandir(path)
	# List all files and directories 
	# in the specified path that are being uploaded successfully to the server.
	click.secho('>>> File/s that are successfully uploaded to the server: ', fg='bright_yellow')
	for entry in obj :
		if entry.is_dir() or entry.is_file():
			click.secho(' * ', entry.name, fg='bright_green')

	obj.close() 

	click.secho('Waiting for up to 30 seconds for everything to finish...', fg='bright_yellow')

	url = 'http://jediluke.space/index'
	response = requests.get(url)
	# print(response.text)

	if response.status_code == 200:
		click.secho('>>> You can now access your homepage {}! '.format(url), fg='bright_green')      
	else:
		return None


@click.group()
@click.version_option(version='1.0', prog_name='Live')
def main():
	"""
	This tool helps you manage website setup.

	Use help [OPTIONS] to see how to use each command.
	
	Ex. live_site take-down --help
	"""
	pass        

# Commands in this script

@main.command()
@click.option('--url', '-u', default='http://jediluke.space', help='URL of the website.', prompt=True)
# Check status of the website
def status(url):
	"""Checks the status of a website by providing a URL.

		Ex.
		live_site status -u http://jediluke.space
	"""
	init(autoreset=True)
	response =''

	try:    
		response = requests.get(url, timeout=5)
		if response.status_code == 200:
			click.echo(Fore.GREEN + '>>> Your website {} is up and running!]'.format(response.status_code,url))   
		else:
			click.echo(Fore.RED + ' HTTP status code: {} [Your website {} is down!]'.format(response.status_code,url))

	except Exception as e:
		click.echo(Fore.RED + '>>> Your website {} is down! - \n {}'.format(url,str(e)))    



@main.command()
# Takes down all droplets
@click.option('--droplet', '-d', default='jediluke-space', help='Droplet name.')
@click.option('--domain-name', '-dn', default='jediluke.space', help='Domain name to delete as argument.')
def take_down(droplet, domain_name):
	"""Takes down or destroys all droplets. 

	-dn option requires an argument
	
	Ex. live_site take-down

	"""
	droplet_exists = check_droplet(droplet)

	dropletId = get_droplet_id()			

	if droplet_exists == droplet:
		click.secho('>>> Deleting your existing droplet {} ...'.format(droplet), fg='bright_yellow')
		del_droplet(dropletId)
	else:
		click.secho(">>> Your droplet <{}> doesn't exist!.".format(droplet), fg='bright_red')	

	domain_exists = check_domain(domain_name)

	if domain_exists == domain_name:
		click.secho('>>> Domain name {} detected! We are deleting it now ...'.format(domain_name), fg='bright_yellow')
		del_domain(domain_name)
	else:
		click.secho(">>> And your domain name <{}> doesn't exist in your domain's list.".format(domain_name), fg='bright_red')	

 
@main.command()
@click.option('--droplet', '-cd', default='jediluke-space', help='Creates a new droplet by providing a droplet name as parameter.')
@click.option('--domain-name', '-cdn', default='jediluke.space', help='Creates a new domain name by providing a domaim name as parameter.')
def deploy(droplet, domain_name):
	"""Deploys a new blog droplet, from scratch. """

	droplet_exists = check_droplet(droplet)

	# if domain exists, prompt to delete or not...
	if droplet_exists == droplet:
		click.secho('>>> Heads up! Your blog droplet for {} is already up.'.format(droplet), fg='bright_red')
	else:
		click.secho('>>> Creating your new blog droplet. This may take a while to complete...', fg='bright_yellow')        
		create_droplet(droplet)
		click.secho('>>> Creating your new domain {}...'.format(domain_name), fg='bright_yellow')
		create_domain(droplet, domain_name)
		click.secho('>>> Creating a new A record for your domain...', fg='bright_yellow')
		add_domain_rec(droplet, domain_name)
		click.secho('>>>Setting up Nginx on your server...', fg='bright_yellow')
		set_nginx(droplet, domain_name)
		#click.secho('>>>Uploading initial homepage to your server...', fg='bright_yellow')
		#upload_temp(droplet)	


if __name__ == '__main__':
	main()

