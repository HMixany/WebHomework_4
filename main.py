import mimetypes
import urllib.parse
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path


BASE_DIR = Path()


class MyFramework(BaseHTTPRequestHandler):
    def do_GET(self):
        print(urllib.parse.urlparse(self.path))
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
        pass

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


def run_server():
    address = ('localhost', 8080)
    http_server = HTTPServer(address, MyFramework)
    try:
        server = Thread(target=http_server.serve_forever())
        server.start()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == '__main__':
    run_server()
