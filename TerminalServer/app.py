from flask import Flask, render_template, request
from flask_sockets import Sockets
from utility.myDocker import ClientHandler, DockerStreamThread
import conf

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/')
def index():
    return render_template('index.html')

@sockets.route('/echo/<containerId>')
def echo_socket(ws, containerId):
    temp = request.args.get("key")
    print(temp)
    dockerCli = ClientHandler(base_url=conf.DOCKER_HOST, timeout=30)
    terminalExecId = dockerCli.creatTerminalExec(containerId)
    terminalStream = dockerCli.startTerminalExec(terminalExecId)._sock

    terminalThread = DockerStreamThread(ws, terminalStream)
    terminalThread.start()

    while not ws.closed:
        message = ws.receive()
        if message is not None:
            terminalStream.send(bytes(message, encoding='utf-8'))

if __name__ == '__main__':
    from gevent import pywsgi 
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('172.16.240.2', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()