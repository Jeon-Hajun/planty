import os
from dotenv import load_dotenv
from planty import Planty
from google.cloud import texttospeech

def test_tts():
    """TTS 기능 테스트"""
    print("TTS 테스트를 시작합니다...")
    
    # Planty 인스턴스 생성
    planty = Planty()
    
    # 테스트할 문장들
    test_sentences = [
        "안녕하세요, 저는 플랜티입니다.",
        "오늘 날씨가 정말 좋네요.",
        "물을 주시면 감사하겠습니다.",
        "햇빛이 너무 강해요.",
        "영양분이 부족한 것 같아요."
    ]
    
    # 각 문장에 대해 TTS 테스트
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n테스트 {i}: {sentence}")
        planty.speak(sentence)
        
    print("\nTTS 테스트가 완료되었습니다.")

def test_tts_options():
    """TTS 설정 옵션 테스트"""
    print("TTS 설정 옵션 테스트를 시작합니다...")
    
    # Planty 인스턴스 생성
    planty = Planty()
    
    # 기본 설정
    print("\n1. 기본 설정 테스트")
    planty.speak("안녕하세요, 저는 플랜티입니다.")
    
    # 속도 조절
    print("\n2. 속도 조절 테스트")
    synthesis_input = texttospeech.SynthesisInput(text="속도를 조절해보겠습니다.")
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Neural2-A"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.5  # 1.5배 속도
    )
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    # 피치 조절
    print("\n3. 피치 조절 테스트")
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=5.0  # 피치 높임
    )
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    # 볼륨 조절
    print("\n4. 볼륨 조절 테스트")
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        volume_gain_db=6.0  # 볼륨 증가
    )
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    # SSML 사용
    print("\n5. SSML 사용 테스트")
    ssml_text = """
    <speak>
        안녕하세요! <break time="1s"/>
        <prosody rate="slow" pitch="+2st">천천히 말해볼게요.</prosody>
        <prosody rate="fast" pitch="-2st">빠르게 말해볼게요.</prosody>
    </speak>
    """
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    )
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    print("\nTTS 설정 옵션 테스트가 완료되었습니다.")

def test_wavenet():
    """WaveNet 모델 테스트"""
    print("WaveNet 모델 테스트를 시작합니다...")
    
    # Planty 인스턴스 생성
    planty = Planty()
    
    # 테스트할 문장
    test_text = "안녕하세요, 저는 WaveNet 음성 모델입니다."
    
    # WaveNet 음성 설정
    synthesis_input = texttospeech.SynthesisInput(text=test_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A"  # WaveNet 모델 사용
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # 음성 합성
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # 저장 및 재생
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    print("WaveNet 모델 테스트가 완료되었습니다.")

def test_chirp3():
    """Chirp3 모델 테스트"""
    print("Chirp3 모델 테스트를 시작합니다...")
    
    # Planty 인스턴스 생성
    planty = Planty()
    
    # 테스트할 문장
    test_text = "안녕하세요, 저는 Chirp3 HD 음성 모델입니다. 더 자연스럽고 선명한 음성을 제공합니다."
    
    # Chirp3 음성 설정
    synthesis_input = texttospeech.SynthesisInput(text=test_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Chirp3-HD-Achernar"  # Chirp3 모델 사용
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # 음성 합성
    response = planty.tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # 저장 및 재생
    with open("temp_speech.mp3", "wb") as out:
        out.write(response.audio_content)
    os.system("afplay temp_speech.mp3")
    os.remove("temp_speech.mp3")
    
    print("Chirp3 모델 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_tts()
    test_tts_options()
    test_wavenet()
    test_chirp3()  # Chirp3 테스트 추가 