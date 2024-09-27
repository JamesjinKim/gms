from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import random
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

bunkers = {
    1: {
        'cabinets': {str(i): {'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]} for i in range(1, 27)},
        'stocker': {'status': 'unknown', 'gas_tanks': [{'id': 1, 'status': 'full'}, {'id': 2, 'status': 'full'}]},
        'agv': {
            'status': 'idle',
            'position': {'x': 0, 'y': 0},
            'gas_tank': None,
            'path': []
        }
    },
    2: {
        'cabinets': {str(i): {'gas_tanks': [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]} for i in range(1, 27)},
        'stocker': {'status': 'unknown', 'gas_tanks': [{'id': 1, 'status': 'full'}, {'id': 2, 'status': 'full'}]},
        'agv': {
            'status': 'idle',
            'position': {'x': 0, 'y': 0},
            'gas_tank': None,
            'path': []
        }
    }
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    emit('update_data', bunkers)

@socketio.on('cabinet_update')
def handle_cabinet_update(data):
    try:
        logging.debug(f"Received cabinet update: {data}")
        bunker_id = data['bunker_id']
        cabinet_id = str(data['cabinet_id'])
        new_status = data['status']

        current_cabinet = bunkers[bunker_id]['cabinets'][cabinet_id]

        # 항상 2개의 gas_tank를 유지하도록 함
        updated_gas_tanks = [{'id': 1, 'status': 'unknown'}, {'id': 2, 'status': 'unknown'}]

        if 'gas_tanks' in new_status:
            for new_tank in new_status['gas_tanks']:
                if new_tank['id'] in [1, 2]:
                    updated_gas_tanks[new_tank['id'] - 1] = new_tank
        else:
            # 새로운 상태에 gas_tanks가 없으면 현재 상태를 유지
            for i in range(2):
                if i < len(current_cabinet.get('gas_tanks', [])):
                    updated_gas_tanks[i] = current_cabinet['gas_tanks'][i]

        new_status['gas_tanks'] = updated_gas_tanks
        current_cabinet.update(new_status)

        logging.info(f"Updated cabinet {cabinet_id} in bunker {bunker_id}: {current_cabinet}")
        emit('update_data', bunkers, broadcast=True)
    except Exception as e:
        logging.error(f"Error in cabinet_update: {str(e)}")
        emit('error', {'message': 'An error occurred while updating the cabinet'})

@socketio.on('agv_update')
def handle_agv_update(data):
    logging.debug(f"Received AGV update: {data}")
    bunker_id = data['bunker_id']
    bunkers[bunker_id]['agv'] = data['status']
    logging.info(f"Updated AGV in bunker {bunker_id}: {bunkers[bunker_id]['agv']}")
    emit('update_data', bunkers, broadcast=True)

@socketio.on('agv_move')
def handle_agv_move(data):
    logging.debug(f"Received AGV move: {data}")
    bunker_id = data['bunker_id']
    agv = bunkers[bunker_id]['agv']
    
    # AGV 이동 로직
    if agv['path']:
        next_position = agv['path'].pop(0)
        agv['position'] = next_position
    
    logging.info(f"Moved AGV in bunker {bunker_id}: {agv}")
    emit('update_data', bunkers, broadcast=True)

@socketio.on('agv_load_unload')
def handle_agv_load_unload(data):
    logging.debug(f"Received AGV load/unload: {data}")
    bunker_id = data['bunker_id']
    agv = bunkers[bunker_id]['agv']
    location = data['location']
    
    if location == 'stocker':
        # Stocker에서 가득 찬 gas_tank 로드
        if not agv['gas_tank'] and bunkers[bunker_id]['stocker']['gas_tanks']:
            agv['gas_tank'] = bunkers[bunker_id]['stocker']['gas_tanks'].pop(0)
            # 빈 가스통을 Stocker에 추가
            bunkers[bunker_id]['stocker']['gas_tanks'].append({'id': agv['gas_tank']['id'], 'status': 'empty'})
    elif location.startswith('cabinet'):
        cabinet_id = location.split('_')[1]
        cabinet = bunkers[bunker_id]['cabinets'][cabinet_id]
        
        # 사용된 gas_tank 언로드
        if agv['gas_tank'] and agv['gas_tank']['status'] == 'empty':
            cabinet['gas_tanks'] = [tank for tank in cabinet['gas_tanks'] if tank['status'] != 'empty']
            cabinet['gas_tanks'].append(agv['gas_tank'])
            agv['gas_tank'] = None
        
        # 새 gas_tank 로드
        if not agv['gas_tank'] and cabinet['gas_tanks']:
            agv['gas_tank'] = next((tank for tank in cabinet['gas_tanks'] if tank['status'] == 'full'), None)
            if agv['gas_tank']:
                cabinet['gas_tanks'].remove(agv['gas_tank'])

    logging.info(f"AGV load/unload in bunker {bunker_id} at {location}: AGV status: {agv}")    
    emit('update_data', bunkers, broadcast=True)

@socketio.on('stocker_update')
def handle_stocker_update(data):
    logging.debug(f"Received stocker update: {data}")
    bunker_id = data['bunker_id']
    bunkers[bunker_id]['stocker'] = data['status']
    logging.info(f"Updated stocker in bunker {bunker_id}: {bunkers[bunker_id]['stocker']}")
    emit('update_data', bunkers, broadcast=True)

# 주기적으로 전체 데이터 로깅
@socketio.on('request_full_data')
def handle_request_full_data():
    logging.debug(f"Full bunkers data: {json.dumps(bunkers, indent=2)}")
    emit('full_data', bunkers)

if __name__ == '__main__':
    socketio.run(app, debug=True)