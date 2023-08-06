from cryptography.fernet import Fernet
import string, random

def passwordToken():
    #---- Generates a random token that is stored that will be used to encrypt user data ----
    passwordToken = ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(120))
    privateToken, privateKey = encryption(passwordToken)
    storedPrivateKey = privateToken.decode("UTF-8") + ":" + privateKey.decode("UTF-8")    
    return storedPrivateKey

def generateSessionToken(username):
    #---- Generates a random 128 character long SessionToken 
    sessionToken = ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(120))
    return encryption(username + ":" + sessionToken)

def dataEncrpytion(text, GeneratedToken):
    #---- Generate a random 128 character password with password to show on the servers and files to save ----
    RandomText = ''.join(random.choice(text + string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(120))
    #---- Creates a random number within the bounds of the length of passwords (basically shoves text in a random location) ----
    TextPoint = random.randrange(len(text))
    RandomTextPoint = random.randrange(len(RandomText))
    #---- Combine all the random points and text together to store this password ----
    text = text[:TextPoint] + RandomText[:RandomTextPoint] + GeneratedToken + RandomText[RandomTextPoint:] + text[TextPoint:]
    TextToken, TextKey = encryption(text)
    RandomTextToken, RandomTextKey = encryption(RandomText)
    return TextToken.decode("utf-8")+":" + TextKey.decode("utf-8") + ":" + RandomTextToken.decode("UTF-8") + ":" + RandomTextKey.decode("UTF-8")

def encryption(text):
    #---- Changes string to byte format ----
    bytetext = str.encode(text)
    #--- Generates a special key ----
    key = Fernet.generate_key()
    encryption_type = Fernet(key)
    #---- Makes Token string an encrypted fernet with the generated key for the byte string ----
    token = encryption_type.encrypt(bytetext)
    #---- Returns encrypted text text format ----
    return token, key

def dataDecryption(EncryptedText, GeneratedToken):
    decryptedpassword = decryption(str.encode(EncryptedText.split(":")[0]), str.encode(EncryptedText.split(":")[1]))
    return decryptedpassword.replace(GeneratedToken,"").replace(decryption(str.encode(EncryptedText.split(":")[2]), str.encode(EncryptedText.split(":")[3])), "")

def decryption(token, key):
    #---- Will decrypt the encrypted text with a token and key ----
    encryption_type = Fernet(key)
    return encryption_type.decrypt(token).decode()