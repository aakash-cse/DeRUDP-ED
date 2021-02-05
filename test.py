from derudped.aes import AESCipher
# The following code is to test the AES encryption of the image data
text = "Hello Everyone"

obj = AESCipher("192.0.2.1:8080")
encry = obj.encrypt(text)
print(encry)
decry = obj.decrypt(encry)
print(decry)