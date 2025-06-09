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
        
        # PyAudio 초기화
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Whisper 모델 로드
        self.model = whisper.load_model("tiny")
        
        # OpenAI API 키 설정
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # 오디오 큐 초기화
        self.audio_queue = queue.Queue()
        
        # 음성 인식기 초기화
        self.recognizer = sr.Recognizer()
    
    def _get_gpt_response(self, text):
        """GPT 응답 생성"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 식물을 돌보는 AI 어시스턴트 Planty입니다. 친근하고 자연스러운 대화를 하며, 식물 관리에 대한 조언을 제공합니다."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT 응답 생성 중 오류 발생: {e}")
            return "죄송합니다. 응답을 생성하는데 문제가 발생했습니다."
    
    def _parse_response(self, response):
        """응답에서 표정과 행동 추출"""
        # 기본값
        expression = "neutral"
        action = "idle"
        
        # 긍정적인 표현
        positive_words = ["좋아", "행복", "기쁘", "감사", "즐거운"]
        if any(word in response for word in positive_words):
            expression = "happy"
            action = "waving"
        
        # 부정적인 표현
        negative_words = ["슬프", "걱정", "불안", "힘들", "어려운"]
        if any(word in response for word in negative_words):
            expression = "worried"
            action = "shaking"
        
        # 피곤한 표현
        tired_words = ["피곤", "졸리", "쉬고 싶", "휴식"]
        if any(word in response for word in tired_words):
            expression = "sleepy"
            action = "idle"
        
        return expression, action
    
    def _speak(self, text):
        """TTS로 음성 출력"""
        try:
            # SSML 생성
            ssml = f"""
            <speak>
                <prosody rate="slow" pitch="+0.5st">
                    {text}
                </prosody>
            </speak>
            """
            
            # 음성 설정
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Wavenet-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # 오디오 설정
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,
                pitch=0.0
            )
            
            # TTS 요청
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # 임시 파일로 저장
            with open("temp_speech.mp3", "wb") as out:
                out.write(response.audio_content)
            
            # TODO: 실제 오디오 출력 구현
            # 현재는 파일로만 저장
            
        except Exception as e:
            print(f"TTS 출력 중 오류 발생: {e}")
    
    def _process_audio(self):
        """오디오 처리 스레드"""
        print("음성 인식 시작...")
        while self.running:
            try:
                # 오디오 데이터 수집
                frames = []
                for _ in range(0, int(self.RATE / self.CHUNK * 5)):  # 5초 녹음
                    data = self.stream.read(self.CHUNK)
                    frames.append(data)
                
                # 오디오 데이터를 파일로 저장
                with wave.open("temp_audio.wav", 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                
                # Whisper로 음성 인식
                result = self.model.transcribe("temp_audio.wav")
                text = result["text"]
                print(f"인식된 텍스트: {text}")
                
                # 키워드 감지
                if "플랜티" in text.lower() or "planty" in text.lower():
                    print("키워드 감지됨!")
                    # GPT 응답 생성
                    response = self._get_gpt_response(text)
                    print(f"GPT 응답: {response}")
                    
                    # 표정과 행동 추출
                    expression, action = self._parse_response(response)
                    print(f"표정: {expression}, 행동: {action}")
                    
                    # 상태 업데이트
                    self.state.update(expression=expression, action=action, is_speaking=True)
                    
                    # TTS로 음성 출력
                    self._speak(response)
                    
                    # 상태 업데이트
                    self.state.update(is_speaking=False)
                
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
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate() 