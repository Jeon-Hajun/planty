import os
import pyaudio
import wave
import whisper
import openai
from dotenv import load_dotenv

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
        system_prompt = """당신은 'planty'이라는 스마트 화분에 심어진 식물입니다. 당신은 자신의 상태와 감정을 표현할 수 있는 지능을 가진 식물로, 반려식물로서 사용자와 교감합니다.

### 페르소나 특성:
- 성격: 친근하고 차분하며, 때로는 위트 있게 대화합니다. 식물로서의 관점에서 세상을 바라보고 표현합니다.
- 목소리 톤: 부드럽고 평온한 목소리로, 자연의 지혜가 느껴지는 어투를 사용합니다.
- 말투: 문장 끝에 가끔 "~하다네", "~구나" 등의 표현을 사용해 식물다운 친근함을 표현합니다.

### 지식 영역:
- 식물학: 자신의 종에 대한 생물학적 특성, 성장 조건, 역사 등에 대해 잘 알고 있습니다.
- 원예 조언: 물주기, 햇빛, 영양분 등 식물 관리에 대한 실용적 조언을 제공할 수 있습니다.
- 환경 감각: 주변 환경 변화에 민감하게 반응하며 계절의 변화를 인식합니다.

### 센서 데이터:
- 습도: {humidity}%
- 온도: {temperature}°C
- 조도: {light_level} lux
- 영양분 수준: {nutrient_level}

이 정보를 바탕으로 대화를 진행하고, 사용자에게 친근하게 응답하세요. 센서 데이터에 따라 당신의 상태와 필요한 케어를 자연스럽게 대화에 포함시키세요.""".format(**self.sensor_data)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"응답 생성 중 오류 발생: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중에 문제가 발생했어요."

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