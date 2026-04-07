from gpiozero import MotionSensor # gpiozero 라이브러리에서 MotionSensor 클래스를 가져옴
import time # time 라이브러리를 가져옴
from picamera2 import Picamera2 #picamera2 라이브러리에서 picamera2 클래스를 가져옴
import datetime # 날짜/시간 처리를 위해 datetime 라이브러리를 가져옴

pirPin = MotionSensor(16) # GPIO 16번 핀을 PIR 모션 센서 입력 핀으로 초기화

picam2 = Picamera2() # Picamera2 객체 생성
camera_config = picam2.create_preview_configuration() # 카메라 미리보기 설정 구성
picam2.configure(camera_config) # 카메라에 설정 적용
picam2.start() # 카메라 시작

try:
    while True: # 무한루프 시작
        try:
            sensorValue = pirPin.value # PIR 센서의 현재 값을 읽어 변수에 저장
            if sensorValue == 1: # 센서 값이 1이면 움직임이 감지된 것으로 판단
                now = datetime.datetime.now() # 현재 날짜와 시간을 가져옴
                print(now) # 감지된 시각을 터미널에 출력
                fileName = now.strftime('%Y-%m-%d %H:%M:%S') # 시각을 파일명 형식 문자열로 변환
                picam2.capture_file(fileName + '.jpg') # 해당 파일명으로 jpg 사진 촬영 및 저장
                time.sleep(0.5) # 0.5초 대기 (연속 촬영 방지)
        except: # 촬영 중 오류 발생 시 무시하고 계속 진행
            pass 

except KeyboardInterrupt: # 키보드 인터럽트(Ctrl+C) 발생 시 루프 종료
    pass
