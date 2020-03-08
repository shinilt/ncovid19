from flask import Flask, render_template
from flask import request
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import time
import datetime
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import threading
import seaborn as sns

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("within auto refresh thread")
        get_new_data_every(1800.0)



app = Flask(__name__)
htmltable = ""
UPDATE_INTERVAL = 1800
def get_new_data_every(period):

    while True:
        GenerateResources()
        time.sleep(period)

def GenerateResources():
    URL = 'https://www.worldometers.info/coronavirus/#countries'
    df = pd.read_html(URL)
    req_data = requests.get(URL)
    review_soup = BeautifulSoup(req_data.content, 'html.parser')

    #copy only selected columns
    df2 = df[0].iloc[:, [0, 1, 2, 3, 5]]
    #rename the columns
    df2.columns = ['Country Or Location', 'Total Cases', 'New Cases', 'Total Deaths', 'Total Recovered']
    # columns to convert to int for visual appearance
    cols = ['Total Cases', 'Total Deaths', 'Total Recovered']
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
    plt.savefig('static/PieChart2.png')
    #close all plots to save memory
    plt.close("all")

    # write the dataframe html to file
    html = df2.to_html()
    dfJson = df2.to_json()
    print(dfJson)
    global htmltable
    htmltable = html
    text_file = open("templates/CountryList.html", "w")
    text_file.write(html)
    text_file.close()
    return dfJson

# refresh the data , generate new data every 10 mins
#schedule.every(10).minutes.do(GenerateResources)

@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


@app.route("/countrylist", methods=['GET'])
def countrylist():
    return htmltable

@app.route("/getjson", methods=['GET'])
def getJson():
    return render_template(json.html)

@app.route("/refresh", methods=['GET'])
def refresh():
    #create new thread
    refreshthread = myThread(2, "ManualRefreshThread")
    # Start new Threads
    refreshthread.setDaemon(True)
    refreshthread.start()
    return "Refresh completed"




if __name__ == "__main__":
    #Initial image and table generation
    GenerateResources()
    # create new thread for auto refresh of image and dataframe
    thread1 = myThread(1, "AutoLoadThread")
    # Start new Threads
    thread1.setDaemon(True)
    thread1.start()

    # do all the shit u want to do before app run below
    app.run(debug=True)



