import socket
import time

def calculate_checksum(data):
    checksum = 0
    for char in data:
        checksum += ord(char)
    return checksum

class UDPServer:
    def __init__(self, host='localhost', port=9999):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)

    # def calculate_checksum(self, data):
    #     checksum = 0
    #     for char in data:
    #         checksum += ord(char)
    #     return checksum

    def handshake(self):
        print("Server is waiting for connection...")
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            if data.decode() == "Ahlan":
                print(f"Received handshake from {client_address}")
                self.server_socket.sendto("ACK".encode(), client_address)
                break
        print("Connection established.")

    def run(self, max_messages=5):
        self.handshake()
        expected_sequence_number = 0
        messages_received = 0

        while messages_received < max_messages:
            time.sleep(1)
            data, client_address = self.server_socket.recvfrom(1024)
            received_sequence_number, received_checksum, message = data.decode().split('|')
            received_checksum = int(received_checksum)
            calculated_checksum = calculate_checksum(message)

            if received_sequence_number == str(expected_sequence_number) and received_checksum == calculated_checksum:
                print("Received:", message)
                ack_message = f"ACK|{expected_sequence_number}"
                self.server_socket.sendto(ack_message.encode(), client_address)
                expected_sequence_number = 1 - expected_sequence_number
                messages_received += 1
            else:
                print("Packet loss or corrupted data. Retransmitting ACK...")
                nack_message = f"NACK|{1 - expected_sequence_number}"
                self.server_socket.sendto(nack_message.encode(), client_address)

        print("All messages received. Closing connection.")
    def close(self):
        self.server_socket.close()

class UDPClient:
    def __init__(self, host='localhost', port=9999):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        print("Connection established1.")
        self.client_socket.sendto("Ahlan".encode(), self.server_address)
        print("Connection established2.")
        while True:
            data, _ = self.client_socket.recvfrom(1024)
            print("Received:", data.decode())
            if data.decode() == "ACK":
                print("Handshake successful.")
                break
            time.sleep(1)
            print("Handshake fail")

    def send_data(self):
        sequence_number = 0
        for i in range(5):
            message = f"Message {i}"
            checksum = calculate_checksum(message)
            packet = f"{sequence_number}|{checksum}|{message}"
            self.client_socket.sendto(packet.encode(), self.server_address)

            while True:
                time.sleep(1)
                data, _ = self.client_socket.recvfrom(1024)
                ack_type, ack_sequence_number = data.decode().split('|')
                if ack_type == "ACK" and int(ack_sequence_number) == sequence_number:
                    print(f"ACK received for message {i}")
                    sequence_number = 1 - sequence_number
                    break
                else:
                    print("Timeout or NACK received. Retransmitting packet...")
                    self.client_socket.sendto(packet.encode(), self.server_address)

    def close(self):
        self.client_socket.close()

if __name__ == "__main__":
    max_messages = 5
    udp_server = UDPServer()
    udp_client = UDPClient()
    udp_client.handshake()  # Perform handshake first
    udp_server.run()  # Start the server after the handshake
    udp_client.send_data(max_messages=max_messages)
    udp_client.close()
    udp_server.close()
