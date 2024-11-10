import socket
import threading
import time

# List to store active peer connections
peer_connections = []

def handle_incoming_connection(sock, addr):
    """Receive messages from the peer."""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message:
                print(f"\n{addr}: {message}")
            else:
                break
        except:
            print("Connection lost.")
            break

def handle_outgoing_messages():
    """Send messages to all connected peers."""
    while True:
        message = input("You: ")
        if message:
            for peer_sock in peer_connections:
                try:
                    peer_sock.sendall(message.encode('utf-8'))
                except:
                    print("Failed to send message to a peer.")
                    peer_connections.remove(peer_sock)

def start_peer(host, port, peer_ports):
    # Create a socket to act as a server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen(len(peer_ports))  # Listen for multiple connections

    # Thread to accept incoming connections
    def accept_connections():
        while True:
            conn, addr = server_sock.accept()
            print(f"Peer connected from {addr}")
            peer_connections.append(conn)
            # Start a thread to handle incoming messages from this connection
            threading.Thread(target=handle_incoming_connection, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_connections, daemon=True).start()

    # Attempt to connect to each peer in peer_ports if not already connected
    for peer_port in peer_ports:
        connected = False
        while not connected:
            try:
                client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_sock.connect((host, peer_port))
                print(f"Connected to peer at {host}:{peer_port}")
                peer_connections.append(client_sock)
                connected = True
            except ConnectionRefusedError:
                print(f"Peer on port {peer_port} not available, retrying...")
                time.sleep(2)

    # Start a thread to handle outgoing messages to all peers
    handle_outgoing_messages()

if __name__ == "__main__":
    # Define the host and the unique port for each peer instance
    host = 'localhost'
    port_my = 5003    # Change this for each peer: e.g., 5001, 5002, 5003
    peer_ports = [5002, 5001]  # Define the ports of the other peers

    start_peer(host, port_my, peer_ports)
