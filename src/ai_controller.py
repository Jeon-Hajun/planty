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
from pydub import AudioSegment
import tempfile
from google.cloud import speech
import re

class AIController:
    def __init__(self, state):
        """AI 컨트롤러 초기화"""
        # 환경 변수 로드
        load_dotenv()
        
        # OpenAI API 키 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # Google Speech-to-Text 클라이언트 초기화
        self.speech_client = speech.SpeechClient()
        
        # 상태 관리
        self.state = state
        
        # 실행 상태
        self.running = True
        
        # 오디오 설정
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # PyAudio 초기화
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # 출력용 스트림 초기화
        self.output_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Whisper 모델 로드
        self.whisper_model = whisper.load_model("tiny")
        
        # 오디오 큐 초기화
        self.audio_queue = queue.Queue()
        
        # 음성 인식기 초기화
        self.recognizer = sr.Recognizer()
   
    def _get_gpt_response(self, text):
        """GPT를 사용하여 응답을 생성합니다."""
        try:
            print("\n[GPT] 응답 생성 중...")
            
            # GPT API 호출
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """당신은 Planty라는 AI 식물 친구입니다. 
                    친근하고 자연스럽게 대화하세요.
                    응답은 반드시 한국어로 해주세요.
                    응답의 마지막에는 [표정]을 표시해주세요.
                    표정은 다음 중 하나여야 합니다: happy, worried, sleepy, excited, thinking, neutral"""},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            # 응답 추출
            gpt_response = response.choices[0].message.content
            print(f"[GPT] 응답 생성 완료: {gpt_response}")
            
            return gpt_response
            
        except Exception as e:
            print(f"[GPT] 오류 발생: {str(e)}")
            return "죄송합니다. 지금은 대화하기 어려운 것 같아요. [neutral]"
    
    def _parse_response(self, response):
        """GPT 응답에서 표정을 추출합니다."""
        try:
            # [표정] 형식 찾기
            match = re.search(r'\[(happy|worried|sleepy|excited|thinking|neutral)\]', response)
            if match:
                expression = match.group(1)
            else:
                expression = "neutral"
            
            return expression, None  # 행동은 더 이상 사용하지 않음
            
        except Exception as e:
            print(f"응답 파싱 중 오류 발생: {str(e)}")
            return "neutral", None
    
    def _speak(self, text):
        """TTS로 음성을 출력합니다."""
        try:
            print("\n[TTS] 음성 합성 중...")
            
            # TTS 요청 설정
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Neural2-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # TTS 요청
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(response.audio_content)
                temp_file_path = temp_file.name
            
            print("[TTS] 음성 출력 중...")
            # 음성 재생
            os.system(f"mpg123 -q {temp_file_path}")
            
            # 임시 파일 삭제
            os.unlink(temp_file_path)
            print("[TTS] 음성 출력 완료")
            
        except Exception as e:
            print(f"[TTS] 오류 발생: {e}")
    
    def _process_audio(self, audio_data):
        """오디오 데이터를 처리하고 음성을 인식합니다."""
        try:
            print("\n[음성 인식] 오디오 데이터 처리 중...")
            
            # 오디오 데이터를 WAV 형식으로 변환
            audio_segment = AudioSegment(
                audio_data,
                sample_width=2,
                frame_rate=16000,
                channels=1
            )
            
            # 임시 WAV 파일로 저장
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio_segment.export(temp_file.name, format='wav')
                temp_file_path = temp_file.name
            
            # Google Speech-to-Text로 음성 인식
            with open(temp_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='ko-KR',
                model='latest_long',
                use_enhanced=True,
                enable_automatic_punctuation=True,
                enable_spoken_punctuation=True,
                enable_spoken_emojis=True
            )
            
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # 임시 파일 삭제
            os.unlink(temp_file_path)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                print(f"[음성 인식] 인식된 텍스트: {transcript}")
                return transcript
            
            print("[음성 인식] 인식된 텍스트 없음")
            return None
            
        except Exception as e:
            print(f"[음성 인식] 오류 발생: {str(e)}")
            return None

    def start_voice_recognition(self):
        """음성 인식을 시작합니다."""
        try:
            # 마이크 설정
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print("\n[시스템] 음성 인식 시작")
            
            while self.running:
                if not self.state.is_speaking:
                    print("\n[음성 인식] 5초 동안 음성 수집 중...")
                    frames = []
                    # 5초 동안 오디오 데이터 수집
                    for _ in range(0, int(RATE / CHUNK * 5)):
                        data = stream.read(CHUNK)
                        frames.append(data)
                    
                    # 수집된 오디오 데이터 처리
                    audio_data = b''.join(frames)
                    transcript = self._process_audio(audio_data)
                    
                    # 음성 인식 결과가 있고, 현재 말하고 있지 않을 때만 처리
                    if transcript and not self.state.is_speaking:
                        # 응답 생성
                        response = self._get_gpt_response(transcript)
                        
                        # 표정 추출
                        expression, _ = self._parse_response(response)
                        print(f"[표정] {expression}")
                        
                        # 상태 업데이트
                        self.state.update(expression=expression, is_speaking=True)
                        
                        # 음성 합성 및 재생
                        self._speak(response)
                        
                        # 상태 업데이트
                        self.state.update(is_speaking=False)
                
        except Exception as e:
            print(f"[시스템] 오류 발생: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("\n[시스템] 음성 인식 종료")
    
    def run(self):
        """AI 컨트롤러 실행"""
        # 오디오 처리 스레드 시작
        process_thread = threading.Thread(target=self.start_voice_recognition)
        process_thread.start()
    
    def stop(self):
        """AI 컨트롤러 종료"""
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.output_stream.stop_stream()
        self.output_stream.close()
        self.audio.terminate()