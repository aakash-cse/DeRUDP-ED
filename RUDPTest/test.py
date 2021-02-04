import time
import sys

from rudp_client import RUDPClient

client = RUDPClient()

def find_roundtriptime():
	initial_time = time.time() 
	client.connect(("127.0.0.1", 8000))
	client.send('hello'.encode('ascii'))
	msg = client.recv(1000)
	ending_time = time.time() 
	elapsed_time = str(ending_time - initial_time)
	client.close()
	print('The Round Trip Time for {} is {}'.format("127.0.0.1", elapsed_time))
find_roundtriptime()