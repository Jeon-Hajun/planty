import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# sys.path.insert를 사용하여 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ai_controller import AIController
from main import GlobalState # GlobalState는 ai_controller에 필요한 의존성

class TestAIController(unittest.TestCase):

    def setUp(self):
        # 환경 변수 모킹 (실제 API 키 필요 없이 테스트 실행)
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'test_credentials.json'

        # GlobalState 인스턴스 생성
        self.state = GlobalState()
        
        # AIController 초기화
        # PyAudio, Whisper, OpenAI, Google Cloud TTS 등 실제 의존성 모킹
        with patch('ai_controller.pyaudio.PyAudio'), \
             patch('ai_controller.whisper.load_model', return_value=MagicMock()), \
             patch('ai_controller.openai.OpenAI'), \
             patch('ai_controller.texttospeech.TextToSpeechClient'):
            self.ai_controller = AIController(self.state)

    def tearDown(self):
        # 테스트 후 환경 변수 정리
        del os.environ['OPENAI_API_KEY']
        del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    @patch('ai_controller.speech_recognition.Recognizer')
    def test_process_audio_keyword_detection(self, MockRecognizer):
        # Recognizer 인스턴스 모킹
        mock_recognizer_instance = MockRecognizer.return_value
        # recognize_google_cloud 또는 transcribe 메서드 모킹
        mock_recognizer_instance.listen.return_value = MagicMock()
        mock_recognizer_instance.recognize_whisper.return_value = "플랜티 안녕"

        # _get_gpt_response와 _speak 메서드 모킹
        with patch.object(self.ai_controller, '_get_gpt_response', return_value="안녕하세요!") as mock_gpt_response, \
             patch.object(self.ai_controller, '_speak') as mock_speak:
            
            # _process_audio 호출
            self.ai_controller._process_audio(MagicMock(), MagicMock(), MagicMock()) # stream, frame_count, time_info, status는 모킹

            # '플랜티' 키워드가 감지되었으므로 _get_gpt_response와 _speak가 호출되었는지 확인
            mock_gpt_response.assert_called_once()
            mock_speak.assert_called_once_with("안녕하세요!")
            
            # GlobalState의 expression 및 action이 업데이트되었는지 확인
            self.assertEqual(self.state.get_expression(), "neutral")
            self.assertEqual(self.state.get_action(), "speaking")

    @patch('ai_controller.speech_recognition.Recognizer')
    def test_process_audio_no_keyword(self, MockRecognizer):
        mock_recognizer_instance = MockRecognizer.return_value
        mock_recognizer_instance.listen.return_value = MagicMock()
        mock_recognizer_instance.recognize_whisper.return_value = "그냥 평범한 대화"

        with patch.object(self.ai_controller, '_get_gpt_response') as mock_gpt_response, \
             patch.object(self.ai_controller, '_speak') as mock_speak:
            
            self.ai_controller._process_audio(MagicMock(), MagicMock(), MagicMock())

            # 키워드가 없으므로 _get_gpt_response와 _speak가 호출되지 않았는지 확인
            mock_gpt_response.assert_not_called()
            mock_speak.assert_not_called()
            
            # GlobalState의 expression 및 action이 변경되지 않았는지 확인
            self.assertEqual(self.state.get_expression(), "neutral") # 기본값 유지
            self.assertEqual(self.state.get_action(), "idle") # 기본값 유지

    def test_get_gpt_response(self):
        # _get_gpt_response 메서드가 올바른 GPT 응답을 생성하는지 테스트
        # OpenAI API 호출을 모의합니다.
        with patch('openai.resources.chat.completions.Completions.create') as mock_create:
            mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="테스트 응답입니다."))])
            
            response = self.ai_controller._get_gpt_response("안녕, 플랜티")
            self.assertEqual(response, "테스트 응답입니다.")
            mock_create.assert_called_once() # GPT 호출이 발생했는지 확인

    def test_parse_response(self):
        # _parse_response 메서드가 응답을 올바르게 파싱하는지 테스트
        # 긍정적인 응답
        expression, action = self.ai_controller._parse_response("식물이 건강하네요! 물을 주세요.")
        self.assertEqual(expression, "happy")
        self.assertEqual(action, "watering")

        # 부정적인 응답
        expression, action = self.ai_controller._parse_response("식물이 시들고 있어요. 영양분이 부족합니다.")
        self.assertEqual(expression, "sad")
        self.assertEqual(action, "fertilizing")

        # 중립적인 응답
        expression, action = self.ai_controller._parse_response("오늘 날씨는 좋습니다.")
        self.assertEqual(expression, "neutral")
        self.assertEqual(action, "idle")
        
        # 알 수 없는 응답 (기본값 확인)
        expression, action = self.ai_controller._parse_response("이건 무슨 말이지?")
        self.assertEqual(expression, "neutral")
        self.assertEqual(action, "idle")

    def test_speak(self):
        # _speak 메서드가 TTS를 호출하고 오디오를 재생하는지 테스트
        # Google Cloud TTS 클라이언트 및 PyAudio 관련 모듈을 모의합니다.
        with patch('ai_controller.texttospeech.TextToSpeechClient.synthesize_speech') as mock_synthesize:
            with patch('ai_controller.pyaudio.PyAudio') as mock_pyaudio:
                with patch('ai_controller.wave.open') as mock_wave_open:
                    with patch('ai_controller.os.remove') as mock_os_remove:

                        # synthesize_speech의 반환값 모의
                        mock_synthesize.return_value = MagicMock(audio_content=b"mock_audio_data")

                        # PyAudio 스트림 관련 모의
                        mock_stream = MagicMock()
                        mock_pyaudio.return_value.open.return_value = mock_stream

                        # wave.open의 반환값 모의
                        mock_wave_file = MagicMock()
                        mock_wave_file.getnchannels.return_value = 1
                        mock_wave_file.getsampwidth.return_value = 2
                        mock_wave_file.getframerate.return_value = 24000
                        mock_wave_file.readframes.return_value = b"mock_audio_frames" # readframes가 반환할 값 설정
                        mock_wave_open.return_value.__enter__.return_value = mock_wave_file

                        self.ai_controller._speak("테스트 스피치입니다.")

                        # synthesize_speech가 호출되었는지 확인
                        mock_synthesize.assert_called_once()
                        # PyAudio 스트림이 열리고 데이터가 기록되었는지 확인
                        mock_pyaudio.return_value.open.assert_called_once()
                        mock_stream.write.assert_called_once_with(b"mock_audio_frames") # 실제 write에 전달될 데이터로 변경
                        mock_stream.stop_stream.assert_called_once()
                        mock_stream.close.assert_called_once()
                        # 임시 파일이 삭제되었는지 확인
                        mock_os_remove.assert_called_once_with("temp_tts_output.wav")

if __name__ == '__main__':
    unittest.main() 