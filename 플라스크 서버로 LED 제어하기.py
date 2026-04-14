from flask import Flask, request, render_template # 웹 서버 만드는 Flask 라이브러리
from gpiozero import LED # 라즈베리 파이 GPIO 핀 제어 라이브러리

app = Flask(__name__) # Flask 앱 생성

red_led = LED(21) # 21번 핀에 연결된 LED 설정   

@app.route('/') # 기본 주소(/) 접속 시 실행
def home():
   return render_template("index.html") # index.html 파일을 브라우저에 보여줌

@app.route('/data', methods = ['POST']) # /data 주소로 POST 요청 왔을 때 실행
def data():
    data = request.form['led'] # HTML 폼에서 'led' 값 가져오기
    
    if(data == 'on'): # 값이 ‘ON’이면 LED 켜기
        red_led.on() 
        return home()

    elif(data == 'off'): # 값이 ‘OFF’이면 LED 끄기
        red_led.off() 
        return home() # 처리 후 다시 메인 페이지로 이동

if __name__ == '__main__':
   app.run(host = '0.0.0.0', port = '80') # 모든 IP(0.0.0.0)에서 80번 포트로 서버 실행
