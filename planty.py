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
        
    def listen(self):
        """마이크로부터 음성을 입력받아 텍스트로 변환"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        print("\n음성을 입력해주세요... (5초)")
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
            
        print("음성 입력 완료")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # 임시 WAV 파일로 저장
        temp_file = "temp_recording.wav"
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Whisper로 음성을 텍스트로 변환
        print("음성을 텍스트로 변환하는 중...")
        result = self.whisper_model.transcribe(temp_file)
        os.remove(temp_file)  # 임시 파일 삭제
        
        return result["text"]
    
    def run(self):
        """Planty 실행"""
        print("Planty 음성 인식 테스트를 시작합니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        while True:
            try:
                # 음성 입력 받기
                text = self.listen()
                print(f"\n인식된 텍스트: {text}")
                
            except KeyboardInterrupt:
                print("\nPlanty를 종료합니다.")
                break
            except Exception as e:
                print(f"오류 발생: {str(e)}")
                continue

if __name__ == "__main__":
    planty = Planty()
    planty.run() 