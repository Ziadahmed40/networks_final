import socket
import time

def calculate_checksum(data):
    checksum = 0
    for char in data:
        checksum += ord(char)
    return checksum

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

    # Simulate data transfer
    sequence_number = 0
    for i in range(5):
        message = f"Message {i}"
        checksum = calculate_checksum(message)
        # print("checksum: " , checksum," type: ",type(checksum))
        
        packet = f"{sequence_number}|{checksum}|{message}"
        client_socket.sendto(packet.encode(), server_address)

        # Wait for ACK or NACK
        while True:
            time.sleep(1)
            data, server_address = client_socket.recvfrom(1024)
            ack_type, ack_sequence_number = data.decode().split('|')
            print("ACK: ",ack_type)
            print("ACK seq: ",ack_sequence_number)
            if ack_type == "ACK" and int(ack_sequence_number) == sequence_number:
                print(f"ACK received for message {i}")
                sequence_number = 1 - sequence_number  # Toggle sequence number
                break
            else:
                print("Timeout or NACK received. Retransmitting packet...")
                client_socket.sendto(packet.encode(), server_address)

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    main()
