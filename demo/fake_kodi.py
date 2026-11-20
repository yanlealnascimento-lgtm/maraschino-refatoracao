import json
import sys

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

RESULTS = {
    'Player.GetActivePlayers': [{'type': 'video', 'playerid': 1}],
    'Application.GetProperties': {'version': {'major': 19, 'minor': 0}},
}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        request = json.loads(self.rfile.read(length).decode('utf-8'))
        method = request.get('method')
        print('KODI <- %s %s' % (method, json.dumps(request.get('params', {}))))
        sys.stdout.flush()

        body = json.dumps({
            'jsonrpc': '2.0',
            'id': request.get('id'),
            'result': RESULTS.get(method, 'OK'),
        }).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print('Fake Kodi listening on port %d' % port)
    sys.stdout.flush()
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
