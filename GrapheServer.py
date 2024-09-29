#!/usr/bin/python3
# coding: utf-8
import http.server
import os.path
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
from graph_page import GraphParameters
from graph_page import GraphPage
from graph.graph_data import GraphDataBuilder

PORT = 8000


class MyHandler(http.server.BaseHTTPRequestHandler):
    graph_page = GraphPage()
    data_builder = GraphDataBuilder()


    @staticmethod
    def parse_parameters(url: str) -> GraphParameters:
        parameters = GraphParameters()
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        parameters.node = params['node'][0] if 'node' in params else ''
        parameters.edges = params['edges'] if 'edges' in params else []
        parameters.distance = params['distance'][0] if 'distance' in params else ''
        return parameters

    def do_GET(self):
        """Serve a GET request."""

        path = urlparse(self.path).path

        if path == '/':
            self.serve_graph_page()
        if path == '/graph_data':
            self.serve_graph_data()
        else:
            self.serve_site_file(path[1:])

    def serve_site_file(self, path: str) -> None:
        file_path = './site/' + path
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('404 : File not found'.encode('utf-8'))

    def serve_graph_data(self) -> None:
        parameters = self.parse_parameters(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=UTF-8')
        self.end_headers()
        self.wfile.write(self.data_builder.build_graph_data(parameters).encode('utf-8'))

    def serve_graph_page(self) -> None:
        parameters = self.parse_parameters(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()
        self.wfile.write(self.graph_page.build_graph_page(parameters))


with socketserver.TCPServer(("", PORT),  MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
