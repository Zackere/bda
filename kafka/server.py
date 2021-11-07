from sys import argv
from http.server import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode('utf-8')
        print(post_body)


def main(port):
    HTTPServer(('', port), RequestHandler).serve_forever()


if __name__ == '__main__':
    main(argv[1] if len(argv) > 1 else 20200)
