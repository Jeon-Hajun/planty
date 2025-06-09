import threading
import time

class CircuitController:
    def __init__(self, state):
        self.state = state
        self.running = True
    
    def _read_humidity(self):
        # TODO: 실제 센서에서 습도 읽기
        return 60
    
    def _read_temperature(self):
        # TODO: 실제 센서에서 온도 읽기
        return 25
    
    def _read_light(self):
        # TODO: 실제 센서에서 조도 읽기
        return 1000
    
    def _read_nutrients(self):
        # TODO: 실제 센서에서 영양분 읽기
        return 70
    
    def run(self):
        """회로 제어 스레드 실행"""
        while self.running:
            try:
                # 센서 데이터 읽기
                sensors = {
                    'humidity': self._read_humidity(),
                    'temperature': self._read_temperature(),
                    'light': self._read_light(),
                    'nutrients': self._read_nutrients()
                }
                
                # 상태 업데이트
                self.state.update(sensors=sensors)
                
                # 1초 대기
                time.sleep(1)
            except Exception as e:
                print(f"회로 제어 중 오류 발생: {e}")
    
    def stop(self):
        """회로 제어 스레드 종료"""
        self.running = False 