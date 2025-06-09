import threading
import time
from circuit_controller import CircuitController
from dashboard import Dashboard
from ai_controller import AIController

class GlobalState:
    def __init__(self):
        self.lock = threading.Lock()
        self.expression = 'neutral'
        self.action = 'idle'
        self.is_speaking = False
        self.sensors = {
            'humidity': 0,
            'temperature': 0,
            'light': 0,
            'nutrients': 0
        }
        self.last_update = time.time()
    
    def update(self, expression=None, action=None, is_speaking=None, sensors=None):
        with self.lock:
            if expression is not None:
                self.expression = expression
            if action is not None:
                self.action = action
            if is_speaking is not None:
                self.is_speaking = is_speaking
            if sensors is not None:
                self.sensors.update(sensors)
            self.last_update = time.time()
    
    def get_state(self):
        with self.lock:
            return {
                'expression': self.expression,
                'action': self.action,
                'is_speaking': self.is_speaking,
                'sensors': self.sensors,
                'last_update': self.last_update
            }

def main():
    # 전역 상태 초기화
    state = GlobalState()
    
    # 컨트롤러 초기화
    circuit = CircuitController(state)
    dashboard = Dashboard(state)
    ai = AIController(state)
    
    try:
        # AI 컨트롤러 실행
        ai.run()
        
        # 회로 제어 스레드 시작
        circuit_thread = threading.Thread(target=circuit.run)
        circuit_thread.start()
        
        # 대시보드 실행 (메인 스레드)
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
        ai.stop()
        circuit.stop()
        circuit_thread.join()
        print("프로그램이 종료되었습니다.")

if __name__ == "__main__":
    main() 