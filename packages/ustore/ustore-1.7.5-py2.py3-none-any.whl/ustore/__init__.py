import os
import platform
import hashlib
import json
import pyaes
import random
import uuid
import time
import socket
import string

__author__ = 'JKinc'

udpath = ""

class Initialisation_Error(Exception):
    pass

class Invalid_Input_Error(Exception):
    pass

class User_Exists_Error(Exception):
    pass

class Invalid_Password_Error(Exception):
    pass

def gensalt():
    seed = str(uuid.getnode()) + str(socket.gethostname()) + str(socket.gethostbyname(socket.gethostname())) + str(time.localtime())
    random.seed(seed)
    saltchoice = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    x = random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice) + random.choice(saltchoice)
    return x

global Encryptedconfig
Encryptedconfig = False

if platform.system() == "Windows":

    def init(userdatapath=".", Encryptedconfig = False):
        global udpath
        udpath = userdatapath + "\\USERDATA\\"
        if not os.path.exists(udpath):
            os.mkdir(udpath)
        if not os.path.exists(udpath + "salts\\"):
            os.mkdir(udpath + "salts\\")


        if os.path.exists(udpath + "CONFB.ini"):
            if open(udpath + "CONFB.ini","r").read() == "True":
                Encryptedconfig = True
            else:
                Encryptedconfig = False
        else:
            open(udpath + "CONFB.ini","w").write(str(Encryptedconfig))

        

    def register_account(user,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error
        if not isinstance(password, str):
            raise Invalid_Input_Error

        if udpath == "":
            raise Initialisation_Error

        user = user.encode('utf-8').hex()

        if os.path.exists(udpath + user + "\\"):
            raise User_Exists_Error

        os.mkdir(udpath + user + "\\")
        salt = gensalt()
        open(udpath + "salts\\"+ user + "salt.ini","w").write(salt)
        passwordhash = hashlib.sha256((password + salt).encode()).hexdigest()
        open(udpath + user + "\\password.ini","w").write(passwordhash)


    def setconfig(user,config,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error

        if Encryptedconfig:
            if not isinstance(password, str):
                raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        if Encryptedconfig:
            iv = "InitializationVe"

            salt = open(udpath + "salts\\"+ user + "salt.ini","r").read()

            if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "\\password.ini","r").read():
                raise Invalid_Password_Error

            key = hashlib.sha3_256((password + salt).encode()).digest()
            aes = pyaes.AESModeOfOperationCTR(key)
            config = aes.encrypt(json.dumps(config))
        
            open(udpath + user + "\\config.ini","wb").write(config)

        else:
            open(udpath + user + "\\config.ini","w").write(json.dumps(config))


    def getconfig(user,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error
        if Encryptedconfig:
            if not isinstance(password, str):
                raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        if Encryptedconfig:
            salt = open(udpath + "salts\\"+ user + "salt.ini","r").read()

            iv = "InitializationVe"

            if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "\\password.ini","r").read():
                raise Invalid_Password_Error

            key = hashlib.sha3_256((password + salt).encode()).digest()
            
            aes = pyaes.AESModeOfOperationCTR(key)
            config = json.loads(aes.decrypt(open(udpath + user + "\\config.ini","rb").read()))

        else:
            config = json.loads(open(udpath + user + "\\config.ini","rb").read())

        return config


    def valid_password(user,password):
        if not isinstance(user, str):
            raise Invalid_Input_Error
        if not isinstance(password, str):
            raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        salt = open(udpath + "salts\\"+ user + "salt.ini","r").read()

        if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "\\password.ini","r").read():
            return False
        else:
            return True

else:

    def init(userdatapath=".", Encryptedconfig = False):
        global udpath
        udpath = userdatapath + "/USERDATA/"
        if not os.path.exists(udpath):
            os.mkdir(udpath)
        if not os.path.exists(udpath + "salts/"):
            os.mkdir(udpath + "salts/")


        if os.path.exists(udpath + "CONFB.ini"):
            if open(udpath + "CONFB.ini","r").read() == "True":
                Encryptedconfig = True
            else:
                Encryptedconfig = False
        else:
            open(udpath + "CONFB.ini","w").write(str(Encryptedconfig))

        

    def register_account(user,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error
        if not isinstance(password, str):
            raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        if os.path.exists(udpath + user + "/"):
            raise User_Exists_Error

        os.mkdir(udpath + user + "/")
        salt = gensalt()
        open(udpath + "salts/"+ user + "salt.ini","w").write(salt)
        passwordhash = hashlib.sha256((password + salt).encode()).hexdigest()
        open(udpath + user + "/password.ini","w").write(passwordhash)
    

    def setconfig(user,config,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error

        if Encryptedconfig:
            if not isinstance(password, str):
                raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        if Encryptedconfig:
            iv = "InitializationVe"

            salt = open(udpath + "salts/"+ user + "salt.ini","r").read()

            if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "/password.ini","r").read():
                raise Invalid_Password_Error

            key = hashlib.sha3_256((password + salt).encode()).digest()
            aes = pyaes.AESModeOfOperationCTR(key)
            config = aes.encrypt(json.dumps(config))
        
            open(udpath + user + "/config.ini","wb").write(config)

        else:
            open(udpath + user + "/config.ini","w").write(json.dumps(config))


    def getconfig(user,password):

        if not isinstance(user, str):
            raise Invalid_Input_Error
        if Encryptedconfig:
            if not isinstance(password, str):
                raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        if Encryptedconfig:
            salt = open(udpath + "salts/"+ user + "salt.ini","r").read()

            iv = "InitializationVe"

            if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "/password.ini","r").read():
                raise Invalid_Password_Error

            key = hashlib.sha3_256((password + salt).encode()).digest()
            
            aes = pyaes.AESModeOfOperationCTR(key)
            config = json.loads(aes.decrypt(open(udpath + user + "/config.ini","rb").read()))

        else:
            config = json.loads(open(udpath + user + "/config.ini","rb").read())

        return config


    def valid_password(user,password):
        if not isinstance(user, str):
            raise Invalid_Input_Error
        if not isinstance(password, str):
            raise Invalid_Input_Error
        user = user.encode('utf-8').hex()
        if udpath == "":
            raise Initialisation_Error

        salt = open(udpath + "salts/"+ user + "salt.ini","r").read()

        if not hashlib.sha256((password + salt).encode()).hexdigest() == open(udpath + user + "/password.ini","r").read():
            return False
        else:
            return True
