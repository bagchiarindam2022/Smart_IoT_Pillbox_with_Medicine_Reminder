import streamlit as st
import smtplib
import schedule
import time
import serial
import requests
from datetime import datetime, timedelta
from threading import Thread
from email.mime.text import MIMEText

# ---------------------- Email Sending Function ----------------------e
def send_email(email, subject, body):
    sender_email = 'teamnexusofficial25@gmail.com'
    sender_password = 'qkmm yqcq vqtm vmoq'  # Use an app password for security

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ---------------------- Schedule Medicine Reminders ----------------------
def schedule_emails(email, name, schedule_data):
    for day, slots in schedule_data.items():
        for slot in slots:
            if slot:
                med_time = datetime.combine(datetime.today(), slot)
                reminder_time = med_time - timedelta(minutes=5)
                follow_up_time = med_time + timedelta(minutes=5)

                # Reminder Email (5 mins before)
                schedule.every().day.at(reminder_time.strftime("%H:%M")).do(
                    send_email,
                    email=email,
                    subject="Team Nexus - Medicine Reminder",
                    body=f"Dear {name},\n\nThis is a reminder to take your medicine at {slot.strftime('%I:%M %p')}.\n\nBest regards,\nTeam Nexus"
                )

                # Follow-up Email (5 mins after)
                schedule.every().day.at(follow_up_time.strftime("%H:%M")).do(
                    send_email,
                    email=email,
                    subject="Team Nexus - Medicine Follow-Up",
                    body=f"Dear {name},\n\nDid you take your medicine at {slot.strftime('%I:%M %p')}?\nPlease confirm.\n\nBest regards,\nTeam Nexus"
                )

# ---------------------- Send Schedule to Arduino (USB) ----------------------
def send_schedule_serial(schedule_data):
    try:
        arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)  # Change COM port as needed
        time.sleep(2)  # Wait for connection

        for day, slots in schedule_data.items():
            for idx, slot in enumerate(slots):
                if slot:
                    message = f"{day},{idx+1},{slot.strftime('%H:%M')}\n"
                    arduino.write(message.encode())
                    time.sleep(0.5)  # Small delay to ensure data is sent

        arduino.close()
        st.success("Schedule sent to Arduino (USB) successfully!")
    except Exception as e:
        st.error(f"Failed to send data to Arduino (USB): {e}")

# ---------------------- Send Schedule to Arduino (Wi-Fi) ----------------------
def send_schedule_wifi(schedule_data, esp_ip):
    try:
        url = f"http://{esp_ip}/update_schedule"
        data = {"schedule": schedule_data}
        response = requests.post(url, json=data)

        if response.status_code == 200:
            st.success("Schedule sent to Arduino (Wi-Fi) successfully!")
        else:
            st.error("Failed to send schedule via Wi-Fi")
    except Exception as e:
        st.error(f"Wi-Fi Error: {e}")

# ---------------------- Background Email Scheduler ----------------------
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# ---------------------- Streamlit UI ----------------------
st.title("Medicine Reminder & Schedule Updater")

# User Inputs
st.subheader("Patient Information")
name = st.text_input("Enter the patient's name")
email = st.text_input("Enter the email address")

# Medicine Schedule Input
st.subheader("Set Medicine Schedule")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
schedule_data = {}

for day in days:
    st.markdown(f"### {day}")
    slot1 = st.time_input(f"Slot 1 Time - {day}", key=f"{day}_slot1")
    slot2 = st.time_input(f"Slot 2 Time - {day}", key=f"{day}_slot2")
    slot3 = st.time_input(f"Slot 3 Time - {day}", key=f"{day}_slot3")
    schedule_data[day] = [slot1, slot2, slot3]

# Select Communication Method
st.subheader("Send Schedule to Arduino")
send_method = st.radio("Choose connection method", ["USB (Serial)", "Wi-Fi (ESP8266/ESP32)"])

if send_method == "Wi-Fi (ESP8266/ESP32)":
    esp_ip = st.text_input("Enter ESP8266/ESP32 IP Address")

if st.button("Send Schedule"):
    if name and email:
        schedule_emails(email, name, schedule_data)  # Schedule Emails

        if send_method == "USB (Serial)":
            send_schedule_serial(schedule_data)  # Send via Serial (USB)
        elif send_method == "Wi-Fi (ESP8266/ESP32)":
            if esp_ip:
                send_schedule_wifi(schedule_data, esp_ip)  # Send via Wi-Fi
            else:
                st.error("Enter ESP8266/ESP32 IP Address!")

        st.success("Reminders scheduled & Arduino updated!")
    else:
        st.error("Please enter both name and email address!")