from sys import argv
from http.server import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode('utf-8')
        print('POST body:', post_body)

        self.send_response(200)
        self.end_headers()


def main():
    HTTPServer(('', 20200), RequestHandler).serve_forever()


if __name__ == '__main__':
    main()
