#! env python
import logging
import socket
import time

class EstimSocket:

    def __init__(self, address="127.0.0.1", port=8089, verbose=1, udp=False):
        self._address = address
        self._port = port
        level = logging.INFO
        if verbose <= 0 or verbose == "quiet":
            level = logging.ERROR
        elif verbose == 1 or verbose == "info":
            level = logging.INFO
        elif verbose >= 2 or verbose == "debug":
            level = logging.DEBUG
        logging.basicConfig(
            level=level, format='%(asctime)s | %(threadName)s: [%(module)s:%(funcName)s] %(levelname)s: %(message)s')
        self._udp = udp

    def open_socket(self):
        if self._udp:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.serversocket.bind(('', self._port))
        if not self._udp:
            self.serversocket.listen(1) # become a server socket
        
        if self._udp:
            logging.info(f"UDP Server started ({self._address}:{self._port})... waiting for data.")
            return None, None
        else:
            logging.info(f"TCP Server started ({self._address}:{self._port})... waiting for client to connect.")
            conn, addr = self.serversocket.accept()
            logging.info(f"New client {addr[0]} connected.")
            logging.info("Running loop.")
            return conn, addr

    def start_server(self, max_incoming=1, callbacks=[], on_close=None, drop_packets=False):

        # handles the TCP vs UDP socket
        conn, addr = self.open_socket()

        while True:

            if self._udp:
                buf, addr = self.serversocket.recvfrom(4096)
            else:
                buf = conn.recv(4096)

            if len(buf) > 0:

                logging.debug(f"Received {buf} from {addr[0]}.")

                # at this point we've recv'd a buffer (buf) that contains data
                # it may contain multiple lines of data, if our server is processing
                # slower than the send rate of the client. To account for this we 
                # split our buffer into lines, and run the callbacks sequentially
                # on those
                #print(type(buf))
                #print(buf.decode('utf-8'))
                #print(str.splitlines(buf.decode('utf-8')))
                buf = [buf.decode('utf-8')]
                if drop_packets:
                    # only use the very last packet that was sent (faster)
                    buf = buf[-1]

                for i, this_buf in enumerate(buf):
                    # run all callbacks on each line in sequence

                    for j, callback in enumerate(callbacks):
                        # callbacks must accept two arguments: the buffer
                        # that was sent, and the address of the device that
                        # sent it.
                        logging.debug(f"callback {j} of {len(callbacks)}...")
                        callback(this_buf, addr[0])

            else: # len(buf) <= 0
                logging.info("Client disconnected, will perform clean exit.")
                if on_close is not None:
                    logging.info("running cleanup...")
                    on_close()
                break

    def client_connect(self):
        self.clientsocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.clientsocket.connect( (self._address, self._port) )

    def client_send(self, buf):
        logging.debug(f"Sending {buf} to {self._address}")
        self.clientsocket.send(buf)


if __name__ == "__main__":

    import sys

    def echo_callback(buf, addr):
        print(f"Received {buf} from {addr}")

    server = EstimSocket(port=int(sys.argv[1]))
    server.start_server(callbacks=[echo_callback])

