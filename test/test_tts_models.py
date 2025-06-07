import os
from dotenv import load_dotenv
from planty import Planty
from google.cloud import texttospeech

def test_all_models():
    """모든 TTS 모델 테스트"""
    print("모든 TTS 모델 테스트를 시작합니다...")
    
    planty = Planty()
    test_text = "안녕하세요, 다양한 음성 모델을 테스트해보겠습니다."
    
    # 테스트할 모델 목록
    models = [
        "ko-KR-Neural2-A",  # Neural2 여성
        "ko-KR-Neural2-B",  # Neural2 남성
        "ko-KR-Wavenet-A",  # WaveNet 여성
        "ko-KR-Wavenet-B",  # WaveNet 남성
        "ko-KR-Chirp3-HD-Achernar",  # Chirp3 여성
        "ko-KR-Chirp3-HD-Betelgeuse"  # Chirp3 남성
    ]
    
    for model in models:
        print(f"\n{model} 모델 테스트 중...")
        synthesis_input = texttospeech.SynthesisInput(text=test_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=model
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = planty.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        output_file = f"test/output_{model.replace('-', '_')}.mp3"
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        os.system(f"afplay {output_file}")
        os.remove(output_file)
        
    print("\n모든 모델 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_all_models() 