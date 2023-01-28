import requests
import json
from datetime import datetime
import pytz
import smtplib
from time import sleep
import schedule

emails = ['test@email.com', 'test2@email.com']
#add more emails as per your needs

def generate_url():
    zone = pytz.timezone('Asia/Kolkata')
    tm = datetime.now(zone)
    date = f'{tm.day}-{tm.month}-{tm.year}'

    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=730&date={date}"
    return url


def get_data():
    response = requests.get(generate_url())    
    data = json.loads(response.text)
    # print(response.text)

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

    server.login('ENTER YOUR EMAIL HERE', 'PASSWORD HERE')

    centers = get_data()
    subject = 'Vaccine Slots Available!!'

    if len(centers) > 0:

        body = ''
        cowin = 'Book on: https://www.cowin.gov.in/home \n'
        for center in centers:
            para = f'{center["quantity"]} slots are available at {center["name"]}, {center["address"]}.\n\n'
            body += para

        zone = pytz.timezone('Asia/Kolkata')
        update = f'Database updated on :{datetime.now(zone)}'
        msg = f'Subject: {subject}\n\n{body + cowin + update}'
        # print(msg)
        for email in emails:
            server.sendmail('EMAIL', email, msg)


if __name__ == "__main__":
    schedule.every(5).minutes.do(send_mail)
    send_mail()

    while True:
        schedule.run_pending()
        sleep(1)
