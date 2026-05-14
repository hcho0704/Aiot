import speech_recognition as sr
import requests
import os
import asyncio
import edge_tts

API_KEY = "50c3bb1ac58a01ec7b10d84c18626318"
CITY = "Seoul"
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Microsoft Edge Korean voices: "ko-KR-SunHiNeural" (Female) or "ko-KR-InJoonNeural" (Male)
VOICE = "ko-KR-SunHiNeural"

async def speak(msg):
    """Generates Edge TTS audio and plays it."""
    output_file = "speech.mp3"
    communicate = edge_tts.Communicate(msg, VOICE)
    await communicate.save(output_file)
    # Use 'mpv' to play the file on Raspberry Pi
    os.system(f"mpv --no-terminal {output_file}")

async def main():
    r = sr.Recognizer()
    
    # Pre-adjust for noise to make it more responsive
    with sr.Microphone() as source:
        print("환경 소음 측정 중...")
        r.adjust_for_ambient_noise(source, duration=1)
        
    try:
        while True:
            with sr.Microphone() as source:
                print("말씀하세요 (날씨가 궁금하면 '날씨'라고 말해보세요)...")
                audio = r.listen(source)
                
            try:
                # Use Google for STT
                text = r.recognize_google(audio, language='ko-KR')
                print(f"인식 결과: {text}")
                
                # Check if '날씨' is in the recognized text
                if "날씨" in text:
                    print("날씨 정보를 가져옵니다...")
                    response = requests.get(WEATHER_URL)
                    data = response.json()
                    
                    temp = int(data["main"]["temp"])
                    humi = data["main"]["humidity"]
                    desc = data["weather"][0]["description"]
                    
                    msg = f"현재 서울의 기온은 {temp}도, 습도는 {humi}퍼센트입니다."
                    print(f"응답: {msg}")
                    await speak(msg)
                    
            except sr.UnknownValueError:
                print("음성을 이해하지 못했습니다.")
            except sr.RequestError as e:
                print(f"구글 서비스 오류: {e}")
                
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    asyncio.run(main())
