from rudp_client import RUDPClient

client = RUDPClient()
client.connect(("127.0.0.1", 8000))
print('Connected established...')

client.send('hello'.encode('ascii'))

client.close()