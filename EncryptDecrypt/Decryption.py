#!/usr/bin/env python
# coding: utf-8

# In[29]:


f = open("ToBeSent for Decryption/cipher2.txt",'r',encoding='utf-8')
cipher = f.read()


# In[2]:


import base64


# In[3]:


import numpy as np
import cv2


# In[30]:


P = cv2.imread('ToBeSent for Decryption/P.png')
R = cv2.imread('ToBeSent for Decryption/R.png')


# In[31]:


h = np.shape(P)[0]
w = np.shape(P)[1]


# In[6]:


CK = np.ones((h,w,1), dtype = 'uint8')


# In[7]:


for i in range(h):
    for j in range(w):
        ck = P[i][j][0] ^ R[i][j][0]
        CK[i][j][0] = ck


# In[8]:


K1 = []
for i in range(len(CK)):
    K1.append(0)


# In[9]:


for i in range(len(CK)):
    count = 0
    for j in range(len(CK[i])):
        if CK[i][j][0] == 0:
            count += 1
    K1[i] = chr(count)


# In[10]:


K1 = "".join(K1)


# In[11]:


K1


# In[12]:


import hashlib 
SK1 = hashlib.sha256(K1.encode()) 

print("The hexadecimal equivalent of SHA256 is : ") 
print(SK1.hexdigest()) 


# In[13]:


# AES 256 in OFB mode:
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
from base64 import b64encode,b64decode

class AESCipher:
    def __init__(self,data,key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr (self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def decrypt(self):
        cipher_text = b64decode(self.data.encode())
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key,AES.MODE_OFB,iv)
        return self.unpad(cipher.decrypt(cipher_text[self.block_size:])).decode()


# In[14]:


import pandas as pd


# In[15]:


xdf = pd.DataFrame(columns = ['1','2'])
a = []
b = []
for i in P:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k%2==0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1    
    a.append(sum(n1))
    b.append(sum(n2))
xdf['1'] = a
xdf['2'] = b


# In[16]:


ydf = pd.DataFrame(columns = ['1','2'])
a = []
b = []
for i in R:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k%2==0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1    
    a.append(sum(n1))
    b.append(sum(n2))
ydf['1'] = a
ydf['2'] = b


# In[17]:


from sklearn.linear_model import LinearRegression


# In[18]:


LRmodel = LinearRegression()
LRmodel.fit(xdf,ydf)


# In[19]:


zdf = pd.DataFrame(columns = ['1','2'])
a = []
b = []
for i in CK:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k%2==0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1    
    a.append(sum(n1))
    b.append(sum(n2))
zdf['1'] = a
zdf['2'] = b


# In[20]:


predict = LRmodel.predict([[sum(zdf['1']),sum(zdf['2'])]])


# In[21]:


x = round(predict[0][0])%26
y = round(predict[0][1])%26


# In[22]:


cipher = cipher.split(' ')


# In[32]:


txt = []
for each in cipher:
    try:
        ch = ord(each) - x + y
        txt.append(int(ch))
    except:
        print(each)


# In[33]:


text = ""
for t in txt:
    text += chr(t)


# In[35]:


de = AESCipher(text,SK1.hexdigest()).decrypt()


# In[36]:


de = de.encode("utf-8")


# In[37]:


with open("DecryptedImg2.png", "wb") as fh:
    fh.write(base64.decodebytes(de))


# In[ ]:




