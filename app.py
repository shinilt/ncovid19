from flask import Flask, render_template
from flask import request
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

UPDATE_INTERVAL = 1800
def get_new_data_every(period=UPDATE_INTERVAL):

    while True:
        GenerateResources()
        print("data updated")
        time.sleep(period)

def GenerateResources():
    URL = 'https://www.worldometers.info/coronavirus/#countries'
    df = pd.read_html(URL)
    req_data = requests.get(URL)
    review_soup = BeautifulSoup(req_data.content, 'html.parser')
    df2 = df[0]
    df2.columns = ['Country Or Location', 'Total Cases', 'New Cases', 'Total Deaths', 'NewDeaths', 'ActiveCases',
                   'Total Recovered', 'Serious']
    df2.fillna(0)
    del df2['NewDeaths']
    del df2['Serious']
    # columns to convert to int
    cols = ['Total Cases', 'New Cases', 'Total Deaths', 'Total Recovered']
    df2[cols] = df2[cols].fillna(0).applymap(np.int64)


    #plot the bar chart of top 25 countries in logaarithmic scale
    plt.figure(figsize=(23, 10))
    plt.title('25 Countries with highest confirmed cases')
    plt.bar(df2['Country Or Location'][:25], df2['Total Cases'][:25], log=True)
    # save it as image here
    plt.savefig('static/barChart.png')

    #plot the pie chart of the share of infection burden
    labels = df2['Country Or Location'][:20]
    Cases = df2['Total Cases'][:20]
    # colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    # explode = (0.1, 0, 0, 0)  # explode 1st slice

    # Plot the pie chart
    plt.figure(figsize=(14, 10))
    # plt.pie(Cases,   shadow=False, startangle=90)
    patches, texts = plt.pie(Cases, shadow=False, startangle=90)  # removed the percentage display autopct='%1.1f%%'
    plt.legend(patches, labels, loc="best")
    plt.title('Country wise share of impact')
    plt.axis('equal')
    plt.savefig('static/PieChart.png')
    #close all plots to save memory
    plt.close("all")

    # write the dataframe html to file
    html = df2.to_html()
    text_file = open("templates/CountryList.html", "w")
    text_file.write(html)
    text_file.close()

# refresh the data , generate new data every 10 mins
#schedule.every(10).minutes.do(GenerateResources)

@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


@app.route("/countrylist", methods=['GET'])
def countrylist():
    return render_template("CountryList.html")

@app.route("/refresh", methods=['GET'])
def refresh():
    GenerateResources()
    return "Refresh completed"



if __name__ == "__main__":
    GenerateResources()

    # do all the shit u want to do before app run below
    app.run(debug=True)
    get_new_data_every(UPDATE_INTERVAL)


