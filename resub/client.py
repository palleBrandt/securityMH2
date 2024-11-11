import random
import socket
import ssl
import threading
import time
import sys

# Order of my field
r = 50

# Choose random secret between 0-r
secret = random.randint(0, r)
# Compute shares
share1 = random.randint(0, r)
share2 = random.randint(0, r)
shares = [share1, share2]
myshare = ((((secret - share1 + r) % r) - share2 + r) % r)

# Lock for thread-safe operations
lock = threading.Lock()

# List to store active peer connections
peer_connections = []
shares_received = 0
connections = 0

def handle_incoming_connection(sock, addr):
    #Receive messages from the peer.
    global myshare, shares_received
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            with lock:
                shares_received += 1
                temp = myshare
                myshare = (temp + int(message)) % r
                # print(f"My share updated to: {temp} + {message} = {myshare}")
        except:
            print("Could not receive from peer:", addr)
            break
    sock.close()

def handle_outgoing_messages():
    global connections
    #Wait till two peers connected
    while connections < 2:
        continue

    i = 0
    while i < 2:
        success = False
        while not success:
            try:
                #Send shares to peers
                peer_connections[i].sendall(str(shares[i]).encode('utf-8'))
                success = True
                i+= 1
            except:
                print("Failed to send message to a peer.")

def start_peer(host, port, peer_ports):
    # Create a socket to act as a server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen(len(peer_ports))  # Listen for multiple connections
    secure_server_sock = server_context.wrap_socket(server_sock, server_side=True) #Wrap socket

    # Thread to accept incoming connections
    def accept_connections():
        global connections
        while True:
            conn, addr = secure_server_sock.accept()
            with lock:
                connections += 1
            threading.Thread(target=handle_incoming_connection, args=(conn, addr), daemon=True).start()
    threading.Thread(target=accept_connections, daemon=True).start()

    # Connect to each peer in peer_ports securely
    for peer_port in peer_ports:
        connected = False
        while not connected:
            try:
                client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                secure_client_sock = client_context.wrap_socket(client_sock, server_hostname="localhost")
                secure_client_sock.connect((host, peer_port))
                peer_connections.append(secure_client_sock)
                connected = True
            except ConnectionRefusedError:
                print(f"Peer on port {peer_port} not available, retrying...")
                time.sleep(2)

    # Start outgoing message handling in a separate thread
    threading.Thread(target=handle_outgoing_messages, daemon=True).start()

    # Wait until all shares are received
    global shares_received
    while shares_received < 2:
        continue

    # Connect to hospital and send the final share securely
    connected = False
    while not connected:
        try:
            hospital_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secure_hospital_sock = client_context.wrap_socket(hospital_sock, server_hostname="localhost")
            secure_hospital_sock.connect((host, 5000))
            secure_hospital_sock.sendall(str(myshare).encode('utf-8'))
            connected = True
            print("Sent local computation to hospital")
        except Exception:
            print("Hospital not available, retrying...")
            time.sleep(2)


if len(sys.argv) != 5:
    print("Usage: python3 peer.py <client_number> <own_port> <peer_port1> <peer_port2>")
    sys.exit(1)

host = 'localhost'
port_my = int(sys.argv[2])
peer_ports = [int(sys.argv[3]), int(sys.argv[4])]
clientId = "client"+sys.argv[1] #Each client has their own certificate, using clientId to differentiate.

# SSL context for server
server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_context.load_cert_chain(certfile=clientId + '.crt', keyfile=clientId + '.key') #Use specific certificate
server_context.load_verify_locations("CA.pem")

# SSL context for client
client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client_context.load_verify_locations("CA.pem")

print(f"My secret is: {secret}")
start_peer(host, port_my, peer_ports)
