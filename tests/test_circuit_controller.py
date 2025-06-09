import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# sys.path.insert를 사용하여 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from circuit_controller import CircuitController
from main import GlobalState

class TestCircuitController(unittest.TestCase):

    def setUp(self):
        self.state = GlobalState()
        self.circuit_controller = CircuitController(self.state)

    def test_read_humidity(self):
        # _read_humidity 메서드가 올바른 값을 반환하는지 테스트
        # 실제 센서 연동이 아니므로, 하드코딩된 값(60)을 기대합니다.
        self.assertEqual(self.circuit_controller._read_humidity(), 60)

    def test_read_temperature(self):
        # _read_temperature 메서드가 올바른 값을 반환하는지 테스트
        self.assertEqual(self.circuit_controller._read_temperature(), 25)

    def test_read_light(self):
        # _read_light 메서드가 올바른 값을 반환하는지 테스트
        self.assertEqual(self.circuit_controller._read_light(), 1000)

    def test_read_nutrients(self):
        # _read_nutrients 메서드가 올바른 값을 반환하는지 테스트
        self.assertEqual(self.circuit_controller._read_nutrients(), 70)

    @patch('circuit_controller.time.sleep', return_value=None) # sleep 모킹
    def test_run_and_stop(self, mock_sleep):
        # run 메서드가 스레드에서 제대로 실행되고 멈추는지 테스트
        import threading
        
        # run 메서드를 별도의 스레드에서 실행
        thread = threading.Thread(target=self.circuit_controller.run)
        thread.start()

        # 잠시 기다려 스레드가 실행되도록 함
        time.sleep(0.1)

        # running 상태가 True인지 확인
        self.assertTrue(self.circuit_controller.running)

        # stop 메서드 호출
        self.circuit_controller.stop()

        # 스레드가 종료될 때까지 기다림
        thread.join(timeout=1) # 타임아웃 설정

        # running 상태가 False인지 확인
        self.assertFalse(self.circuit_controller.running)
        self.assertFalse(thread.is_alive()) # 스레드가 종료되었는지 확인

if __name__ == '__main__':
    unittest.main() 