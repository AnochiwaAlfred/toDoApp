# import rsa
import random
import string
from cryptography.fernet import Fernet




def randomCharacter(length):  
    letters = string.ascii_lowercase # define the specific string  
    # define the condition for random.sample() method  
    result = ''.join((random.sample(letters, length)))   
    return result
  




# https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/
def hasherGenerator():
    '''
    word hasherGenerator. Can be used for hashing password, create a session pass key.
    '''

    message=randomCharacter(10)
    key = Fernet.generate_key()
    # Instance the Fernet class with the key
    fernet = Fernet(key)
    encMessage = fernet.encrypt(message.encode())
    return {
        'key':key, 
        # 'message':message, 
        'token':encMessage
    }




def decrypter(key, token):
    '''
    data: is passed in as a dictionary. {'key':key, 'message':message, 'token':encMessage}
    '''
    fernet = Fernet(key)
    result = fernet.decrypt(token).decode()
    return result

# dt =  hasherGenerator()
# print(dt)
# d = decrypter(key=dt.get('key'), token=dt.get('token'))
# print(d)