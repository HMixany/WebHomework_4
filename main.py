import json
import mimetypes
import urllib.parse
import logging
import socket
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_HOST = '0.0.0.0'
HTTP_PORT = 3000
SOCKET_HOST = 'localhost'
SOCKET_PORT = 5000


class MyFramework(BaseHTTPRequestHandler):
    def do_GET(self):
        # print(urllib.parse.urlparse(self.path))
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html('index.html')
            case "/message.html":
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', status_code=404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        # print(data)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def save_data_from_form(data):
    pars_data = urllib.parse.unquote_plus(data.decode())
    # print(pars_data)
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in pars_data.split('&')]}
        logging.info(f'{parse_dict}')
        existing_dict = {}
        if Path('storage/data.json').is_file():
            with open('storage/data.json', 'r', encoding='utf-8') as fh:
                existing_dict = json.load(fh)
                logging.info(f'{existing_dict}')

        key = str(datetime.now())
        existing_dict[key] = parse_dict

        with open('storage/data.json', 'w', encoding='utf-8') as file:
            json.dump(existing_dict, file, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)


def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    # server_socket.listen()
    logging.info('Starting socket server')
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f'Socket received {address}: {msg}')
            save_data_from_form(msg)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()


def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, MyFramework)
    try:
        logging.info('Starting http server')
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()
    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()
