import socket
import time

class UDP_client_side:
    def _calculate_checksum(self, data):
        checksum = 0
        for char in data:
            checksum += ord(char)
        return checksum
    def __createsocket(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def __init__(self, server_host='localhost', server_port=9999):
        self._server_address = (server_host, server_port)
        self.__createsocket()
    def _handshake(self):
        print("Trying to connect with server....")
        self._client_socket.sendto("Ahlan".encode(), self._server_address)
        while True:
            data, server_address = self._client_socket.recvfrom(1024)
            if data.decode() == "ACK":
                print("Handshake successful.")
                break
    def _send_http_request(self, request):
        self.__createsocket()
        self._handshake()
        self._client_socket.sendto(request.encode(), self._server_address)
        response, _ = self._client_socket.recvfrom(1024)
        print(response.decode())
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
    def packing_message_to_be_send(self, message,sequence_number):
        checksum = self._calculate_checksum(message)
        packet = f"{sequence_number[0]}|{checksum}|{message}"
        self._client_socket.sendto(packet.encode(), self._server_address)
        return  packet
    def validate_message_sending(self,sequence_number,packet,message):
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
            else:
                print("Timeout or NACK received. Retransmitting packet...")
                self._client_socket.sendto(packet.encode(), server_address)

    def close(self,sequence_number):
        print(f"clossing connection with server {self._server_address[0]}..")
        packet = self.packing_message_to_be_send("close", sequence_number)
        self.validate_message_sending(sequence_number, packet, "close")
        self._client_socket.close()
        print("connection clossed succesfully")
    def send_message(self,message=None):
        self._handshake()
        sequence_number = [0]
        if message:
            packet=self.packing_message_to_be_send(message,sequence_number)
            self.validate_message_sending(sequence_number,packet,message)
        else:
            for i in range(5):
                message = f"Message {i}"
                packet = self.packing_message_to_be_send(message, sequence_number)
                self.validate_message_sending(sequence_number, packet,message)
        self.close(sequence_number)

