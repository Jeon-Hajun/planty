import os
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import openai
from google.cloud import texttospeech
from dotenv import load_dotenv
import tempfile
import json

class AIAssistant:
    def __init__(self):
        load_dotenv()
        
        # OpenAI API 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Whisper 모델 로드
        self.whisper_model = whisper.load_model("tiny")
        
        # Google Cloud TTS 클라이언트 초기화
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # 오디오 설정
        self.sample_rate = 16000
        self.channels = 1
        
    def record_audio(self, duration=5):
        """마이크로부터 오디오를 녹음합니다."""
        print("녹음을 시작합니다...")
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels
        )
        sd.wait()
        print("녹음이 완료되었습니다.")
        return recording
    
    def save_audio(self, recording, filename):
        """녹음된 오디오를 WAV 파일로 저장합니다."""
        wav.write(filename, self.sample_rate, recording)
    
    def transcribe_audio(self, audio_file):
        """Whisper를 사용하여 오디오를 텍스트로 변환합니다."""
        result = self.whisper_model.transcribe(audio_file)
        return result["text"]
    
    def get_gpt_response(self, prompt):
        """GPT API를 사용하여 응답을 생성합니다."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 스마트 반려식물 관리 시스템의 AI 비서입니다. 식물 관리와 관련된 질문에 답변해주세요."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GPT 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def text_to_speech(self, text):
        """Google Cloud TTS를 사용하여 텍스트를 음성으로 변환합니다."""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Neural2-A"
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # 임시 파일에 오디오 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.audio_content)
                return temp_file.name
                
        except Exception as e:
            print(f"TTS 변환 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def process_command(self):
        """음성 명령을 처리하는 전체 프로세스를 실행합니다."""
        # 1. 오디오 녹음
        recording = self.record_audio()
        
        # 2. 임시 파일에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            self.save_audio(recording, temp_file.name)
            
            # 3. 음성을 텍스트로 변환
            text = self.transcribe_audio(temp_file.name)
            print(f"인식된 텍스트: {text}")
            
            # 4. GPT로 응답 생성
            response = self.get_gpt_response(text)
            print(f"GPT 응답: {response}")
            
            # 5. 응답을 음성으로 변환
            audio_file = self.text_to_speech(response)
            
            # 임시 파일 삭제
            os.unlink(temp_file.name)
            
            return {
                "recognized_text": text,
                "response": response,
                "audio_file": audio_file
            }

if __name__ == "__main__":
    # 테스트 코드
    assistant = AIAssistant()
    result = assistant.process_command()
    print("처리 결과:", json.dumps(result, ensure_ascii=False, indent=2)) 