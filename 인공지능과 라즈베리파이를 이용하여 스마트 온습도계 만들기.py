import time
import collections
import tkinter as tk
from tkinter import ttk
import threading
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures  # 다항 회귀를 위한 라이브러리
import requests  # 텔레그램 메시지 전송용

# 라즈베리파이 5 하드웨어 제어 라이브러리
import board
import adafruit_dht
from gpiozero import LED, Buzzer

# [사용자 설정] 텔레그램 봇 정보 입력
TELEGRAM_TOKEN = ""  # 발급받은 봇 토큰 입력
CHAT_ID = ""            # 본인의 채팅 ID(숫자) 입력

# 1. 하드웨어 설정 (GPIO 핀 지정)
DHT_PIN = board.D4       # GPIO 4
LED_PIN = 17            # GPIO 17
BUZZER_PIN = 27         # GPIO 27

dht_device = adafruit_dht.DHT11(DHT_PIN)
led = LED(LED_PIN)
buzzer = Buzzer(BUZZER_PIN)

# 2. 데이터 저장을 위한 큐 (다항 회귀 추세를 보기 위해 최근 60초 데이터 저장으로 확장)
time_history = collections.deque(maxlen=60)
temp_history = collections.deque(maxlen=60)
hum_history = collections.deque(maxlen=60)

# 전역 변수 초기화
current_temp = 0.0
current_hum = 0.0
predicted_temp = 0.0
predicted_hum = 0.0
alert_status = "정상"

# 텔레그램 알림 도배 방지를 위한 마지막 발송 시간 기록 변수 (초기값 0)
last_telegram_time = 0 

# 3. 텔레그램 메시지 전송 함수 (비동기 스레드 활용용)
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print("텔레그램 전송 실패:", response.text)
    except Exception as e:
        print("텔레그램 에러:", e)

# 4. 데이터 예측 AI 함수
def predict_future_value(time_list, value_list, target_future_time=30):
    # 데이터가 최소 4개 이상 쌓여야 곡선(2차 다항식)을 안정적으로 그릴 수 있음
    if len(value_list) < 4:
        return value_list[-1] if value_list else 0.0
    
    X = np.array(time_list).reshape(-1, 1)
    y = np.array(value_list)
    
    # degree=2 설정으로 데이터를 2차 곡선형태(y = ax² + bx + c)로 변환
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    
    # 변환된 다항 특징량을 선형 회귀 모델에 학습시킵니다 (이것이 다항회귀)
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # 미래 타겟 시간 계산 및 예측 수행
    future_time = X[-1][0] + target_future_time
    future_time_poly = poly.transform([[future_time]])
    prediction = model.predict(future_time_poly)
    
    return float(prediction[0])

# 5. 센서 데이터 수집 및 수정된 제어 스레드 함수
def sensor_loop():
    global current_temp, current_hum, predicted_temp, predicted_hum, alert_status, last_telegram_time
    start_time = time.time()
    
    while True:
        try:
            temp = dht_device.temperature
            hum = dht_device.humidity
            
            if temp is not None and hum is not None:
                current_temp = temp
                current_hum = hum
                elapsed_time = time.time() - start_time
                
                # 시계열 학습 데이터 추가
                time_history.append(elapsed_time)
                temp_history.append(current_temp)
                hum_history.append(current_hum)
                
                # AI 예측 수행 (다항 회귀 기반 30초 후 예측)
                predicted_temp = predict_future_value(list(time_history), list(temp_history), 30)
                predicted_hum = predict_future_value(list(time_history), list(hum_history), 30)
                
                status_parts = []
                telegram_msg_parts = [] # 텔레그램에 보낼 문구 취합

                # ① 현재 값이 기준을 넘으면 부저(Buzzer) 작동
                if current_temp >= 26.0 or current_hum >= 70.0:
                    buzzer.on()
                    status_parts.append("🚨 현재 상태 위험 (부저)")
                    telegram_msg_parts.append(f"[현재 상태 위험]\n현재 온도: {current_temp:.1f}°C, 현재 습도: {current_hum:.1f}%")
                else:
                    buzzer.off()

                # ② AI 예측치가 기준을 넘으면 LED 작동 (미리 경고)
                if predicted_temp >= 26.0 or predicted_hum >= 70.0:
                    led.on()
                    status_parts.append("🔮 AI 예측 위험 (LED)")
                    telegram_msg_parts.append(f"[AI 30초후 예측 위험]\n예측 온도: {predicted_temp:.1f}°C, 예측 습도: {predicted_hum:.1f}%")
                else:
                    led.off()

                # GUI 상태 메시지 업데이트 
                if len(status_parts) == 2:
                    alert_status = "⚠️ 현재 & 예측 모두 위험!!"
                elif len(status_parts) == 1:
                    alert_status = status_parts[0]  
                else:
                    alert_status = "✅ 정상"         
                    
                # 텔레그램 전송 로직
                if status_parts:
                    current_now = time.time()
                    if current_now - last_telegram_time > 60:
                        full_msg = "⚠️ [라즈베리파이 경고 알림]\n\n" + "\n\n".join(telegram_msg_parts)
                        
                        tg_thread = threading.Thread(target=send_telegram_message, args=(full_msg,), daemon=True)
                        tg_thread.start()
                        
                        last_telegram_time = current_now 
                    
        except RuntimeError as error:
            pass
        except Exception as e:
            print(f"오류 발생: {e}")
            
        time.sleep(1) # 1초 주기로 반복 수집

