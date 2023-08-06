# **AdvancedFernetDataEncryption**

An encryption that uses the Fernet assymetric key generator and random values to create a secure token and key that can be stored and still be unreadable to any user. 

## **Methods Supported**
- passwordToken(): Generates a random 120 length string and encrypts with fernet assymmetric algorithm `return <string>`
- generateSessionToken(<AnyString>): Generates a random 120 length string and encrypts with fernet assymetric algorithm. Used for Web Sessions `return Token, Key`
- dataEncryption(<PlainTxt>, <Token>): Generates a random 120 length string and shoves it randomly in the PlainTxt and shoves the token randomly in the 120 length string generated. Then all of this information is encrypted with the fernet algorithm. `return <string>`
- encryption(<AnyString>): Base method that simply adds a fernet encryption. `return Token, Key`
- dataDecrpytion(<EncyptedTxt>, <Token>): Decodes the giant encrypted text generated and creates a plain text version `return <String>`
- decryption(<AnyString>): Base method that simply decodes the fernet encryption. `return <String>`

## **Basic Usage Example**
```python
from AdvancedFernetDataEncryption import *

Token = passwordToken()
text = "Hello I would like to be encrypted
encryptedText = dataEncryption(text, Token)
unencryptedText = dataDecrpytion(text, Token)
```

When run these following lines the text will be encrypted and would be unecryptable without the usage of the Token generated. 