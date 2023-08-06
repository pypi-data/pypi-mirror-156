from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, AuthenticationException

class SSHAuthentication:
    def __init__(self, client: SSHClient, known_hosts_path: str) -> None:
        self.__client = client

        self.__client.load_host_keys(known_hosts_path)
        self.__client.load_system_host_keys()

        self.__client.set_missing_host_key_policy(AutoAddPolicy())

    def login(self, hostname: str, username: str, password: str) -> None:
        try:
            self.__client.connect(hostname=hostname, username=username, password=password)
        except SSHException:
            print('Error connecting or establishing an SSH session.')
            self.login(hostname, username, password)
        except AuthenticationException:
            print('Authentication failed.')
            self.login(hostname, username, password)  
    
    def debug_info(self, stdout, stderr) -> None:
        print(f'STDOUT: {stdout.read().decode("utf8")}')
        print(f'STDERR: {stderr.read().decode("utf8")}')
        
        print(f'Return code: {stdout.channel.recv_exit_status()}')