from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import json


# 1- fetch the data from the api
# 2- save the data to data/records.json
# 3- get the data from data/records.json
# 4- generate graphs and wordcloud
# 5- return data, station, date

def fetch_data(station, date):
    if date == '':
        date = '1990-01-01'
    url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&sort=date&facet=numer_sta&refine.nom=" + station.upper() + "&refine.date=" + date + "&fields=date,tc,u,ff,pmer"
    response = requests.get(url)
    data = response.json()
    indented_json = json.dumps(data, indent=4)

    # save response data to json file
    with open("data/records.json", "w") as outfile:
        outfile.write(indented_json)

    # opening records.json file
    with open('data/records.json', 'r') as recordsfile:
        # reading from records.json file
        records = json.load(recordsfile)

    heures = []
    temperatures = []
    vitesse = []
    humidite = []
    pression = []
    if len(records["records"]) > 0:
        for record in records["records"]:
            record_date = datetime.fromisoformat(record["fields"]["date"])
            heure = record_date.strftime("%H:%M")

            # append details to list
            heures.append(heure)
            temperatures.append(record["fields"]["tc"])
            vitesse.append(record["fields"]["ff"])
            humidite.append(record["fields"]["u"])
            pression.append(record["fields"]["pmer"])

        # plot graphs

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

        wordcloud = WordCloud().generate(station + date + json.dumps(records["records"]))
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig("static/images/wordcloud.png")
        plt.close()

        return records, station, date
    else:
        return 0
