from AdvancedFernetDataEncryption import *
import json

# Generates the Token and stores the random token into the Token.json file 
def writeJson():
    with open("Token.json", "w") as outfile:
        outfile.write(json.dumps({"GenerateToken":passwordToken()}))

# Reads all information from Token.json file and stores in the dictionary data
def useJson():
    with open("Token.json") as Token:
        TokenJson = json.load(Token)
    return TokenJson

# Encrypts any plain text and uses the token that is stored to generate an encrypted text
def encryption():
    TokenJson = useJson()
    plainText = input("Plan text: ")
    print("Encrypted Text: ", dataEncrpytion(plainText, TokenJson.get("GenerateToken")))

# Encrypts any encrypted text and generates the plain text with the token stored
def decryption():
    TokenJson = useJson()
    encryptedText = input("Encrypted Text: ")
    print("Decrypted Text: ", dataDecryption(encryptedText, TokenJson.get("GenerateToken")))

# Generates a unique sessionToken and Key for user sessions (For Web Servers)
def WebSession():
    UsernameToken = input("User Session: ")
    SessionToken, SessionKey = generateSessionToken(UsernameToken)
    print ("Session Token: ", SessionToken)
    print("Session Key: ", SessionKey)