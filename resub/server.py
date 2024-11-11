import socket
import ssl
import threading
import time

# Server details
HOST = 'localhost'  # localhost
PORT = 5000

#Order
r = 50

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to an address and port
server_socket.bind((HOST, PORT))
server_socket.listen(3)
print(f'Server listening on {HOST}:{PORT}')

# Wrap the server socket with SSL (TLS)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

number_of_participant = 0
sockets = []
addresses = []
lock = threading.Lock()

comp = 0

numReceived = 0

def handle_client(client_socket, client_addr):
        global number_of_participant
        global numReceived
        global comp
        # Accept client connections
        print(number_of_participant)
        print(f"Client {client_addr} connected")

        with lock:
            number_of_participant += 1

        #Next step is to wait. and add responses. Because the next things the server is gonna receive is the
        while numReceived < 3:
            data = client_socket.recv(1024).decode('utf-8')
            print("received : " + data)
            if data:
                with lock:
                    temp = comp
                    comp =(temp + int(data)) % (r)
                    numReceived += 1
                    print("comp = " + str(temp) + " + " + data + " = " + str(comp))
        client_socket.close()


while numReceived < 3:

    # Accept client connections
    try:
        client_socket, client_addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.start()
    except:
         print("something went wrong")
    time.sleep(2)
print(comp)

