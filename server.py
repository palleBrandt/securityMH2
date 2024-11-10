import socket
import ssl
import threading

# Server details
HOST = 'localhost'  # localhost
PORT = 65432

#Order
r = 50

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to an address and port
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'Server listening on {HOST}:{PORT}')

# Wrap the server socket with SSL (TLS)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='server.crt', keyfile='server.key')
context.load_verify_locations("CA.pem")

number_of_participant = 0
sockets = []
addresses = []
lock = threading.Lock()

comp = 0

numReceived = 0

def handle_client(client_socket, client_addr):
        global number_of_participant
        loading = True

        # Accept client connections
        print(f"Client {client_addr} connected")
        with lock:
            participant_id = number_of_participant
            sockets.append(client_socket)
            addresses.append(client_addr)
            number_of_participant += 1
        
        # # Receive data from client
        # data = client_socket.recv(1024).decode('utf-8')
        # print(f"Received from client: {data}")
        while loading:
            if not number_of_participant < 2:
                  
                        client_socket.sendall(str(True).encode('utf-8'))
                        loading = False

        #Next step is to wait. and add responses. Because the next things the server is gonna receive is the
        while numReceived < 2:
            data = client_socket.recv(1024).decode('utf-8')
            with lock:
                temp = comp
                comp =(temp + int(data)) % (r+1)
        client_socket.close()


with context.wrap_socket(server_socket, server_side=True) as tls_server_socket:
    while number_of_participant < 2:
        # Accept client connections
        client_socket, client_addr = tls_server_socket.accept()
        
        # Handle each client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.start()
    while numReceived < 2:
        continue
    print(comp)

