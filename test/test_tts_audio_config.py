import os
from dotenv import load_dotenv
from planty import Planty
from google.cloud import texttospeech

def test_audio_configs():
    """오디오 설정 테스트"""
    print("오디오 설정 테스트를 시작합니다...")
    
    planty = Planty()
    test_text = "안녕하세요, 다양한 오디오 설정을 테스트해보겠습니다."
    
    # 테스트할 오디오 설정들
    audio_configs = [
        {
            "name": "기본 설정",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
        },
        {
            "name": "속도 증가",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.5
            )
        },
        {
            "name": "속도 감소",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.75
            )
        },
        {
            "name": "피치 증가",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=5.0
            )
        },
        {
            "name": "피치 감소",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=-5.0
            )
        },
        {
            "name": "볼륨 증가",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                volume_gain_db=6.0
            )
        },
        {
            "name": "볼륨 감소",
            "config": texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                volume_gain_db=-6.0
            )
        }
    ]
    
    for config in audio_configs:
        print(f"\n{config['name']} 테스트 중...")
        synthesis_input = texttospeech.SynthesisInput(text=test_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Neural2-A"
        )
        
        response = planty.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=config['config']
        )
        
        output_file = f"test/output_audio_{config['name'].replace(' ', '_')}.mp3"
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        os.system(f"afplay {output_file}")
        os.remove(output_file)
        
    print("\n오디오 설정 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_audio_configs() 