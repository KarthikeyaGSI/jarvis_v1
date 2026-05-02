"""
Marketingkolabs Premium API Server
Serves the premium UI and provides API endpoints for voice control
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from pathlib import Path
import sys
import logging
import json
from threading import Thread
import time

sys.path.insert(0, str(Path(__file__).parent))

from autonomous_agent import AutonomousAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='static')
app.config['SECRET_KEY'] = 'marketingkolabs-premium'
socketio = SocketIO(app, cors_allowed_origins="*")

agent = None
agent_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    if agent:
        return jsonify({
            'status': 'active' if agent.is_running else 'stopped',
            'voice_mode': agent.voice_mode,
            'personality': agent.voice_personality,
            'gamification': agent.get_gamification_status() if hasattr(agent, 'get_gamification_status') else {}
        })
    return jsonify({'status': 'not_initialized'})

@app.route('/api/personality', methods=['POST'])
def set_personality():
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 400

    data = request.json
    name = data.get('personality', 'default')

    result = agent.switch_personality(name)
    return jsonify(result)

@app.route('/api/command', methods=['POST'])
def process_command():
    if not agent:
        return jsonify({'error': 'Agent not initialized'}), 400

    data = request.json
    text = data.get('command', '')

    if not text:
        return jsonify({'error': 'No command provided'}), 400

    result = agent._process_voice_command(text)
    return jsonify(result)

@app.route('/api/start', methods=['POST'])
def start_agent():
    global agent, agent_thread

    if agent and agent.is_running:
        return jsonify({'message': 'Agent already running'})

    try:
        agent = AutonomousAgent()
        agent_thread = Thread(target=agent.start, daemon=True)
        agent_thread.start()
        return jsonify({'message': 'Agent started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_agent():
    global agent
    if agent:
        agent.stop()
        return jsonify({'message': 'Agent stopped'})
    return jsonify({'error': 'Agent not running'}), 400

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('status', {'status': 'connected'})

@socketio.on('voice_command')
def handle_voice_command(data):
    if not agent:
        emit('response', {'error': 'Agent not initialized'})
        return

    text = data.get('text', '')
    if text:
        result = agent._process_voice_command(text)
        emit('response', result)

def start_server():
    """Start the API server"""
    logger.info("Starting Marketingkolabs Premium UI Server...")
    socketio.run(app, host='0.0.0.0', port=3000, debug=False)

if __name__ == '__main__':
    logger.info("Marketingkolabs Premium - Starting...")
    start_server()
