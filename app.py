from flask import Flask, render_template
from flask import request, Response
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
from lxml import etree


class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("within auto refresh thread")
        get_new_data_every(1800.0)



app = Flask(__name__)
dataframejson = ""

def get_new_data_every(period):

    while True:
        global dataframejson
        dataframejson = GenerateResources()
        time.sleep(period)

def GenerateResources():
    URL = 'https://www.worldometers.info/coronavirus/#countries'
    df = pd.read_html(URL)
    req_data = requests.get(URL)
    review_soup = BeautifulSoup(req_data.content, 'html.parser')

    #copy only required columns
    df2 = df[0].iloc[:, [0, 1, 2, 3, 5, 6]]
    #rename the columns
    df2.columns = ['Country Or Location', 'Total Cases', 'New Cases', 'Total Deaths', 'Total Recovered', 'Active Cases']
    # columns to convert to int for visual appearance
    cols = ['Total Cases', 'Total Deaths', 'Total Recovered']
    df2 = df2.fillna(0)
    df2[cols] = df2[cols].fillna(0).applymap(np.int64)
    """
    #commenting the entire section as the plot and table generation moved to javascript
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

    # Plot the pie chart. 
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
    # write the dataframe html to file. Heroku is not letting save the files. Not suing now as the design changed
    html = df2.to_html()
    text_file = open("templates/CountryList.html", "w")
    text_file.write(html)
    text_file.close() 
    """

    #create json from dataframe for the use in web javascript
    dfJson = df2.to_json()
    return dfJson




@app.route("/", methods=['GET'])
def Index():
    return render_template("index.html")


@app.route("/getdata", methods=['GET'])
def getdata():
    # this method will fetch the current value of the complete dataframe json and return
    global dataframejson
    return Response(dataframejson, 200)



if __name__ == "__main__":
    # create new thread for auto refresh of the dataframe
    thread1 = myThread(1, "AutoLoadThread")
    # Start new Threads
    thread1.setDaemon(True)
    thread1.start()

    # do all the shit u want to do before app run below
    app.run(debug=True)



