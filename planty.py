import os
import pyaudio
import wave
import whisper

class Planty:
    def __init__(self):
        # Whisper 모델 로드
        print("Whisper 모델을 로드하는 중...")
        self.whisper_model = whisper.load_model("tiny")
        print("Whisper 모델 로드 완료!")
        
        # 오디오 설정
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5
        
        # 오디오 장치 설정
        self.p = pyaudio.PyAudio()
        self.device_index = self._get_input_device()
        
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