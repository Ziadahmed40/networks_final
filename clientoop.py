import signal
import socket
import sys
import time

import random


class UDP_client_side:
    def _calculate_checksum(self, data):
        checksum = 0
        for char in data:
            checksum += ord(char)
        return checksum

    def __createsocket(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, server_host='localhost', server_port=9999, connection_type="non-persistent"):
        self._server_address = (server_host, server_port)
        self.__createsocket()
        self._connectiontype = True if connection_type == "persistent" else False
        self._first_persistent_hanshake=True
        self._sequence_number=[0]
        self._current_communication=None
        # Register keyboard shortcut for Ctrl+F2
        # keyboard.add_hotkey('ctrl+f2', self._handle_ctrl_f2)
        # signal.signal(signal.SIGINT, self._handle_interrupt)

    # def _handle_ctrl_f2(self):
    #     print("\nCtrl+F2 pressed. Closing connection...")
    #     if not self._connectiontype:
    #         if self._current_communication=="message":
    #             self.close(self._sequence_number)
    #         else:
    #             self._client_socket.close()
    #     else:
    #         self._client_socket.close()
    #     sys.exit(0)
    # def _handle_interrupt(self, signum, frame):
    #     print("\nCtrl+C pressed. Closing connection...")
    #     if not self._connectiontype:
    #         if self._current_communication=="message":
    #             self.close(self._sequence_number)
    #         else:
    #             self._client_socket.close()
    #     else:
    #         self._client_socket.close()
    #     sys.exit(0)

    def simulate_packet_loss(self):
        loss_probability = 0.1  # Example: 10% packet loss probability
        random_number = random.random()
        print("Random number:", random_number)
        if random_number < loss_probability:
            print("Packet loss simulated.")
            time.sleep(random.uniform(0.1, 0.5))  # Simulate delay
            return True
        return False

    def corrupt_packet(self, packet):
        # Simulate packet corruption by randomly modifying data
        corrupted_packet = bytearray(packet)
        for _ in range(random.randint(1, 5)):  # Randomly select 1 to 5 positions to corrupt
            position = random.randint(0, len(packet) - 1)
            corrupted_packet[position] = random.randint(0, 255)  # Modify byte value
        return bytes(corrupted_packet)
    def _handshake(self):
        print("Trying to connect with server....")
        self._client_socket.sendto(f"Ahlan|{self._connectiontype}".encode(), self._server_address)
        while True:
            data, server_address = self._client_socket.recvfrom(1024)
            if data.decode() == "ACK":
                print("Handshake successful.")
                break

    def _send_http_request(self, request):
        self._current_communication="http"
        if not self._connectiontype:
            self.__createsocket()
            self._handshake()
        if self._first_persistent_hanshake and self._connectiontype :
            self._handshake()
            self._first_persistent_hanshake=False
        self._client_socket.sendto(request.encode(), self._server_address)
        response, _ = self._client_socket.recvfrom(1024)
        print(response.decode())
        if not self._connectiontype:
            print(f"clossing connection with server {self._server_address[0]}..")
            self._client_socket.close()
            print("connection clossed succesfully")

    # Implement HTTP GET method
    def http_get(self, path):
        request = f"GET|{path}|HTTP/1.0\r\n\r\n"
        self._send_http_request(request)

    # Implement HTTP POST method
    def http_post(self, path, data):
        request = f"POST|{path}|HTTP/1.0\r\n\r\n|{data}"
        self._send_http_request(request)

    def packing_message_to_be_send(self, message, sequence_number):
        checksum = self._calculate_checksum(message)
        packet = f"{sequence_number[0]}|{checksum}|{message}"
        self._client_socket.sendto(packet.encode(), self._server_address)
        return packet

    def validate_message_sending(self, sequence_number, packet, message):
        while True:
            time.sleep(1)
            data, server_address = self._client_socket.recvfrom(1024)
            ack_type, ack_sequence_number = data.decode().split('|')
            print("ACK: ", ack_type)
            print("ACK seq: ", ack_sequence_number)
            if ack_type == "ACK" and int(ack_sequence_number) == sequence_number[0]:
                print(f"ACK received for message: {message}")
                sequence_number[0] = 1 - sequence_number[0]  # Toggle sequence number
                break
                # return
            else:
                print("Timeout or NACK received. Retransmitting packet...")
                self._client_socket.sendto(packet.encode(), server_address)

    def close(self, sequence_number):
        print(f"clossing connection with server {self._server_address[0]}..")
        packet = self.packing_message_to_be_send("close", sequence_number)
        self.validate_message_sending(sequence_number, packet, "close")
        self._client_socket.close()
        print("connection clossed succesfully")

    def send_message(self, message=None):
        self._handshake()
        self._sequence_number = [0]
        self._current_communication="message"
        if message:
            packet = self.packing_message_to_be_send(message, self._sequence_number)
            self.validate_message_sending(self._sequence_number, packet, message)
        else:
            for i in range(5):
                message = f"Message {i}"
                packet = self.packing_message_to_be_send(message, self._sequence_number)
                self.validate_message_sending(self._sequence_number, packet, message)
        self.close(self._sequence_number)
    def stop_and_wait(self, messages):
        self._handshake()
        sequence_number = [0]

        for message in messages:
            packet = self.packing_message_to_be_send(message, sequence_number)
            # Wait for acknowledgment before sending the next message
            while True:
                time.sleep(1)
                self.validate_message_sending(sequence_number, packet, message)
                break

        self.close(sequence_number)
