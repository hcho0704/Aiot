from gpiozero import LED # gpiozero 라이브러리에서 LED 클라스를 가져옴
from time import sleep # time 라이브러리에서 sleep함수를 가져옴

#다양한 LED핀의 핀 번호를 변수로 정의하고 carLedRed, carLedYellow, carLedGreen, humanLedRed, humanLedGreen 변수에 각각 핀 번호를 할당함.
carLedRed = 2 
carLedYellow = 3
carLedGreen = 4
humanLedRed = 20
humanLedGreen = 21

#각 LED를 LED클래스의 객체로 초기화함. 이 때 핀번호를 사용하여 LED객체를 생성함.
carLedRed = LED(2)
carLedYellow = LED(3)
carLedGreen = LED(4)
humanLedRed = LED(20)
humanLedGreen = LED(21)

#무한루프(while 1:) 시작
#변수의 값을 조절하여 LED를 켜고 끔(value 속성이 1이면 켜짐, 0이면 꺼짐)
#각각의 LED를 제어하는 값에 따라 차량 및 보행자 신호등의 상태가 변경됨.
#sleep 함수를 사용하여 LED상태가 변경된 후 대기 사간을 설정함.
try:
    while 1:
        carLedRed.value = 0
        carLedYellow.value = 0
        carLedGreen.value = 1
        humanLedRed.value = 1
        humanLedGreen.value = 0
        sleep(3.0)
        carLedRed.value = 0
        carLedYellow.value = 1
        carLedGreen.value = 0
        humanLedRed.value = 1
        humanLedGreen.value = 0
        sleep(1.0)
        carLedRed.value = 1
        carLedYellow.value = 0
        carLedGreen.value = 0
        humanLedRed.value = 0
        humanLedGreen.value = 1
        sleep(3.0)
    
# 사용자가 Ctrl + C 를 누르면 루프가 중단되고 코드 실행이 종료됨
except KeyboardInterrupt:
    pass

#코드 실행이 종료되면 모든 LED 꺼짐
carLedRed.value = 0
carLedYellow.value = 0
carLedGreen.value = 0
humanLedRed.value = 0
humanLedGreen.value = 0
