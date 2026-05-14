import speech_recognition as sr  # 마이크의 음성 신호를 듣고 텍스트로 바꾸기 위한 도구
import requests                 # 인터넷(API)을 통해 날씨 정보를 받아오기 위한 도구
import os                       # 시스템 명령어(mpv 실행 등)를 사용하기 위한 도구
import asyncio                  # 비동기 처리(작업이 끝날 때까지 효율적으로 기다림)를 위한 도구
import edge_tts                 # 마이크로소프트 엣지의 고품질 음성을 사용하기 위한 도구

# --- 설정값 영역 ---
API_KEY = "50c3bb1ac58a01ec7b10d84c18626318"  # OpenWeatherMap 서버 접속을 위한 개인 비밀키
CITY = "Seoul"                                 # 날씨를 확인하고 싶은 도시 이름
# 날씨 데이터를 요청할 웹 주소 (metric 설정으로 섭씨 온도 사용)
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Microsoft Edge의 신경망 음성: "ko-KR-SunHiNeural" (여성), "ko-KR-InJoonNeural" (남성)
VOICE = "ko-KR-SunHiNeural"

async def speak(msg):
    """
    텍스트(msg)를 받아서 실제 사람 목소리처럼 읽어주는 함수입니다.
    """
    output_file = "speech.mp3"  # 생성된 목소리를 저장할 파일 이름
    # 엣지 TTS 서버에 접속하여 음성 데이터를 만듭니다.
    communicate = edge_tts.Communicate(msg, VOICE)
    await communicate.save(output_file)  # 음성 파일 저장이 완료될 때까지 기다립니다.
   
    # os.system을 통해 라즈베리 파이의 외부 플레이어 'mpv'로 mp3를 재생합니다.
    # --no-terminal은 터미널에 재생 정보가 표시되지 않게 깔끔하게 가려줍니다.
    os.system(f"mpv --no-terminal {output_file}")

async def main():
    """
    프로그램의 메인 루프를 담당하는 함수입니다.
    """
    r = sr.Recognizer()  # 음성 인식기 객체 생성
   
    # 1단계: 마이크 환경 설정
    with sr.Microphone() as source:
        print("환경 소음 측정 중...")
        # 주변이 시끄러우면 인식이 잘 안 되므로, 1초간 소음을 측정해 기준점을 잡습니다.
        r.adjust_for_ambient_noise(source, duration=1)
       
    try:
        while True:
            # 2단계: 사용자 목소리 듣기
            with sr.Microphone() as source:
                print("말씀하세요 (날씨가 궁금하면 '날씨'라고 말해보세요)...")
                audio = r.listen(source)  # 사용자가 말을 멈출 때까지 녹음합니다.
               
            try:
                # 3단계: 구글 음성 인식을 통해 한국어 텍스트로 변환 (STT)
                text = r.recognize_google(audio, language='ko-KR')
                print(f"인식 결과: {text}")
               
                # 만약 인식된 문장에 '날씨'라는 단어가 들어있다면?
                if "날씨" in text:
                    print("날씨 정보를 가져옵니다...")
                    # 4단계: 날씨 API 서버에 접속해서 최신 정보를 받아옵니다.
                    response = requests.get(WEATHER_URL)
                    data = response.json()  # 받아온 복잡한 데이터를 파이썬 딕셔너리로 변환
                   
                    # 데이터에서 필요한 정보(온도, 습도)만 쏙쏙 뽑아냅니다.
                    temp = int(data["main"]["temp"])    # 온도를 정수로 변환
                    humi = data["main"]["humidity"]    # 습도값 추출
                   
                    # 5단계: 대답할 문장 생성
                    msg = f"현재 서울의 기온은 {temp}도, 습도는 {humi}퍼센트입니다."
                    print(f"응답: {msg}")
                   
                    # 생성된 문장을 TTS 함수로 전달하여 목소리로 출력합니다.
                    await speak(msg)
                   
            except sr.UnknownValueError:
                # 목소리가 너무 작거나 인식할 수 없는 소리인 경우
                print("음성을 이해하지 못했습니다.")
            except sr.RequestError as e:
                # 인터넷 연결 끊김 등 API 서버 접속 오류인 경우
                print(f"구글 서비스 오류: {e}")
               
    except KeyboardInterrupt:
        # 사용자가 Ctrl+C를 눌러 프로그램을 강제로 끌 때 실행됩니다.
        print("\n프로그램을 종료합니다.")

# 프로그램의 시작점
if __name__ == "__main__":
    # 비동기 함수인 main을 실행합니다.
    asyncio.run(main())
