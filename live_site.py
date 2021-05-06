import click
import requests
import colorama
from colorama import Fore
from colorama import init

@click.command()
@click.option('--status',default='http://jediluke.space',help='Check the status of your website.')


def live(status):
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

if __name__ == '__main__':
    live()
