from unittest import TestCase

from src.pyStFTP.pyStFTP import create_sftp_client


class Test(TestCase):
    def test_create_sftp_client(self):
        host = 'localhost'
        port = 22
        username = 'ivan'
        keyfile_path = None
        password = 'secretpassword'

        sftpclient = create_sftp_client(host, port, username, password,
                                        keyfile_path,
                                        'DSA')

        # List files in the default directory on the remote computer.
        dirlist = sftpclient.listdir('.')
        for row in dirlist:
            print
            row

        # Retrieve a file with the name 'remote_file.txt' on the remote
        # computer and
        # store it in a file named 'downloaded_file.txt'
        # next to this SFT client program.
        sftpclient.get('remote_file.txt', 'downloaded_file.txt')
        # Upload a file that locally has the name 'testfile.txt' to a file
        # on the
        # remote computer that will have the name 'remote_testfile.txt'.
        sftpclient.put('testfile.txt', 'remote_testfile.txt')

        # We're done with the SFTPClient.
        sftpclient.close()

