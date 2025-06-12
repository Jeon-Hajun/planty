import os
import pyaudio
import wave
import openai
import threading
import queue
from dotenv import load_dotenv
from google.cloud import texttospeech
import tempfile
from google.cloud import speech
import re
import time
import pvporcupine
import struct

class AIController:
    def __init__(self, state):
        """AI 컨트롤러 초기화"""
        # 환경 변수 로드
        load_dotenv()
        
        # OpenAI API 키 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # Google Speech-to-Text 클라이언트 초기화 (일반 대화 인식용)
        self.speech_client = speech.SpeechClient()
        
        # Picovoice 초기화
        try:
            self.porcupine = pvporcupine.create(
                access_key=os.getenv('PICOVOICE_ACCESS_KEY'),
                keyword_paths=['models/planty.ppn']
            )
        except Exception as e:
            print(f"[초기화] Picovoice 초기화 실패: {str(e)}")
            raise
        
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
        
        # 오디오 큐 초기화
        self.audio_queue = queue.Queue()
        
    def _get_gpt_response(self, text):
        """GPT를 사용하여 응답을 생성합니다."""
        try:
            print("\n[GPT] 응답 생성 중...")
            
            # 현재 센서 데이터 가져오기
            sensor_data = self.state.sensors
            
            # GPT API 호출
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""당신은 Planty라는 AI 식물 친구입니다. 
                    친근하고 자연스럽게 대화하세요.
                    응답은 반드시 한 문장으로 해주세요.
                    응답의 마지막에는 [표정]을 표시해주세요.
                    표정은 다음 중 하나여야 합니다: happy, worried, sleepy, excited, thinking, neutral

                    현재 센서 데이터:
                    - 습도: {sensor_data['humidity']}%
                    - 온도: {sensor_data['temperature']}°C
                    - 조도: {sensor_data['light']} lux
                    - 영양분: {sensor_data['nutrients']}%

                    센서 데이터는 사용자가 물어볼 때만 언급하세요.
                    일상적인 대화에서는 센서 데이터를 언급하지 않아도 됩니다."""},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=100
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
    
    def _process_gpt_response(self, response):
        """GPT 응답을 처리하고 TTS로 변환합니다."""
        try:
            # 표정 추출
            emotion_match = re.search(r'\[(.*?)\]$', response)
            if emotion_match:
                emotion = emotion_match.group(1)
                # 표정 제외한 텍스트 추출
                text = response[:emotion_match.start()].strip()
            else:
                emotion = "neutral"
                text = response

            # TTS 변환
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
            
            # 음성 재생
            print("[TTS] 음성 재생 중...")
            os.system(f"mpg123 -q {temp_file_path}")
            
            # 임시 파일 삭제
            os.unlink(temp_file_path)
            
            return emotion
            
        except Exception as e:
            print(f"[TTS] 오류 발생: {str(e)}")
            return "neutral"
    
    def _process_conversation_audio(self):
        """일반 대화 인식을 위한 오디오 데이터 처리"""
        try:
            print("[대화 인식] 시작...")
            
            # 오디오 데이터 수집 (3초)
            frames = []
            for _ in range(0, int(self.RATE / self.CHUNK * 3)):
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
            
            # WAV 형식으로 변환
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
                with wave.open(temp_file_path, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
            
            # 오디오 파일 읽기
            with open(temp_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            # 음성 인식 설정
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="ko-KR",
                model="latest_long"
            )
            
            # 음성 인식 요청
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # 인식 결과 처리
            if not response.results:
                print("[대화 인식] 인식된 텍스트가 없습니다.")
                return None
                
            transcript = response.results[0].alternatives[0].transcript
            print(f"[대화 인식] 인식된 텍스트: {transcript}")
            
            return transcript
            
        except Exception as e:
            print(f"[대화 인식] 오류 발생: {str(e)}")
            return None
        finally:
            # 임시 파일 삭제
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

    def _is_silence(self, audio_data, threshold=300):
        """오디오 데이터가 무음인지 확인합니다."""
        return max(audio_data) < threshold

    def run(self):
        """AI 컨트롤러 실행"""
        print("[AI 컨트롤러] 시작...")
        try:
            while self.running:
                # 오디오 데이터 읽기
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # 키워드 인식
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print("[키워드 인식] 키워드 감지됨!")
                    self._handle_keyword_detected()
                    
        except Exception as e:
            print(f"[실행] 오류 발생: {str(e)}")
        finally:
            self.stop()

    def _handle_keyword_detected(self):
        """키워드가 감지되었을 때의 처리"""
        try:
            # 상태 업데이트
            self.state.update(is_listening=True)
            
            # 음성 인식
            transcript = self._process_conversation_audio()
            
            if transcript:
                # GPT 응답 생성
                response = self._get_gpt_response(transcript)
                
                # 표정 추출
                expression, _ = self._parse_response(response)
                print(f"[표정] {expression}")
                
                # 상태 업데이트
                self.state.update(expression=expression, is_speaking=True)
                
                # 음성 합성 및 재생
                emotion = self._process_gpt_response(response)
                
                # 상태 업데이트
                self.state.update(is_speaking=False)
            
        except Exception as e:
            print(f"[처리] 오류 발생: {str(e)}")
        finally:
            self.state.update(is_listening=False)

    def stop(self):
        """AI 컨트롤러 종료"""
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'output_stream'):
            self.output_stream.stop_stream()
            self.output_stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()