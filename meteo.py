from flask import Flask, render_template, request, session
from prettytable import PrettyTable
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from wordcloud import WordCloud
from datetime import datetime
from functions import *
import requests
import json
import os

# get the station name
station = input("Saisez le nom de la station: ").upper()
print(station)
date = ''


# validate the date
def validate_date():
    dt = input("Saisez la date (YYYY-MM-DD): ")
    global date
    date = dt
    date_format = '%Y-%m-%d'
    try:
        # formatting the date using strptime() function
        datetime.strptime(date, date_format)

    # If the date validation goes wrong
    except ValueError:
        return 0
    return date


while validate_date() == 0:
    print("Please enter a valid date YYYY-MM-DD")

# Fetch the station data
url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&sort=date&facet=numer_sta&refine.nom=" + station + "&refine.date=" + date + "&fields=date,tc,u,ff,pmer"
response = requests.get(url)
data = response.json()

indented = json.dumps(data, indent=4)
# Print the response json
if len(data["records"]) > 0:
    print(indented)

    # create data directory if it does not exist
    isExist = os.path.exists("data")

    print("\n")
    if not isExist:
        os.makedirs("data")
        print("data directory has been created successfully.")

    # save response data to json file
    with open("data/records.json", "w") as outfile:
        outfile.write(indented)
        print("data saved to records.json file successfully.")
    print("\n")

    # opening records.json file
    with open('data/records.json', 'r') as recordsfile:
        # reading from records.json file
        records = json.load(recordsfile)

    # format the date from YYYY-MM-DD to e.g. 20 February 2019 to use it in the table
    date_f = datetime.fromisoformat(date)

    date_full = date_f.strftime("%d %B %Y")

    # Print the table
    x = PrettyTable()
    x.field_names = ["Heure", "T(°C)", "Humidité(%)", "Vitesse du vent moyen 10 mn (m/s)",
                     "Pression au niveau mer (Pa)"]

    heures = []
    temperatures = []
    vitesse = []
    humidite = []
    pression = []

    for record in records["records"]:
        record_date = datetime.fromisoformat(record["fields"]["date"])
        heure = record_date.strftime("%H:%M")
        x.add_row([heure, "{:.1f}".format(record["fields"]["tc"]), record["fields"]["u"], record["fields"]["ff"],
                   record["fields"]["pmer"]])

        # append details to list
        heures.append(heure)
        temperatures.append(record["fields"]["tc"])
        vitesse.append(record["fields"]["ff"])
        humidite.append(record["fields"]["u"])
        pression.append(record["fields"]["pmer"])

    print(x.get_string(title="Station: " + station + ", numéro " + records["facet_groups"][0]["facets"][0][
        "name"] + "  - Date: " + date_full))

    # plot graphs with matplotlib

    # temperature graphique
    x = heures
    y = temperatures
    plt.plot(x, y, color='#fb7819')
    plt.xlabel('Heures', color='#1e8bc3')
    plt.ylabel('Temperature (°C)', color='#e74c3c')
    plt.title('Temperature in ' + station, color='#34495e')
    plt.savefig("static/images/temperatures.png")
    plt.close()

    # vitesse graphique
    x = heures
    y = vitesse
    plt.plot(x, y, color='#2596be')
    plt.xlabel('Heures', color='#1e8bc3')
    plt.ylabel('Vitesse (m/s)', color='#e74c3c')
    plt.title('Vitesse du vent moyen 10 mn (m/s) : ' + station, color='#34495e')
    plt.savefig("static/images/vitesse.png")
    plt.close()

    # Humidité graphique
    x = heures
    y = humidite
    plt.bar(x, y, color='#be2596')
    plt.xlabel('Heures', color='#1e8bc3')
    plt.ylabel('Humidité (%)', color='#e74c3c')
    plt.title('Humidité (%) : ' + station, color='#34495e')
    plt.savefig("static/images/humidite.png")
    plt.close()

    # Pression graphique
    x = heures
    y = humidite
    plt.stem(x, y, linefmt='#3ba1c5', markerfmt='D')
    plt.xlabel('Heures', color='#1e8bc3')
    plt.ylabel('Pression (Pa)', color='#e74c3c')
    plt.title('Pression au niveau mer (Pa) : ' + station, color='#34495e')
    plt.savefig("static/images/pression.png")
    plt.close()

    # generate wordcloud

    wordcloud = WordCloud().generate(station + " " + date + " " + json.dumps(records["records"]))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("static/images/wordcloud.png")
    plt.close()

    app = Flask(__name__)

    # use app secret key for sessions
    app.secret_key = b'_5#y2L"Q8z\n\xec]/'


    @app.route("/", methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if fetch_data(request.form['nom_station'], request.form['date']) == 0:
                return render_template('index.html', data=0)
            else:
                session["station"] = request.form['nom_station']
                session["date"] = request.form['date']
                data_records, st, dt = fetch_data(request.form['nom_station'], request.form['date'])
                return render_template('index.html', data=[data_records, st, dt])
        else:
            if session.get("station") is None:
                return render_template('index.html', data=[records, station, date])
            else:
                return render_template('index.html', data=[records, session.get("station"), session.get("date")])



    app.run()
else:
    print("No records found, please try again!")