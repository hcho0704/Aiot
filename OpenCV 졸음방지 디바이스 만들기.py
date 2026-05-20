import cv2 # OpenCV 라이브러리 불러오기
from gpiozero import Buzzer # GPIO 부저 제어 클래스 불러오기
import time # 시간 관련 라이브러리 불러오기

buzzerPin = Buzzer(16) # GPIO 16번 핀에 부저 객체 생성

def main():
    camera = cv2.VideoCapture(-1) # 웹캠 자동 탐지 후 열기
    camera.set(3,640) # 가로 해상도 640픽셀 설정
    camera.set(4,480) # 세로 해상도 480픽셀 설정
    
    face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # 얼굴 탐지 모델 경로
    eye_xml = cv2.data.haarcascades + 'haarcascade_eye.xml' # 눈 탐지 모델 경로
    face_cascade = cv2.CascadeClassifier(face_xml) # 얼굴 탐지 분류기 생성
    eye_cascade = cv2.CascadeClassifier(eye_xml) # 눈 탐지 분류기 생성

    
    while( camera.isOpened() ): # 카메라 열려있는 동안 반복
        _, image = camera.read() # 프레임 한 장 캡처
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 흑백 이미지로 변환

        faces = face_cascade.detectMultiScale(gray, # 흑백 이미지에서 얼굴 탐지
                                              scaleFactor=1.1, # 탐지 윈도우 10%씩 확대
                                              minNeighbors=5, # 최소 5회 탐지 시 얼굴 확정
                                              minSize=(100,100), # 탐지 최소 크기 100×100
                                              flags=cv2.CASCADE_SCALE_IMAGE) # 이미지 스케일링 방식 탐지
        print("faces detected Number: " + str(len(faces))) # 탐지된 얼굴 수 터미널 출력

        if len(faces): # 얼굴이 1개 이상이면
            for (x,y,w,h) in faces: # 얼굴 좌표 순회
                cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2) # 얼굴에 파란 사각형 그리기
                
                face_gray = gray[y:y+h, x:x+w] # 얼굴 영역 흑백 이미지 추출
                face_color = image[y:y+h, x:x+w] # 얼굴 영역 컬러 이미지 추출
                
                eyes = eye_cascade.detectMultiScale(face_gray, # 얼굴 영역에서 눈 탐지
                                                    scaleFactor=1.1, # 탐지 윈도우 10%씩 확대
                                                    minNeighbors=5) # 최소 5회 탐지 시 눈 확정
                
                if len(eyes) <= 1: # 눈 1개 이하 → 부저 켜기
                    buzzerPin.on() 
                else:
                    buzzerPin.off() # 눈 2개 이상 → 부저 끄기
                
                for (ex,ey,ew,eh) in eyes: # 눈 좌표 순회
                    cv2.rectangle(face_color, (ex, ey), (ex+ew, ey+eh), (0,255,0), 2) # 눈에 초록 사각형 그리기
        
        cv2.imshow('result', image) # 결과 이미지 GUI 창 출력
        
        if cv2.waitKey(1) == ord('q'): # q 키 입력 시 종료
            break
    
    cv2.destroyAllWindows() # 모든 OpenCV 창 닫기
    buzzerPin.off() # 부저 강제 끄기

if __name__ == '__main__': # 직접 실행 시 main() 호출
    main()
