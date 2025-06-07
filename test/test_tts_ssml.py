import os
from dotenv import load_dotenv
from planty import Planty
from google.cloud import texttospeech

def test_ssml_features():
    """SSML 기능 테스트"""
    print("SSML 기능 테스트를 시작합니다...")
    
    planty = Planty()
    
    # SSML 테스트 케이스들
    ssml_tests = [
        {
            "name": "기본 SSML",
            "ssml": """
            <speak>
                안녕하세요! <break time="1s"/>
                오늘은 <emphasis level="strong">정말</emphasis> 좋은 날이에요.
            </speak>
            """
        },
        {
            "name": "속도와 피치 조절",
            "ssml": """
            <speak>
                <prosody rate="slow" pitch="+2st">천천히 말해볼게요.</prosody>
                <break time="1s"/>
                <prosody rate="fast" pitch="-2st">빠르게 말해볼게요.</prosody>
            </speak>
            """
        },
        {
            "name": "감정 표현",
            "ssml": """
            <speak>
                <prosody rate="slow" pitch="+4st" volume="loud">와! 정말 기뻐요!</prosody>
                <break time="1s"/>
                <prosody rate="slow" pitch="-4st" volume="soft">음... 조금 슬퍼요.</prosody>
            </speak>
            """
        }
    ]
    
    for test in ssml_tests:
        print(f"\n{test['name']} 테스트 중...")
        synthesis_input = texttospeech.SynthesisInput(ssml=test['ssml'])
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Neural2-A"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = planty.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        output_file = f"test/output_ssml_{test['name'].replace(' ', '_')}.mp3"
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        os.system(f"afplay {output_file}")
        os.remove(output_file)
        
    print("\nSSML 기능 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_ssml_features() 