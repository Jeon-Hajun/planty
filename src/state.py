class GlobalState:
    def __init__(self):
        self.is_speaking = False
        self.is_listening = False
        
    def get_sensor_data(self):
        """현재 센서 데이터를 반환합니다."""
        return {
            'temperature': 25.0,  # 기본 온도 25도
            'humidity': 60.0,     # 기본 습도 60%
            'soil_moisture': 70.0, # 기본 토양 수분 70%
            'light': 500.0        # 기본 조도 500lux
        } 