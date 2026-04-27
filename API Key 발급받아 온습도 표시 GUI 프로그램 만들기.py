import urllib.request, json, tkinter, tkinter.font #웹 요청 보내는 라이브러리, JSON 데이터 처리 라이브러리, GUI 창 만드는 라이브러리, tkinter 폰트 설정 라이브러리
 
API_KEY = "Enter your API key here" #OpenWeatherMap에서 발급받은 API키 입력
 
def tick1Min():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric" # 서울 날씨 요청 URL
    with urllib.request.urlopen(url) as r: # API에 요청 보내기
        data = json.loads(r.read()) # 응답을 JSON 형태로 변환
    temp = data["main"]["temp"] # 온도 꺼내기
    humi = data["main"]["humidity"] # 습도 꺼내기
    label.config(text=f"{temp:.1f}C   {humi}%") # 라벨 텍스트 업데이트
    window.after(60000, tick1Min) # 1분(60000ms) 후 함수 재실행
 
window = tkinter.Tk() # 창 생성
window.title("TEMP HUMI DISPLAY") # 창 제목 설정
window.geometry("400x100") # 창 크기 설정 (가로 x 세로)
window.resizable(False, False) # 창 크기 조절 불가 설정 (True로 입력 시 조절 가능)
font = tkinter.font.Font(size=30) # 폰트 크기 30 설정
label = tkinter.Label(window, text="", font=font) # 텍스트 라벨 생성
label.pack() # 라벨을 창에 배치 
tick1Min() # 시작 시 날씨 첫 호출
window.mainloop() # 창 유지 (이벤트 루프)

