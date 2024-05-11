import signal
import socket
import sys
import time
import os

import keyboard


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
        self._connection_type = None
        # signal.signal(signal.SIGINT, self._handle_interrupt)
        #
        # keyboard.add_hotkey('ctrl+f2', self._handle_ctrl_f2)
        self._run_detect_intterupts(self._connect)

    # def _handle_interrupt(self, signum, frame):
    #     print("\nCtrl+C pressed. Closing connection...")
    #     self.close()
    #     sys.exit(0)
    #
    # def _handle_ctrl_f2(self):
    #     print("\nCtrl+F2 c pressed. Closing connection...")
    #     self.close()
    #     sys.exit(0)

    def close(self):
        self._server_socket.close()

    def _connect(self):
        print("Server is waiting for connection...")
        while True:
            data, self._current_client = self._server_socket.recvfrom(1024)
            data = data.decode().split('|')
            if data[0] == "Ahlan":
                self._connection_type = True if data[1] == 'True' else False
                self._server_socket.settimeout(10) if self._connection_type else self._server_socket.settimeout(None)
                print(f"Received handshake from {self._current_client}")
                self._server_socket.sendto("ACK".encode(), self._current_client)
                break
        print("Connection established.")

    def _handle_http_requests(self, data):
        method = data[0]
        path = data[1]
        if method == "GET":
            try:
                with open(os.getcwd() + path.strip(), 'r') as file:
                    response_body = file.read()
                response = f"HTTP/1.0 200 OK\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
            except FileNotFoundError:
                response = "HTTP/1.0 404 Not Found\r\n\r\nFile Not Found"
        elif method == "POST":
            body = data[3]
            response = f"HTTP/1.0 200 OK\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        else:
            response = "HTTP/1.0 400 Bad Request\r\n\r\nUnsupported Method"
        self._server_socket.sendto(response.encode(), self._current_client)

    def _run_detect_intterupts(self, function):
        try:
            print("inside")
            function()
        except KeyboardInterrupt:
            print("interrupt to terminate ...clossing server")
            self._server_socket.close()
            sys.exit(0)

    def _run_internal(self):
        global data, client_address
        expected_sequence_number = 0
        while True:
            time.sleep(1)
            try:
                data, client_address = self._server_socket.recvfrom(1024)
            except socket.timeout:
                print(f"time out ..closing peristent conection with {self._current_client}")
                self._server_socket.settimeout(None)
                self._connect()
                continue
            if "HTTP/1.0\r\n\r\n" in data.decode().split('|'):
                self._handle_http_requests(data.decode().split('|'))
                if not self._connection_type:
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
                print("sending acknowledgement message..",ack_message)
                self._server_socket.sendto(ack_message.encode(), client_address)
                expected_sequence_number = 1 - expected_sequence_number  # Toggle sequence number
            else:
                print("Packet loss or corrupted data. Retransmitting ACK...")
                # Send NACK
                nack_message = f"NACK|{1 - expected_sequence_number}"
                print("sending Nacknowledgement message..",nack_message)
                self._server_socket.sendto(nack_message.encode(), client_address)
            if message == "close":
                print(f"currently clossing connection for {self._current_client}")
                expected_sequence_number = 0
                self._connect()

    def run(self):
        self._run_detect_intterupts(self._run_internal)
