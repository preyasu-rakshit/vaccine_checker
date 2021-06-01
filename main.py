import requests
import json
from datetime import datetime
import pytz
import smtplib
from time import sleep
import schedule

emails = ['preyasu.official@gmail.com', 'shouryabhadra28@gmail.com', 'balajishaw16@gmail.com']

def generate_url():
    zone = pytz.timezone('Asia/Kolkata')
    tm = datetime.now(zone)
    date = f'{tm.day}-{tm.month}-{tm.year}'

    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=730&date={date}"
    return url


def get_data():
    response = requests.get(generate_url())    
    data = json.loads(response.text)
    print(response.text)

    available_centers = []
    names = []
    for d in data['centers']:
        for s in d['sessions']:
            if s['available_capacity_dose1'] > 0 and s['min_age_limit'] == 18:
                center = {
                    'name': d['name'],
                    'address': d['address'],
                    'quantity': s['available_capacity_dose1']
                }

                if d['name'] not in names:
                    available_centers.append(center)
                    names.append(d['name'])

    print(available_centers)
    return available_centers


def send_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('preyasujph@gmail.com', 'odydhtybyfkfmlih')

    centers = get_data()
    subject = 'Vaccine Slots Available!!'

    if len(centers) > 0:

        body = ''
        cowin = 'Book on: https://www.cowin.gov.in/home'
        for center in centers:
            para = f'{center["quantity"]} slots are available at {center["name"]}, {center["address"]}.\n\n'
            body += para

        msg = f'Subject: {subject}\n\n{body + cowin}'
        print(msg)
        for email in emails:
            server.sendmail('preyasujph@gmail.com', email, msg)


if __name__ == "__main__":
    schedule.every(5).minutes.do(send_mail)
    send_mail()

    while True:
        schedule.run_pending()
        sleep(1)