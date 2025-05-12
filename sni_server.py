import socket
import threading
import sys

def handle_client(client_socket, target_host, target_port):
    try:
        # Connect to the target service (e.g., SSH on localhost)
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target_host, target_port))

        # Start forwarding traffic in both directions
        threading.Thread(target=forward, args=(client_socket, remote_socket)).start()
        threading.Thread(target=forward, args=(remote_socket, client_socket)).start()

    except Exception as e:
        print(f"[!] Error handling client: {e}")
        client_socket.close()

def forward(source, destination):
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    except:
        pass
    finally:
        source.close()
        destination.close()

def start_sni_proxy(listen_port, forward_host, forward_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', listen_port))
    server.listen(100)

    print(f"[+] SNI Proxy running on 0.0.0.0:{listen_port} -> {forward_host}:{forward_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[+] New connection from {addr[0]}:{addr[1]}")
        threading.Thread(target=handle_client, args=(client_socket, forward_host, forward_port)).start()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <listen_port> <forward_host> <forward_port>")
        sys.exit(1)

    listen_port = int(sys.argv[1])
    forward_host = sys.argv[2]
    forward_port = int(sys.argv[3])

    start_sni_proxy(listen_port, forward_host, forward_port)

