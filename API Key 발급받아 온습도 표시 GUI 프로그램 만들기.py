import urllib.request, json, tkinter, tkinter.font
 
API_KEY = "Enter your API key here"
 
def tick1Min():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
    temp = data["main"]["temp"]
    humi = data["main"]["humidity"]
    label.config(text=f"{temp:.1f}C   {humi}%")
    window.after(60000, tick1Min)
 
window = tkinter.Tk()
window.title("TEMP HUMI DISPLAY")
window.geometry("400x100")
window.resizable(False, False)
font = tkinter.font.Font(size=30)
label = tkinter.Label(window, text="", font=font)
label.pack()
tick1Min()
window.mainloop()
