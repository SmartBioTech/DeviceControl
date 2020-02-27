import socket
from Crypto.Cipher import AES


PAD_CHAR = ' '
DELIMITER = ';'
ESCAPE_CHAR = '\\'


class Connection:
    def __init__(self, host_address, host_port, encryption_key, timeout=10):
        self.unescaped = DELIMITER
        self.escaped = ESCAPE_CHAR + DELIMITER
        while len(encryption_key.encode("utf8")) < 16:
            encryption_key += ' '
        secret_key = encryption_key.encode("utf8")[:16]
        self.encrypter = AES.new(secret_key, AES.MODE_ECB)
        self.decrypter = AES.new(secret_key, AES.MODE_ECB)
        self.empty_block = (PAD_CHAR * 16).encode("utf8")

        self.host_address = host_address
        self.host_port = host_port
        self.timeout = timeout

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host_address, self.host_port))
        return sock

    def send_command(self, device, command, args):
        sock = self.connect()
        command = self.construct_command(device, command, args)
        com_msg = command.replace(self.unescaped, self.escaped) + DELIMITER
        data = com_msg.encode("utf8") + self.empty_block
        while len(data) % 16 != 0:
            data += self.empty_block[0:1]
        cipher_text = self.encrypter.encrypt(data)

        try:
            sock.send(cipher_text)
            recv_buffer = ""
            packet = self.decrypter.decrypt(sock.recv(4096)).decode("utf-8")

            for c in packet:
                if c == DELIMITER and (len(recv_buffer) == 0 or recv_buffer[-1] != ESCAPE_CHAR):
                    return True, recv_buffer.replace(self.escaped, self.unescaped)
                else:
                    recv_buffer += c

            self.disconnect(sock)
        except socket.timeout:
            return False, "Error: socket timed out"

    @staticmethod
    def construct_command(device, command, args):
        return device + "->" + command + "(" + ", ".join(map(str, args)) + ")"

    @staticmethod
    def disconnect(sock):
        sock.close()
