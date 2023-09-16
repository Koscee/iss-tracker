import smtplib
import time
from math import fabs, floor

import requests
from datetime import datetime

# provide the sender and receiver's email info
SENDER_EMAIL = ''
SENDER_PASSWORD = ''
RECIPIENT_EMAIL = ''

MY_LAT = 36.7201600
MY_LNG = -4.4203400


def iss_is_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    # My position is within +5 or -5 degrees of the ISS position.
    return floor(fabs(iss_latitude - MY_LAT)) <= 5 and floor(fabs(iss_longitude - MY_LNG)) <= 5


def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LNG,
        "formatted": 0,
    }
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    time_now = datetime.now().hour

    return time_now >= sunset or time_now <= sunrise


def send_email():
    with smtplib.SMTP(host="smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        message = "Subject: Look Up 👆\n\n  The ISS is above you in the sky."
        connection.sendmail(from_addr=SENDER_EMAIL, to_addrs=RECIPIENT_EMAIL, msg=message)


# run every 60 seconds
while True:
    time.sleep(60)
    # ISS is close to my current position and it is currently dark
    if iss_is_overhead() and is_night():
        send_email()
