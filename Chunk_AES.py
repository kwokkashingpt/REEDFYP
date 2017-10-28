# !/usr/bin/env python
# coding: utf-8
'''

'''

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import os
import md5

def read_in_block(file_path,BLOCK_SIZE = 1024):  

    with open(file_path, "r") as f:  
        while True:  
            block = f.read(BLOCK_SIZE)  
            if block:  
                yield block  
            else:  
                return  
  
  
def test3():  
    file_path = "C:\Users\kashing\Desktop\Client\RFNgram.java"
    filedir,name = os.path.split(file_path)
    name,ext = os.path.splitext(name)
    filedir = os.path.join(filedir,name)
    if not os.path.exists(filedir):
        os.mkdir(filedir)  

    partno = 1
    for block in read_in_block(file_path):
        partfilename = os.path.join(filedir,name + '_' + str(partno) + ext)
        print('write start %s' % partfilename)
        part_stream = open(partfilename,'w')  
        if block:
            m = md5.new(block)  
            mycrypt = MyCrypt(m.hexdigest())
            part_stream.write(block)
            e = mycrypt.myencrypt(block)
            d = mycrypt.mydecrypt(e)
            print e
            print "**************************************************************************"
        else:
            break
        part_stream.close()
        partno += 1

class MyCrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def myencrypt(self, text):
        length = 16
        count = len(text)
        print count
        if count < length:
            add = length - count
            text= text + ('\0' * add)

        elif count > length:
            add = (length -(count % length))
            text= text + ('\0' * add)

        # print len(text)
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    def mydecrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')

if __name__ == '__main__':
    test3()
    