# 6. Tkinter GUI 레이아웃 구성
root = tk.Tk()
root.title("라즈베리파이5 온습도 모니터링 & AI 예측 시스템")
root.geometry("500x400")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 14))
style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))

lbl_title = ttk.Label(root, text="실시간 온습도 & AI 예측 제어", style="Header.TLabel")
lbl_title.pack(pady=15)

frame = ttk.Frame(root, padding="10")
frame.pack(fill="both", expand=True)

# 현재 데이터 표시
ttk.Label(frame, text="현재 온도:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
lbl_current_temp = ttk.Label(frame, text="0.0 °C", font=("Helvetica", 14))
lbl_current_temp.grid(row=0, column=1, padx=10, pady=10, sticky="w")

ttk.Label(frame, text="현재 습도:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
lbl_current_hum = ttk.Label(frame, text="0.0 %", font=("Helvetica", 14))
lbl_current_hum.grid(row=1, column=1, padx=10, pady=10, sticky="w")

ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky="ew", pady=15)

# 30초 후 예측 데이터 표시
ttk.Label(frame, text="30초 후 예측 온도:", font=("Helvetica", 12, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
lbl_pred_temp = ttk.Label(frame, text="계산 중...", font=("Helvetica", 14, "italic"), foreground="blue")
lbl_pred_temp.grid(row=3, column=1, padx=10, pady=10, sticky="w")

ttk.Label(frame, text="30초 후 예측 습도:", font=("Helvetica", 12, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="e")
lbl_pred_hum = ttk.Label(frame, text="계산 중...", font=("Helvetica", 14, "italic"), foreground="blue")
lbl_pred_hum.grid(row=4, column=1, padx=10, pady=10, sticky="w")

ttk.Separator(frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky="ew", pady=15)

# 현재 장치 상태 표시
ttk.Label(frame, text="시스템 상태:", font=("Helvetica", 12, "bold")).grid(row=6, column=0, padx=10, pady=10, sticky="e")
lbl_status = ttk.Label(frame, text="정상", font=("Helvetica", 12, "bold"), foreground="green")
lbl_status.grid(row=6, column=1, padx=10, pady=10, sticky="w")

# 7. GUI 갱신 함수
def update_gui():
    lbl_current_temp.config(text=f"{current_temp:.1f} °C")
    lbl_current_hum.config(text=f"{current_hum:.1f} %")
    
    lbl_pred_temp.config(text=f"{predicted_temp:.1f} °C")
    lbl_pred_hum.config(text=f"{predicted_hum:.1f} %")
    
    lbl_status.config(text=alert_status)
    
    # 텍스트 내용에 따른 색상 제어
    if "모두 위험" in alert_status or "현재 상태 위험" in alert_status:
        lbl_status.config(foreground="red")       
    elif "AI 예측 위험" in alert_status:
        lbl_status.config(foreground="orange")    
    else:
        lbl_status.config(foreground="green")     
        
    root.after(500, update_gui)

# 백그라운드 스레드 시작 및 GUI 루프 실행
sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
sensor_thread.start()

root.after(500, update_gui)
root.mainloop()

dht_device.exit()
