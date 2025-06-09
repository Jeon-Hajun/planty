import threading
import time
from circuit_controller import CircuitController
from dashboard import Dashboard
from ai_controller import AIController
import os
from flask import Flask, render_template, jsonify, request
import logging

# Flask 로그 레벨 설정
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

class GlobalState:
    def __init__(self):
        self.lock = threading.Lock()
        self.expression = 'neutral'
        self.action = 'idle'
        self.is_speaking = False
        self.is_listening = False
        self.sensors = {
            'humidity': 0,
            'temperature': 0,
            'light': 0,
            'nutrients': 0
        }
        self.last_update = time.time()
    
    def update(self, expression=None, action=None, is_speaking=None, is_listening=None, sensors=None):
        with self.lock:
            if expression is not None:
                self.expression = expression
            if action is not None:
                self.action = action
            if is_speaking is not None:
                self.is_speaking = is_speaking
            if is_listening is not None:
                self.is_listening = is_listening
            if sensors is not None:
                self.sensors.update(sensors)
            self.last_update = time.time()
    
    def get_state(self):
        with self.lock:
            return {
                'expression': self.expression,
                'action': self.action,
                'is_speaking': self.is_speaking,
                'is_listening': self.is_listening,
                'sensors': self.sensors,
                'last_update': self.last_update
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_state')
def get_state():
    return jsonify(state.get_state())

@app.route('/toggle_led/<color>', methods=['POST'])
def toggle_led(color):
    state.toggle_led(color)
    return jsonify({'is_on': state.get_led_state(color)})

@app.route('/control_motor/<direction>', methods=['POST'])
def control_motor(direction):
    state.control_motor(direction)
    return jsonify({'status': 'success'})

def main():
    # 전역 상태 초기화
    state = GlobalState()
    
    # 컨트롤러 초기화
    circuit = CircuitController(state)
    dashboard = Dashboard(state)
    ai = AIController(state)
    
    try:
        # AI 컨트롤러 스레드 시작
        ai_thread = threading.Thread(target=ai.run)
        ai_thread.start()
        
        # 회로 제어 스레드 시작
        circuit_thread = threading.Thread(target=circuit.run)
        circuit_thread.start()
        
        # 대시보드 실행 (메인 스레드)
        print("웹 서버를 시작합니다...")
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
        ai.stop()
        circuit.stop()
        ai_thread.join()
        circuit_thread.join()
        print("프로그램이 종료되었습니다.")

if __name__ == "__main__":
    main() 