from derudped.aes import AESCipher
# The following code is to test the AES encryption of the image data
text = "Hi Everyone"
key = "Aakash"

obj = AESCipher(key)
encry = obj.encrypt(text)
print(encry)
decry = obj.decrypt(encry)
print(decry)