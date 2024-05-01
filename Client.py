import socket

def main():
    # Define the server address and port
    server_address = ('localhost', 8888)

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send handshake to server
    client_socket.sendto("Ahlan".encode(), server_address)

    # Wait for handshake response
    while True:
        data, server_address = client_socket.recvfrom(1024)
        if data.decode() == "ACK":
            print("Handshake successful.")
            break

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    main()
