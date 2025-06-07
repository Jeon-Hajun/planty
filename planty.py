import os
import pyaudio
import wave
import whisper
import openai
from dotenv import load_dotenv
from google.cloud import texttospeech
import json

class Planty:
    def __init__(self):
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
        self.RECORD_SECONDS = 5
        
        # 오디오 장치 설정
        self.p = pyaudio.PyAudio()
        self.device_index = self._get_input_device()
        
        # 센서 데이터 초기화
        self.sensor_data = {
            "humidity": 60,
            "temperature": 25,
            "light_level": 1000,
            "nutrient_level": 70
        }
        
    def _get_input_device(self):
        """사용 가능한 입력 장치 찾기"""
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info.get('maxInputChannels') > 0:  # 입력 장치인 경우
                print(f"입력 장치 발견: {dev_info.get('name')}")
                return i
        return None
        
    def listen(self):
        """마이크로부터 음성을 입력받아 텍스트로 변환"""
        if self.device_index is None:
            print("입력 장치를 찾을 수 없습니다.")
            return None
            
        try:
            stream = self.p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               input_device_index=self.device_index,
                               frames_per_buffer=self.CHUNK)
            
            print("\n음성을 입력해주세요... (5초)")
            frames = []
            
            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                
            print("음성 입력 완료")
            
            stream.stop_stream()
            stream.close()
            
            # 임시 WAV 파일로 저장
            temp_file = "temp_recording.wav"
            wf = wave.open(temp_file, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Whisper로 음성을 텍스트로 변환 (한국어로 고정)
            print("음성을 텍스트로 변환하는 중...")
            result = self.whisper_model.transcribe(
                temp_file,
                language="ko",  # 한국어로 고정
                task="transcribe"  # 음성-텍스트 변환 작업
            )
            os.remove(temp_file)  # 임시 파일 삭제
            
            return result["text"]
            
        except Exception as e:
            print(f"오디오 입력 중 오류 발생: {str(e)}")
            return None
    
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
그렇군요! 더 자세히 이야기해주세요.""".format(**self.sensor_data)

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

    def run(self):
        """Planty 실행"""
        print("Planty 음성 인식 테스트를 시작합니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        while True:
            try:
                # 음성 입력 받기
                text = self.listen()
                if text:
                    print(f"\n인식된 텍스트: {text}")
                    # LLM 응답 생성
                    response = self.generate_response(text)
                    print(f"\nPlanty의 응답: {response}")
                    # TTS로 응답 재생
                    self.speak(response)
                else:
                    print("음성 인식에 실패했습니다. 다시 시도해주세요.")
                
            except KeyboardInterrupt:
                print("\nPlanty를 종료합니다.")
                self.p.terminate()
                break
            except Exception as e:
                print(f"오류 발생: {str(e)}")
                continue

if __name__ == "__main__":
    planty = Planty()
    planty.run() 