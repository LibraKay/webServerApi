# -*- coding: UTF-8 -*-
from paramiko import SSHClient, AutoAddPolicy, SFTPClient


class RemoteClient:
    def __init__(self, remote_host, port=22, username=None, password=None):
        self.remote_host = remote_host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = self.ssh_connection(self.remote_host, self.port, self.username, self.password)

    def ssh_connection(self, remote_host, port=22, username=None, password=None):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(remote_host, port, username, password)
        return ssh_client

    def upload_file(self, local_path, remote_path):
        sftp = SFTPClient.from_transport(self.ssh_client.get_transport())
        sftp.put(local_path, remote_path)
        self.ssh_client.close()

    def closeConnection(self):
        self.ssh_client.close()