from flask import Flask, request, render_template
from gpiozero import LED

app = Flask(__name__)

red_led = LED(21)   

@app.route('/')
def home():
   return render_template("index.html")

@app.route('/data', methods = ['POST'])
def data():
    data = request.form['led']
    
    if(data == 'on'):
        red_led.on() 
        return home()

    elif(data == 'off'):
        red_led.off() 
        return home()

if __name__ == '__main__':
   app.run(host = '0.0.0.0', port = '80')