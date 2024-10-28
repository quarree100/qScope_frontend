from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO
import csv
import os
import webbrowser
from q100viz.settings.config import config

http_port = config['HTTP_SERVER_PORT']
websocket_port = config['UDP_SERVER_PORT']

app = Flask(__name__, static_folder='static', static_url_path='')
socketio = SocketIO(
    app, cors_allowed_origins=f"http://localhost:{websocket_port}"
    )


@socketio.on('connect')
def handle_connect():
    print("A client has connected.")


@socketio.on('message')
def handle_message(data):
    socketio.emit('message', data, broadcast=True)


@app.route('/')
def serve_static():
    return send_from_directory('static', 'index.html')

def init_server(http_port):
    print(f'HTTP Server started at http://localhost:{http_port}')
    # webbrowser.open(f'http://localhost:{http_port}')
    socketio.run(app, port=http_port)


if __name__ == '__main__':
    init_server(http_port)
