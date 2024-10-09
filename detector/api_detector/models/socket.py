import socketio
import os
from dotenv import load_dotenv

load_dotenv()

sio = socketio.SimpleClient()
    
def start():
    print('starting socket connection with host ' + os.getenv('SOCKET_HOST') + ' and port ' + os.getenv('SOCKET_PORT'))
    sio.connect('http://' + os.getenv('SOCKET_HOST') + ':' + os.getenv('SOCKET_PORT'))
    print('connection established')
    
def emit(event, data):
    sio.emit(event, data)
    print(f'event {event} emitted with data {data}')