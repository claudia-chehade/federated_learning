import paramiko
import os
import time
import stat
import logging
import argparse

class Connection:
    def __init__(self, sftp_host, sftp_port, sftp_username, sftp_password):
        self.sftp_host = sftp_host
        self.sftp_port = sftp_port
        self.sftp_username = sftp_username
        self.sftp_password = sftp_password


    def connect(self, local_filename: str):
        def download_file(sftp, remotePath, localPath):
            start_time = time.time()
            for fileattr in sftp.listdir_attr(remotePath):  
                if not stat.S_ISDIR(fileattr.st_mode):
                    # sftp.get(os.path.join(remotePath, fileattr.filename), os.path.join(localPath, fileattr.filename))
                    sftp.get(fileattr.filename, os.path.join(localPath, fileattr.filename))
            end_time = time.time()
            elapsed_time = end_time - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            print(f"File downloaded in {int(minutes)} minutes and {int(seconds)} seconds")


        def upload_file(sftp, remote_path, local_path):
            start_time = time.time()
            local_path = '100MB_original.bin'
            if os.path.exists(local_path):
                print(f"The file at {local_path} exists.")
            else:
                print(f"The file at {local_path} does not exist.")

            sftp.put(local_path, remote_path)

            end_time = time.time()
            elapsed_time = end_time - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            print(f"File uploaded in {int(minutes)} minutes and {int(seconds)} seconds ({elapsed_time})")

        try:
            # Make connection and setup client
            paramiko.util.log_to_file("paramiko.log")
            ssh_client = paramiko.SSHClient()

            policy = paramiko.AutoAddPolicy()
            ssh_client.set_missing_host_key_policy(policy)

            ssh_client.connect(
                self.sftp_host, 
                port=self.sftp_port, 
                username=self.sftp_username, 
                password=self.sftp_password
                )
            sftp = ssh_client.open_sftp()

            # Define paths
            local_filepath = os.path.join(".", local_filename)
            remote_path = "transfer_test"
            remote_filepath = os.path.join(remote_path, local_filename)

            print(f'Upload file form {local_filepath} to {remote_filepath}')
            
            # download_file(sftp, remote_path, local_path)
            upload_file(sftp, remote_filepath, local_filepath)
            
            # Close the SFTP and SSH sessions
            sftp.close()
            ssh_client.close()
        except Exception as e:
            print(e)


def main():
   
    parser = argparse.ArgumentParser(description="A script to connect to an SFTP server.")
    parser.add_argument('--sftp-host', required=True, type=str, help="SFTP server hostname or IP address.")
    parser.add_argument('--sftp-port', type=int, default=22, help="SFTP server port (default: 22).")
    parser.add_argument('--sftp-username', type=str, required=True, help="SFTP username.")
    parser.add_argument('--sftp-password', type=str, required=True, help="SFTP password.")
    
    args = parser.parse_args()

    # You can access the arguments like this:
    sftp_host = args.sftp_host
    sftp_port = args.sftp_port
    sftp_username = args.sftp_username
    sftp_password = args.sftp_password

    # Your code to connect to the SFTP server and perform actions goes here
    print(f"Connecting to SFTP server {sftp_host}:{sftp_port} with username {sftp_username} and password {sftp_password}")

    connection = Connection(sftp_host, sftp_port, sftp_username, sftp_password)
    connection.connect('100MB_original.bin')

if __name__ == "__main__":
    main()
