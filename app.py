from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

bunkers = {
    1: {
        'cabinets': {str(i): {'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]} for i in range(1, 27)},
        'stocker': {'status': 'unknown', 'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]},
        'agv': {'status': 'unknown', 'position': {'x': 0, 'y': 0}}
    },
    2: {
        'cabinets': {str(i): {'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]} for i in range(1, 27)},
        'stocker': {'status': 'unknown', 'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]},
        'agv': {'status': 'unknown', 'position': {'x': 0, 'y': 0}}
    }
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_data', bunkers)

@socketio.on('cabinet_update')
def handle_cabinet_update(data):
    bunker_id = data['bunker_id']
    cabinet_id = data['cabinet_id']
    bunkers[bunker_id]['cabinets'][str(cabinet_id)] = data['status']
    emit('update_data', bunkers, broadcast=True)

@socketio.on('agv_update')
def handle_agv_update(data):
    bunker_id = data['bunker_id']
    bunkers[bunker_id]['agv'] = data['status']
    emit('update_data', bunkers, broadcast=True)

@socketio.on('stocker_update')
def handle_stocker_update(data):
    bunker_id = data['bunker_id']
    bunkers[bunker_id]['stocker'] = data['status']
    emit('update_data', bunkers, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)