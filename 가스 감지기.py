from gpiozero import Buzzer, DigitalInputDevice
import time

bz = Buzzer(18)
gas = DigitalInputDevice(17)

try:
    while True:
        if gas.value == 0:    # ← 0 = 가스 감지 (LOW)
            print("가스 감지됨")
            bz.on()
        else:                 # ← 1 = 정상 (HIGH)
            print("정상")
            bz.off()

        time.sleep(0.2)

except KeyboardInterrupt:
    pass

bz.off()
