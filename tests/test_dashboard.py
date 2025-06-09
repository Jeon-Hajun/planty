import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# sys.path.insert를 사용하여 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dashboard import Dashboard
from main import GlobalState

class TestDashboard(unittest.TestCase):

    def setUp(self):
        self.state = GlobalState()
        self.dashboard = Dashboard(self.state)
        self.app = self.dashboard.app.test_client()
        self.app.testing = True

    def test_index_route(self):
        # 루트 경로가 올바르게 렌더링되는지 테스트
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data) # HTML 문서임을 확인
        self.assertIn(b'Planty Sensor Data', response.data) # 대시보드 제목 확인

    def test_get_state_route(self):
        # /state 경로가 올바른 JSON 데이터를 반환하는지 테스트
        # GlobalState의 초기 상태를 가정
        expected_state = {
            'expression': 'neutral',
            'action': 'idle',
            'is_speaking': False,
            'sensors': {
                'humidity': 0,
                'temperature': 0,
                'light': 0,
                'nutrients': 0
            }
        }
        
        response = self.app.get('/state')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_state)

        # 상태 업데이트 후 다시 테스트
        self.state.update_state("happy", "watering", True)
        self.state.update_sensors(humidity=70, temperature=26, light=1200, nutrients=75)
        
        updated_expected_state = {
            'expression': 'happy',
            'action': 'watering',
            'is_speaking': True,
            'sensors': {
                'humidity': 70,
                'temperature': 26,
                'light': 1200,
                'nutrients': 75
            }
        }
        
        response = self.app.get('/state')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, updated_expected_state)

if __name__ == '__main__':
    unittest.main() 