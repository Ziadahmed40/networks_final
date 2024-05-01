import socket

def calculate_checksum(data):
    checksum = 0
    for char in data:
        checksum += ord(char)  # get the unicode from char example: 'A' = 65
    return checksum

def main():
    # Define the server address and port
    server_address = ('localhost', 8888)

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the server address
    server_socket.bind(server_address)

    print("Server is waiting for connection...")

    # Wait for the client handshake
    while True:
        data, client_address = server_socket.recvfrom(1024)
        if data.decode() == "Ahlan":
            print(f"Received handshake from {client_address}")
            # Send handshake response
            server_socket.sendto("ACK".encode(), client_address)
            break

    print("Connection established.")
    
     # Receive data from client
    expected_sequence_number = 0
    while True:
        data, client_address = server_socket.recvfrom(1024)
        received_sequence_number, received_checksum, message = data.decode().split('|')
        
        received_checksum = int(received_checksum)
        calculated_checksum = calculate_checksum(message)

        if received_sequence_number == str(expected_sequence_number) and received_checksum == calculated_checksum:
            print("Received:", message)
            # Send ACK
            ack_message = f"ACK|{expected_sequence_number}"
            server_socket.sendto(ack_message.encode(), client_address)
            expected_sequence_number = 1 - expected_sequence_number  # Toggle sequence number
        else:
            print("Packet loss or corrupted data. Retransmitting ACK...")
            # Send NACK
            nack_message = f"NACK|{1 - expected_sequence_number}"
            server_socket.sendto(nack_message.encode(), client_address)

    # Close the socket
    server_socket.close()

if __name__ == "__main__":
    main()
