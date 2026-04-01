from gpiozero import Buzzer, DigitalInputDevice # 'gpiozero' 라이브러리에서 'DigitalInputDevice', 'Buzzer' 클래스를 가져옴
import time #＇time＇ 라이브러리를 가져옴

bz = Buzzer(18) # GPIO 18번 핀을 부저 제어 핀으로 초기화
gas = DigitalInputDevice(17) # GPIO 17번 핀을 MQ2 센서 입력 핀으로 초기화

try: # 무한 루프를 시작, 아래 동작을 반복함 (Lines 8 ~ 18)

    while True:
        if gas.value == 0:    # DO 핀이 LOW(0)이면 가스가 감지된 것으로 판단
            print("Gas Detected") # 터미널에 'Gas Detected' 출력
            bz.on() # 부저 ON
        else:                 # DO 핀이 HIGH(1)이면 정상 상태로 판단
            print("Safe") # 터미널에 'Safe' 출력
            bz.off() # 부저 OFF

        time.sleep(0.2) # 0.2초 마다 센서 값을 반복 확인

except KeyboardInterrupt: # 키보드 인터럽트(Ctrl+C) 발생 시 루프 종료
    pass

bz.off() # 프로그램 종료 시 부저를 반드시 OFF 처리
