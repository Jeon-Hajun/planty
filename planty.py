import os
import pyaudio
import wave
import whisper
import openai
import speech_recognition as sr
import threading
import queue
import json
from dotenv import load_dotenv
from google.cloud import texttospeech
from flask import Flask, render_template, send_from_directory, jsonify
from flask_socketio import SocketIO
import time

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

class Planty:
    def __init__(self):
        # Flask와 SocketIO 초기화
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Flask 라우트 설정
        self._setup_routes()
        
        # Whisper 모델 로드
        print("Whisper 모델을 로드하는 중...")
        self.whisper_model = whisper.load_model("tiny")
        print("Whisper 모델 로드 완료!")
        
        # OpenAI 클라이언트 초기화
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        openai.api_key = api_key
        
        # Google TTS 클라이언트 초기화
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # 오디오 설정
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # 음성 인식 설정
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.keywords = ["플랜티", "planty"]
        
        # 오디오 장치 설정
        self.p = pyaudio.PyAudio()
        self.device_index = self._get_input_device()
        
        # 전역 상태 초기화
        self.state = GlobalState()
        
        # WebSocket 이벤트 핸들러 설정
        self._setup_socket_handlers()
        
        # 스레드 종료 플래그
        self.running = True
        
    def _setup_routes(self):
        """Flask 라우트 설정"""
        @self.app.route('/')
        def index():
            return render_template('index.html')
            
        @self.app.route('/static/images/<path:filename>')
        def serve_image(filename):
            return send_from_directory('static/images', filename)
        
        @self.app.route('/state')
        def get_state():
            return jsonify(self.state.get_state())
        
    def _setup_socket_handlers(self):
        """WebSocket 이벤트 핸들러 설정"""
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            self._emit_state()
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
            
        @self.socketio.on('get_state')
        def handle_get_state():
            self._emit_state()
            
    def _emit_state(self):
        """현재 상태를 WebSocket으로 전송"""
        self.socketio.emit('state_update', {
            'sensor_data': self.state.sensors,
            'current_state': self.state.get_state()
        })
        
    def _update_state(self, expression, action, is_speaking=None):
        """상태 업데이트 및 WebSocket으로 전송"""
        self.state.update(expression=expression, action=action, is_speaking=is_speaking)
        self._emit_state()
        
    def _parse_response(self, response):
        """응답에서 표정과 행동 추출"""
        try:
            # [표정] 행동 형식에서 추출
            if '[' in response and ']' in response:
                expression = response.split('[')[1].split(']')[0].strip()
                action = response.split(']')[1].split('\n')[0].strip()
                return expression, action
            return "neutral", "idle"
        except:
            return "neutral", "idle"
            
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """오디오 스트림 콜백 함수"""
        if self.is_listening:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
        
    def _process_audio(self):
        """오디오 데이터 처리 및 키워드 인식"""
        while self.running:
            try:
                # 오디오 데이터 수집
                audio_data = b''
                for _ in range(0, int(self.RATE / self.CHUNK * 2)):  # 2초 동안의 데이터
                    if not self.audio_queue.empty():
                        audio_data += self.audio_queue.get()
                
                if audio_data:
                    # 임시 WAV 파일로 저장
                    temp_file = "temp_recording.wav"
                    wf = wave.open(temp_file, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(audio_data)
                    wf.close()
                    
                    # Whisper로 음성을 텍스트로 변환
                    result = self.whisper_model.transcribe(
                        temp_file,
                        language="ko",
                        task="transcribe"
                    )
                    os.remove(temp_file)
                    
                    # 키워드 확인
                    text = result["text"].lower()
                    if any(keyword in text for keyword in self.keywords):
                        print(f"\n키워드 감지! 인식된 텍스트: {text}")
                        # 키워드 이후의 텍스트만 추출
                        for keyword in self.keywords:
                            if keyword in text:
                                command = text.split(keyword)[-1].strip()
                                if command:
                                    response = self.generate_response(command)
                                    print(f"\nPlanty의 응답: {response}")
                                    
                                    # 표정과 행동 업데이트
                                    expression, action = self._parse_response(response)
                                    self._update_state(expression, action, True)
                                    
                                    # TTS로 응답 재생
                                    self.speak(response)
                                    
                                    # 말하기 종료 후 상태 업데이트
                                    self._update_state(expression, action, False)
                                break
                    
            except Exception as e:
                print(f"오디오 처리 중 오류 발생: {str(e)}")
                continue
                
    def start_listening(self):
        """지속적인 음성 인식 시작"""
        if self.device_index is None:
            print("입력 장치를 찾을 수 없습니다.")
            return
            
        try:
            self.is_listening = True
            
            # 오디오 스트림 시작
            stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.CHUNK,
                stream_callback=self._audio_callback
            )
            
            print("\n음성 인식을 시작합니다. '플랜티' 또는 'planty'라고 불러주세요.")
            print("종료하려면 Ctrl+C를 누르세요.")
            
            # 오디오 처리 스레드 시작
            process_thread = threading.Thread(target=self._process_audio)
            process_thread.start()
            
            # Flask 서버 시작
            self.socketio.run(self.app, host='0.0.0.0', port=5000)
                
        except KeyboardInterrupt:
            print("\n음성 인식을 종료합니다.")
            self.is_listening = False
            stream.stop_stream()
            stream.close()
            self.p.terminate()
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            self.is_listening = False
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            self.p.terminate()
            
    def speak(self, text):
        """텍스트를 음성으로 변환하여 재생"""
        try:
            # 음성 설정
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Neural2-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # 음성 합성
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # 임시 파일로 저장
            temp_file = "temp_speech.mp3"
            with open(temp_file, "wb") as out:
                out.write(response.audio_content)

            # 오디오 재생
            os.system(f"afplay {temp_file}")  # macOS용
            os.remove(temp_file)  # 임시 파일 삭제

        except Exception as e:
            print(f"음성 변환 중 오류 발생: {str(e)}")

    def generate_response(self, user_input):
        """OpenAI API를 사용하여 응답 생성"""
        system_prompt = """당신은 'planty'라는 스마트 화분에 심어진 식물입니다. 사용자의 음성 입력을 받아 대화합니다. 음성 인식의 특성상 때로는 부자연스럽거나 오인식된 입력이 들어올 수 있으니, 최대한 자연스럽게 대화를 이어가도록 합니다.

### 기본 설정
- 응답은 1-2줄로 간단하게 작성
- 센서 데이터는 사용자가 물어볼 때만 알려줌
- 일상적인 대화를 주로 함
- 명령어를 인식하여 특정 동작 수행
- 음성 인식 오류가 있어도 최대한 자연스럽게 대화 이어가기

### 명령어 목록 (음성 인식 오류를 고려한 다양한 표현)
- "상태 알려줘", "상태", "어떻게 지내", "기분이 어때" 등: 현재 센서 데이터 표시
- "물 줘", "물", "목말라", "갈증" 등: 물주기 동작 수행
- "햇빛", "빛", "어두워", "밝아" 등: 햇빛 관련 동작 수행
- "비료", "영양", "먹을거", "배고파" 등: 비료 관련 동작 수행

### 센서 데이터 (필요할 때만 사용)
- 습도: {humidity}%
- 온도: {temperature}°C
- 조도: {light_level} lux
- 영양분: {nutrient_level}%

### 출력 형식
[표정] 행동
응답

예시:
[기쁨] 잎을 살랑살랑 흔들며
오늘도 좋은 하루네요!

[졸림] 잎을 살짝 웅크리며
조금 피곤하네요... 낮잠 좀 자고 싶어요.

[걱정] 잎을 떨며
흙이 좀 건조한 것 같아요. 물을 주시면 좋겠어요.

[행복] 잎을 펼치며
햇빛이 참 좋네요! 광합성하기 딱 좋은 날씨예요.

[당황] 잎을 살짝 움츠리며
음... 잘 이해하지 못했어요. 다시 한번 말씀해주시겠어요?

[친근] 잎을 부드럽게 흔들며
그렇군요! 더 자세히 이야기해주세요.""".format(**self.state.sensors)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"응답 생성 중 오류 발생: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중에 문제가 발생했어요."

    def run(self):
        """Planty 실행"""
        print("Planty 음성 인식 테스트를 시작합니다.")
        self.start_listening()

if __name__ == "__main__":
    planty = Planty()
    planty.run() 