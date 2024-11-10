import random
import socket
import ssl
import threading
import time

# Define server details
host = 'localhost'
port_s = 65432
port_1 = 65433
port_2 = 65343
port_my = 65345


connected = False

#Order of my field
r = 50
#Choose random secret between 0-r
secret = random.randint(0,r)

#compute shares
share1 = random.randint(0,r)
share2 = random.randint(0,r)
shares = [share1, share2]

myshare = ((((secret - share1 + r) % (r+1)) - share2 + r) % (r+1))

numReceived = 0

lock = threading.Lock()

# Load SSL context and verify server certificate
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('server.crt')

context1 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context1.load_verify_locations('client1.crt')

context2 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context2.load_verify_locations('client2.crt')

def connector(port, context):
    global connected
    while connected == False:
        continue
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tls_client_socket = context.wrap_socket(client_socket, server_hostname=host)
    tls_client_socket.connect((host, port))

def caller(con):
    with lock:
        con.sendall(str(shares.pop))

def listener(con):
    global numReceived
    con.setblocking()
    data = client_socket.recv(1024).decode('utf-8')
    print(f"Received from client: {data}")
    with lock:
        numReceived += 1
        temp = myshare
        myshare = (temp + int(data)) % (r+1)
    con.close()

def handleClient(con, addr):
    print(f"Client {addr} connected")
    con.setblocking(True)

    listener_thread = threading.Thread(target=listener, args=(con))
    listener_thread.start()

    call_thread = threading.Thread(target=caller, args=(con))
    call_thread.start()

    listener_thread.join()
    call_thread.join()

def serverlistener(con):
    global connected
    con.setblocking(True)
    while connected == False:
        # Receive response from server
        response = con.recv(1024)
        if response:
            print(f"Received from server: {response.decode('utf-8')}")
            with lock:
                connected = True
    while numReceived < 2:
        continue
    con.sendall(str(myshare))

def handleserver(con):
    # Wrap own server socket with SSL (TLS)
    contextOwnServer = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contextOwnServer.load_cert_chain(certfile='client1.crt', keyfile='client1.key')
    with contextOwnServer.wrap_socket(con, server_side=True) as tls_server_socket:
        while True:
            # Accept client connections
            client_socket, client_addr = tls_server_socket.accept()
            
            # Handle each client in a new thread
            client_thread = threading.Thread(target=handleClient, args=(client_socket, client_addr))
            client_thread.start()

#Setup own server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host,port_my))
server_socket.listen(2)
print("Client listening")

server_thread = threading.Thread(target=handleserver, args=(server_socket,))
server_thread.start()

# Wrap the socket with the SSL context for server connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tls_client_socket = context.wrap_socket(client_socket, server_hostname=host)
tls_client_socket.connect((host, port_s))

#Listen on to server
listener_thread = threading.Thread(target=serverlistener, args=(tls_client_socket,))
listener_thread.start()

#Connect to other clients
con2_thread = threading.Thread(target=connector, args=(port_1, context1))
con3_thread = threading.Thread(target=connector, args=(port_2, context2))
con2_thread.start()
con3_thread.start()

listener_thread.join()
