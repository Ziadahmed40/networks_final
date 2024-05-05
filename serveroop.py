import socket
import time
import os

class UDP_server_side:
    def _calculate_checksum(self, data):
        checksum = 0
        for char in data:
            checksum += ord(char)
        return checksum

    def __init__(self, host='localhost', port=9999):
        self._server_address = (host, port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server_socket.bind(self._server_address)
        self._current_client = None
        self._connect()

    def close(self):
        self._server_socket.close()

    def _connect(self):
        print("Server is waiting for connection...")
        while True:
            data, self._current_client = self._server_socket.recvfrom(1024)
            if data.decode() == "Ahlan":
                print(f"Received handshake from {self._current_client}")
                self._server_socket.sendto("ACK".encode(), self._current_client)
                break
        print("Connection established.")
    def _handle_http_requests(self,data):
        method=data[0]
        path=data[1]
        if method == "GET":
            try:
                with open(os.getcwd()+path.strip(), 'r') as file:
                    response_body = file.read()
                response = f"HTTP/1.0 200 OK\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
            except FileNotFoundError:
                response = "HTTP/1.0 404 Not Found\r\n\r\nFile Not Found"
        elif method == "POST":
            body=data[3]
            response = f"HTTP/1.0 200 OK\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        else:
            response = "HTTP/1.0 400 Bad Request\r\n\r\nUnsupported Method"
        self._server_socket.sendto(response.encode(), self._current_client)

    def run(self):
        expected_sequence_number = 0
        while True:
            time.sleep(1)
            data, client_address = self._server_socket.recvfrom(1024)
            if "HTTP/1.0\r\n\r\n" in data.decode().split('|'):
                self._handle_http_requests(data.decode().split('|'))
                print(f"currently clossing connection for {self._current_client}")
                self._connect()
                continue
            received_sequence_number, received_checksum, message = data.decode().split('|')
            received_checksum = int(received_checksum)
            calculated_checksum = self._calculate_checksum(message)
            if received_sequence_number == str(expected_sequence_number) and received_checksum == calculated_checksum:
                print("Received:", message if message != "close" else "ending connection protocol")
                # Send ACK
                ack_message = f"ACK|{expected_sequence_number}"
                self._server_socket.sendto(ack_message.encode(), client_address)
                expected_sequence_number = 1 - expected_sequence_number  # Toggle sequence number
            else:
                print("Packet loss or corrupted data. Retransmitting ACK...")
                # Send NACK
                nack_message = f"NACK|{1 - expected_sequence_number}"
                self._server_socket.sendto(nack_message.encode(), client_address)
            if message == "close":
                print(f"currently clossing connection for {self._current_client}")
                expected_sequence_number = 0
                self._connect()
