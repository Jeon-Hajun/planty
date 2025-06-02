from ai_assistant import AIAssistant
import json

def test_voice_recognition():
    """음성 인식 테스트"""
    print("음성 인식 테스트를 시작합니다...")
    assistant = AIAssistant()
    
    try:
        result = assistant.process_command()
        print("\n테스트 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return True
    except Exception as e:
        print(f"테스트 중 오류가 발생했습니다: {str(e)}")
        return False

if __name__ == "__main__":
    test_voice_recognition() 