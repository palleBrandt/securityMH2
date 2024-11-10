import random
import socket
import threading
import time
import sys

#Order of my field
r = 50
#Choose random secret between 0-r
secret = random.randint(0,r)
#compute shares
share1 = random.randint(0,r)
share2 = random.randint(0,r)
shares = [share1, share2]
myshare = ((((secret - share1 + r) % (r+1)) - share2 + r) % (r+1))

lock = threading.Lock()

# List to store active peer connections
peer_connections = []

shares_received = 0
connections = 0

def handle_incoming_connection(sock, addr):
    """Receive messages from the peer."""
    global myshare
    global shares_received
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            print(f"\n{addr}: {message}")
            with lock:
                shares_received += 1
                temp = myshare
                myshare = (temp + int(message)) % (r+1)
        except:
            print("Could not receive:" )

def handle_outgoing_messages():
    global connections
    while connections < 2:
        continue

    # peer1_con.sendall("hi".encode('utf-8'))
    # peer2_con.sendall("hi".encode('utf-8'))

    i = 0
    while i < 2:
        success = False
        while not success:
            try:
                peer_connections[i].sendall(str(shares[i]).encode('utf-8'))
                success = True
                i+= 1
            except:
                print("Failed to send message to a peer.")
    
    # """Send messages to all connected peers."""
    # send = False
    # while not send:
    #     try:
    #         peer_connections[0].sendall(str(secret).encode('utf-8'))
    #     except ConnectionRefusedError:
    #         print(f"Peer on port {peer_ports[0]} not available, retrying...")
    #         time.sleep(2)
    # send = False
    # while not send:
    #     try:
    #         peer_connections[1].sendall(str(secret).encode('utf-8'))
    #     except ConnectionRefusedError:
    #         print(f"Peer on port {peer_ports[1]} not available, retrying...")
    #         time.sleep(2)

def start_peer(host, port, peer_ports):
    # Create a socket to act as a server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen(len(peer_ports))  # Listen for multiple connections

    # Thread to accept incoming connections
    def accept_connections():
        global connections
        while True:
            conn, addr = server_sock.accept()
            with lock:
                connections += 1
            print(f"Peer connected from {addr}")
            # peer_connections.append(conn)
            # Start a thread to handle incoming messages from this connection
            threading.Thread(target=handle_incoming_connection, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_connections, daemon=True).start()

    # Attempt to connect to each peer in peer_ports if not already connected
    connected = False
    global peer1_con
    global peer2_con
    while not connected:
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((host, peer_1))
            print(f"Connected to peer1 at {host}:{peer_1}")
            peer_connections.append(client_sock)
            connected = True
        except ConnectionRefusedError:
            print(f"Peer on port {peer_1} not available, retrying...")
            time.sleep(2)

    connected = False
    while not connected:
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((host, peer_2))
            print(f"Connected to peer1 at {host}:{peer_2}")
            peer_connections.append(client_sock)
            connected = True
        except ConnectionRefusedError:
            print(f"Peer on port {peer_2} not available, retrying...")
            time.sleep(2)


    # for peer_port in peer_ports:
    #     connected = False
    #     while not connected:
    #         try:
    #             client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             client_sock.connect((host, peer_port))
    #             print(f"Connected to peer at {host}:{peer_port}")
    #             peer_connections.append(client_sock)
    #             connected = True
    #         except ConnectionRefusedError:
    #             print(f"Peer on port {peer_port} not available, retrying...")
    #             time.sleep(2)

    # Start a thread to handle outgoing messages to all peers
    handle_outgoing_messages()

    global shares_received
    while shares_received < 2:
        # print("not enough")
        continue
    
    connected = False
    hospital_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not connected:
        try:
            hospital_sock.connect((host, 5000))
            connected = True
            print(f"Connected to hospital")
        except Exception:
            print(f"Hospital not available, retrying...")
            time.sleep(2)

    hospital_sock.sendall(str(myshare).encode('utf-8'))

    while True:
        continue

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 peer.py <own_port> <peer_port1> <peer_port2>")
        sys.exit(1)

    host = 'localhost'
    port_my = int(sys.argv[1])
    peer_1 = int(sys.argv[2])
    peer_2 = int(sys.argv[3])
    peer_ports = [int(sys.argv[2]), int(sys.argv[3])]  # The ports of the other peers
    
    print("My secret is: " + str(secret))
    start_peer(host, port_my, peer_ports)
