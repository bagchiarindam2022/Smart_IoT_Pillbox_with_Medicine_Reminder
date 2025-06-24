import serial
import time

def send_schedule():
    try:
        arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)
        time.sleep(2)  # Wait for connection

        schedule_data = {
            "Monday": ["08:00", "12:00", "18:00"],
            "Tuesday": ["08:15", "12:15", "18:15"],
            "Wednesday": ["08:30", "12:30", "18:30"],
        }

        for day, slots in schedule_data.items():
            for idx, slot in enumerate(slots):
                if slot:
                    message = f"{day},{idx+1},{slot}\n"
                    arduino.write(message.encode())
                    time.sleep(0.5)

        print("Schedule sent!")
        arduino.close()
    except serial.SerialException:
        print("Arduino not connected. Skipping serial communication.")

if __name__ == "__main__":
    send_schedule()

