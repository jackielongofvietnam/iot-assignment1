import tkinter as tk
from tkinter import Label, Button
import serial
import pymysql
import time

# Database Setup
database = pymysql.connect(
    host="localhost", 
    user="pi", 
    password="", 
    database="assignment1"
)
cursor = database.cursor()

# Connect to Arduino via Serial
arduino = serial.Serial('/dev/ttyS0', 9600, timeout=1)
time.sleep(2)

# UI Setup
root = tk.Tk()
root.title("Environment Monitor")
root.geometry("300x200")

tempLabel = Label(
    root, 
    text="Temperature: -- C", 
    font=("Arial", 14)
)
tempLabel.pack()

fireLabel = Label(
    root, 
    text="Fire Status: No Fire", 
    font=("Arial", 14), fg="green"
)
fireLabel.pack()

fanStatus = False  # Track fan state

def toggle_fan():
    global fanStatus
    if fanStatus:
        command = "FAN_OFF\n"
        arduino.write(command.encode())  # Send command
        fanButton.config(text="Turn Fan ON")
    else:
        command = "FAN_ON\n"
        arduino.write(command.encode())  # Send command
        fanButton.config(text="Turn Fan OFF")

    fanStatus = not fanStatus # Change fan state every time button is pressed

fanButton = Button(root, text="Turn Fan ON", command=toggle_fan, font=("Arial", 12))
fanButton.pack()

fireStatus = "1"  # Track fire state

# Read Arduino Data
def update_data():
    arduino.write(b'')
    data = arduino.readline().decode().strip()
    print("Received data:", data)
    global fireStatus
    if data:
        try:
            temp, fire = data.split(",")
            tempLabel.config(text="Temperature: {} C".format(temp))
            if fire != fireStatus:
                fireStatus = fire
                if fire == "0":
                    fireLabel.config(text="Fire Status: FIRE DETECTED!", fg="red")
                    arduino.write(b'BUZZER_ON\n')  # Buzzer ON
                else:
                    fireLabel.config(text="Fire Status: No Fire", fg="green")
                    arduino.write(b'BUZZER_OFF\n')  # Buzzer OFF

            cursor.execute("INSERT INTO tempLog (temperature, time) VALUES (%s, NOW())", (temp,))
            database.commit()

        except ValueError:
            pass

    root.after(1000, update_data)  # Refresh UI every second

update_data()
root.mainloop()

cursor.close()
database.close()