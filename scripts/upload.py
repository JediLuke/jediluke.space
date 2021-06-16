import paramiko

ssh = paramiko.SSHClient()

ssh.load_system_host_keys()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname='hostname',username='username',password='',key_filename='C:/Users/M/.ssh/carrot_key',port='22')

sftp_client=ssh.open_sftp()


local_path = input('Enter local path: ')

sftp_client.chdir("/var/www/beauregardtech.academy/html")

remote_path = input('Enter remote path: ')

sftp_client.put(local_path,remote_path)

stdin, stdout, stderr = ssh.exec_command("cd /var/www/beauregardtech.academy/html && ls")
print (stdout.readlines())

sftp_client.close()

ssh.close()