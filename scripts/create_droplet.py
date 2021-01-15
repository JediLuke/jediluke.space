import digitalocean

droplet = digitalocean.Droplet(token="token",
                               name='jediluke-space',
                               region='sfo2',
                               image='ubuntu-20-04-x64',
                               size_slug='s-1vcpu-1gb', 
                               backups=True, 
                               ipv6=False, 
                               ssh_keys=[28355743],
                               user_data='',
                               private_networking='',
                               volumes=[],
                               tags="web")
droplet.create()



