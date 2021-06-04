import os
import json
import time
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


api_url_base = 'https://api.digitalocean.com/v2/'

headers = {'Content-Type': 'application/json',
    'Authorization': 'Bearer {0}'.format(api_token)}


if os.getenv('SSH_KEY'):
    ssh_key = os.getenv('SSH_KEY')
else:
    ssh_key = input (' Enter your SSH Key path: ')   


def get_all_droplets():
    api_url = '{0}droplets'.format(api_url_base)
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


def does_droplet_exists(droplet):
    my_droplets = get_all_droplets()
    droplet_exists = ''
    
    # Checks if the droplet already exists or not
    for each_droplet, details in enumerate(my_droplets['droplets']):
        for key, value in details.items():
            x = details['name']
            if droplet != x: continue
            droplet_exists = x
            return True


def create_droplet(droplet):

    this_droplet_exists = does_droplet_exists(droplet)

    if this_droplet_exists:
        raise RuntimeError('>>> [!] Droplet {} already exists.'.format(droplet))
    else:
        click.secho('>>> Please wait until we finished creating your droplet ...', fg='bright_yellow')
        new_droplet = digitalocean.Droplet(token=api_token,
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

        new_droplet.create()
        time.sleep(15)        

        droplet_created = does_droplet_exists(droplet)

        if droplet_created:
            click.secho(">>> Droplet created sucessfully! ", fg='bright_green')
            d = new_droplet.__str__()
            click.secho(d,  fg='bright_green')
        else:
            raise RuntimeError('[!] Failed to create your droplet.')    



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
        click.secho(">>> [!] Request failed.", fg='bright_red')
        raise RuntimeError(">>> Your droplet {}' doesn't exist!".format(droplet))        


def del_droplet(dropletId):

    droplet = digitalocean.Droplet(token=api_token,id=dropletId)

    destroyed = droplet.destroy()
    click.secho(">>> Your droplet deleted successfully!", fg='bright_green')


def get_all_domains():

    api_url = '{0}domains'.format(api_url_base)

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

    
def del_domain(domain):

    domain = digitalocean.Domain(token=api_token, name=domain)

    destroyed = domain.destroy()
    
    return destroyed


def does_domain_exists(domain):
    my_domains = get_all_domains()
    domain_exists = ''

    for each_domain, details in enumerate(my_domains['domains']):
        for key, value in details.items():
            x = details['name']            
            if domain != x: continue
            domain_exists = x
            return True


def add_new_domain(droplet, domain):

    ip = get_hostname_ip(droplet)

    ip_address = str(ip)

    api_url = '{0}domains'.format(api_url_base)    

    domain = {'name': domain, 'ip_address': ip_address}

    response = requests.post(api_url, headers=headers, json=domain)

    time.sleep(5)

    if response.status_code == 201:
        created_domain = json.loads(response.content)        
        click.secho(">>> Domain name {} created successfully! Your domain's IP Address is {}.".format(domain, ip_address), fg='bright_green')        
        return created_domain
    else:
        raise RuntimeError('>>> [?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None
        

def create_domain(droplet, domain):

    click.secho('>>> Creating your domain name. Please wait ...', fg='bright_yellow')    

    this_domain_exists = does_domain_exists(domain)    

    if this_domain_exists:
        click.secho('>>> Domain name {} already exists!'.format(domain), fg='bright_red')
        click.secho('>>> Deleting and removing it to droplet IP mapping ...', fg='bright_yellow')
        
        destroyed = del_domain(domain)

        if destroyed:
            click.secho('>>> Domain name {} successfully deleted and removed from droplet IP mapping!'.format(domain), fg='bright_green')
            click.secho(">>> We'll now creating a new domain name {} ...".format(domain), fg='bright_yellow')
            add_new_domain(droplet, domain)            
        else:
            raise RuntimeError('>>> [!] Failed to delete the domain name.')
    else:
        add_new_domain(droplet, domain)



def add_domain_rec(droplet, domain):

    the_domain_exists = does_domain_exists(domain)

    if the_domain_exists:
        ip = get_hostname_ip(droplet)
        rec_data = str(ip)

        api_url = '{0}domains/{1}/records'.format(api_url_base,domain)    

        records = {"type":"A","name":"www","data":rec_data,"ttl":1800}

        response = requests.post(api_url, headers=headers, json=records)

        if response.status_code == 201:
            records = json.loads(response.content)
            click.secho('>>> Your A Record added successfully!', fg='bright_green')            
            return records
        else:
            raise RuntimeError('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
            return None
    else:
        click.secho('>>> [!] Failed adding your A record.', fg='bright_red')
        raise RuntimeError(">>> [!] Your domain name {} doesn't exists.".format(domain))


def set_nginx(droplet, domain):
    host = get_hostname_ip(droplet)

    client = SSHClient(host, user='root', password='', pkey=ssh_key,port=22)
    click.secho('Connecting to your server...', fg='bright_yellow')


    def upload():
    # This funtion will:
    # Upload the initial files and configuration needed in setting up Nginx to the server 


        def cmd_run(cmd):
            for command in cmd:
                x = command
                output = client.run_command(x)  

        click.echo('Setting up your configuration block for {}...'.format(domain))
        loc_file1 = './files/jediluke.space.txt'
        rem_file1 = '/etc/nginx/jediluke.space.txt'
        loc_file2 = './files/nginx.conf'
        rem_file2 = '/etc/nginx/nginx.conf'

        upload_1 = client.copy_file(loc_file1, rem_file1)
        time.sleep(5)
        upload_2 = client.copy_file(loc_file2, rem_file2)
        time.sleep(5)

        cmd = ["sudo mv /etc/nginx/jediluke.space.txt /etc/nginx/sites-available/jediluke.space", 
        "sudo ln -s /etc/nginx/sites-available/jediluke.space /etc/nginx/sites-enabled/", 
        "sudo nginx -t", 
        "sudo systemctl restart nginx"
        ]

        # Cycle through the cmd list and run it on the server
        cmd_run(cmd)

    time.sleep(3)
    # Cycle through the cmd list and run each command to the server
    # The last command 'upload' will call upload() to upload Nginx config files
    cmd = ["sudo apt-get update", 
    "sudo apt-get -y install nginx", 
    "sudo ufw allow 'Nginx HTTP' ",
    "sudo ufw status", 
    "systemctl status nginx", 
    "sudo mkdir -p /var/www/jediluke.space/html", 
    "sudo chown -R root:root /var/www/jediluke.space/html", 
    "sudo chmod -R 755 /var/www/jediluke.space", 
    "upload"
    ] 

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

        loc_file = 'D:/Workbench/Luke/jediluke.space/files/index.html'
        rem_file = '/var/www/jediluke.space/html'
        upload = client.copy_file(loc_file, rem_file, recurse=True)

        # Set ownership of the directory
        cmd = ["sudo chown -R root:root /var/www/jediluke.space/html", 
        "sudo chmod -R 755 /var/www/jediluke.space"
        ]

        cmd_run(cmd)

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


    upload_temp()
    time.sleep(30)
        
    url = 'http://jediluke.space/index'
    response = requests.get(url)        

    if response.status_code == 200:
        click.secho('>>> You can now access your homepage at {}! '.format(url), fg='bright_green')
        click.echo(response.text)      
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
@click.option('--droplet', '-d', default='jediluke-space', help='Creates a new droplet by providing a droplet name as parameter.')
@click.option('--domain', '-dn', default='jediluke.space', help='Creates a new domain name by providing a domaim name as parameter.')
def deploy(droplet, domain):
    """Deploys a new blog droplet, from scratch. """

    create_droplet(droplet)
    create_domain(droplet, domain)
    add_domain_rec(droplet, domain)
    set_nginx(droplet, domain)


if __name__ == '__main__':
    main()