import TCP


CRLF = '\r\n'
B_CRLF = b'\r\n'
FTP_PORT = 21

#  Server response Codes
USER_LOGIN_SUCCESS_CODE = 230
ENTERING_PASV_MODE_CODE = 227


class FTPclient:

    def __init__(self, ftp_server, user='', password=''):
        self._ftp_server = ftp_server
        self._user = user
        self._data_port = None
        self._tcp_data = None
        # self._password = password // We should probably not store user passwords
        self._tcp_cmd = TCP.TCP(self._ftp_server, FTP_PORT)
        self._welcome_msg = self._tcp_cmd.receive()
        print(self._welcome_msg)
        self.login(self._user, password)

    def login(self, user, password):
        self._tcp_cmd.transmit('USER' + user + CRLF)
        server_resp = self._tcp_cmd.receive()
        self._tcp_cmd.transmit('PASS' + password + CRLF)
        s = self._tcp_cmd.receive(8192)
        print(server_resp)
        if USER_LOGIN_SUCCESS_CODE == self.whatIsTheCode(server_resp):
            return True

        return False

    def whatIsTheCode(self, message):
        code = message[:3]
        return int(code)

    def quit(self):
        self._tcp_cmd.transmit('QUIT' + CRLF)
        server_resp = self._tcp_cmd.receive()
        print(server_resp)

    def pasv(self):
        self._tcp_cmd.transmit('PASV' + CRLF)
        server_resp = self._tcp_cmd.receive(8192)

        server_ip, self._data_port = self.pasvModeStringHandling(server_resp)
        self._tcp_data = TCP.TCP(self._ftp_server, self._data_port)
        return self._tcp_data

    def list(self):
        self._tcp_cmd.transmit('LIST' + CRLF)
        print(self._tcp_cmd.receive())
        print(self._tcp_data.receive())

    def retr(self, path):
        self._tcp_cmd.transmit('RETR' + ' ' + path + CRLF)
        print(self._tcp_cmd.receive())
        x = self._tcp_data.receive()
        f = open('Photo.scr', "w+")
        f.write(x)
        f.close()

    def pwm(self):
        self._tcp_cmd.transmit(CRLF)
        print(self._tcp_data.receive())

    def cwd(self, path):
        self._tcp_cmd.transmit('CWD' + ' ' + path + CRLF)
        print(self._tcp_cmd.receive())

    def pasvModeStringHandling(self, server_resp):

        if ENTERING_PASV_MODE_CODE != self.whatIsTheCode(server_resp):
            return "Server did Not Respond"

        start_of_ip = server_resp.find('(')
        server_resp = server_resp[start_of_ip+1:-3]
        server_resp = server_resp.split(',')

        # Retrieving IP from the server response
        # deliminating the IP by dot so as to get 192.134...
        temp = ''
        for i in range(0, 4):
            temp = temp + (server_resp[i]) + '.'

        server_ip = temp + server_resp[3]
        # Retrieving Port Number client must listen to
        server_resp_port = server_resp[-2:]
        # Formula to calculate port number
        self._data_port = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))
        print('Data Connection with IP: ' + server_ip + ':' + str(self._data_port))
        return server_ip, self._data_port


# Testing the class works with an open ftp server
if __name__ == '__main__':
    client = FTPclient('ftp.mirror.ac.za')
    client.pasv()
    client.list()

    path = input('Please enter file path: ')
    client.cwd(path)
    client.list()

    # client.retr(path)
    # client.pwm()
    client.quit()
