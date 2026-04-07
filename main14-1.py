from gpiozero import MotionSensor
import time
from picamera2 import Picamera2
import datetime

pirPin = MotionSensor(16)

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

try:
    while True:
        try:
            sensorValue = pirPin.value
            if sensorValue == 1:
                now = datetime.datetime.now()
                print(now)
                fileName = now.strftime('%Y-%m-%d %H:%M:%S')
                picam2.capture_file(fileName + '.jpg')
                time.sleep(0.5)
        except:
            pass

except KeyboardInterrupt:
    pass