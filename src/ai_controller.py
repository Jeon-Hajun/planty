import os
import pyaudio
import wave
import whisper
import openai
import speech_recognition as sr
import threading
import queue
from dotenv import load_dotenv
from google.cloud import texttospeech

class AIController:
    def __init__(self, state):
        self.state = state
        self.running = True
        
        # 오디오 설정
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Whisper 모델 로드
        self.model = whisper.load_model("base")
        
        # OpenAI API 키 설정
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # 오디오 큐 초기화
        self.audio_queue = queue.Queue()
    
    def _get_gpt_response(self, text):
        """GPT 응답 생성"""
        # TODO: 실제 GPT 응답 생성 구현
        return "안녕하세요! 저는 Planty입니다."
    
    def _parse_response(self, response):
        """응답에서 표정과 행동 추출"""
        # TODO: 실제 응답 파싱 구현
        return "neutral", "idle"
    
    def _speak(self, text):
        """TTS로 음성 출력"""
        # TODO: 실제 TTS 구현
        pass
    
    def _process_audio(self):
        """오디오 처리 스레드"""
        while self.running:
            try:
                # 오디오 데이터 처리
                audio_data = self.audio_queue.get(timeout=1)
                if audio_data:
                    # Whisper로 음성 인식
                    result = self.model.transcribe(audio_data)
                    text = result["text"]
                    
                    # 키워드 감지
                    if "플랜티" in text.lower() or "planty" in text.lower():
                        # GPT 응답 생성
                        response = self._get_gpt_response(text)
                        
                        # 표정과 행동 추출
                        expression, action = self._parse_response(response)
                        
                        # 상태 업데이트
                        self.state.update(expression=expression, action=action, is_speaking=True)
                        
                        # TTS로 음성 출력
                        self._speak(response)
                        
                        # 상태 업데이트
                        self.state.update(is_speaking=False)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"오디오 처리 중 오류 발생: {e}")
    
    def run(self):
        """AI 컨트롤러 실행"""
        # 오디오 처리 스레드 시작
        process_thread = threading.Thread(target=self._process_audio)
        process_thread.start()
    
    def stop(self):
        """AI 컨트롤러 종료"""
        self.running = False 