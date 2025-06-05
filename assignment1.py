import tkinter as tk
from tkinter import Label, Button
import serial
import pymysql
import time

# Database Setup
db = pymysql.connect(host="localhost", user="pi", password="123", database="assignment1")
cursor = db.cursor()

# Connect to Arduino via Serial
arduino = serial.Serial('/dev/ttyS0', 9600, timeout=1)
time.sleep(2)

# GUI Setup
root = tk.Tk()
root.title("Arduino Monitor")
root.geometry("300x200")

temp_label = Label(root, text="Temperature: -- C", font=("Arial", 14))
temp_label.pack()

fire_label = Label(root, text="Fire Status: No Fire", font=("Arial", 14), fg="green")
fire_label.pack()

fan_status = False  # Track fan state

def toggle_fan():
    global fan_status
    if fan_status:
        arduino.write(b'FAN_OFF\n')
        fan_button.config(text="Turn Fan ON")
    else:
        arduino.write(b'FAN_ON\n')
        fan_button.config(text="Turn Fan OFF")
    fan_status = not fan_status

fan_button = Button(root, text="Turn Fan ON", command=toggle_fan, font=("Arial", 12))
fan_button.pack()

# Function to Read Arduino Data
def update_data():
    arduino.write(b'')  # Ensure we read fresh data
    data = arduino.readline().decode().strip()
    if data:
        try:
            temp, flame = data.split(",")
            temp_label.config(text=f"Temperature: {temp} C")
            
            if flame == "0":
                fire_label.config(text="Fire Status: FIRE DETECTED!", fg="red")
                arduino.write(b'BUZZER_ON\n')  # Activate buzzer
            else:
                fire_label.config(text="Fire Status: No Fire", fg="green")
                arduino.write(b'BUZZER_OFF\n')  # Deactivate buzzer

            # Save Data to MySQL
            cursor.execute("INSERT INTO tempLog (temperature, time) VALUES (%s, NOW())", (temp,))
            db.commit()

        except ValueError:
            pass

    root.after(1000, update_data)  # Refresh every second

update_data()
root.mainloop()

# Close DB connection when GUI closes
cursor.close()
db.close()