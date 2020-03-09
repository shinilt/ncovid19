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
htmltable = ""

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
    df2 = df[0].iloc[:, [0, 1, 2, 3, 5, 6]]
    #rename the columns
    df2.columns = ['Country Or Location', 'Total Cases', 'New Cases', 'Total Deaths', 'Total Recovered', 'Active Cases']
    # columns to convert to int for visual appearance
    cols = ['Total Cases', 'Total Deaths', 'Total Recovered']
    df2 = df2.fillna(0)
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
    #create json from dataframe for the use in web javascript
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

@app.route("/home", methods=['GET'])
def home():
    return render_template("home.html")


@app.route("/", methods=['GET'])
def getJson():
    str1 = """
    <!DOCTYPE html>
<html>
<head>
    <title>Corona Virus Updates and Statistics</title>
	<!-- Load plotly.js into the DOM -->
	<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
</head>
<body>
<h1>NCOVID-19 Information and statistics</h1>
<h2>Cumulative cases</h2>
<div id='BarChartAllDiv'>
<h2>Active cases</h2>
<div id='BarChartActiveDiv'>
<h2>New cases</h2>
<div id='BarChartNewCaseDiv'>
<h2>Total Death stats</h2>
<div id='BarChartTotalDeathsDiv'>


<h2>Cumulative cases</h2>
<div id='PieChartAllDiv'>
<h2>Current Active cases</h2>
<div id='PieChartActiveDiv'>
<h2>New cases</h2>
<div id='PieChartNewCaseDiv'>
<h2>Total Deaths</h2>
<div id='PieChartTotalDeathsDiv'>

<h2>Complete list of affected areas</h2>
<p id="AffectedCountryTable">Pulling out the dat from several places.</p>


<div id='text1'>
<div id='text2'>
<script>
var txt = """
    str2 = GenerateResources()
    str3 = """
var obj = JSON.parse(txt);
Country=[];
TotalCases=[];
ActiveCases=[];
NewCases=[];
TotalDeaths=[];
txt = "<table border='1'><tr><th>Country Or Location</th><th>Total Cases</th><th>Total Deaths</th><th>Total Recovered</th><th>Active Cases</th></tr>"
      for (x in obj['Country Or Location']) {
      Country.push(obj['Country Or Location'][x]);
      TotalCases.push(obj['Total Cases'][x]);
      ActiveCases.push(obj['Active Cases'][x]);
      NewCases.push(obj['New Cases'][x]);
      TotalDeaths.push(obj['Total Deaths'][x]);
        txt += "<tr><td>" + obj['Country Or Location'][x] + "</td><td>"+ obj['Total Cases'][x]  +  "</td><td>"+ obj['Total Deaths'][x] + "</td><td>"+ obj['Total Recovered'][x] + "</td><td>"+ obj['Active Cases'][x]+"</td></tr>";
      }
      txt += "</table>"    
      document.getElementById("AffectedCountryTable").innerHTML = txt;
      Country.pop();
      TotalCases.pop();
      ActiveCases.pop();
      NewCases.pop();
      TotalDeaths.pop();
      
      var plotlayout = {  height: 400,  width: 500};
      
      var barchartdataAll = [  { x: Country,    y: TotalCases,    type: 'bar'  }];
      var barchartdataActive = [  { x: Country,    y: ActiveCases,    type: 'bar'  }];
      var barchartdataNewCase = [  { x: Country,    y: NewCases,    type: 'bar'  }];
      var barchartdataTotalDeaths = [  { x: Country,    y: TotalDeaths,    type: 'bar'  }];
      
      var piechartdataAll = [  { values:TotalCases ,    labels: Country ,    type: 'pie'  }];
      var piechartdataActive = [  { values:ActiveCases ,    labels: Country ,    type: 'pie'  }];
      var piechartdataNewCase = [  { values:NewCases ,    labels: Country ,    type: 'pie'  }];
      var piechartdataTotalDeaths = [  { values:TotalDeaths ,    labels: Country ,    type: 'pie'  }];
      

Plotly.newPlot('BarChartAllDiv', barchartdataAll, plotlayout);
Plotly.newPlot('BarChartActiveDiv', barchartdataActive, plotlayout);
Plotly.newPlot('BarChartNewCaseDiv', barchartdataNewCase, plotlayout);
Plotly.newPlot('BarChartTotalDeathsDiv', barchartdataTotalDeaths, plotlayout);

Plotly.newPlot('PieChartAllDiv', piechartdataAll, plotlayout);
Plotly.newPlot('PieChartActiveDiv', piechartdataActive, plotlayout);
Plotly.newPlot('PieChartNewCaseDiv', piechartdataNewCase, plotlayout);
Plotly.newPlot('PieChartTotalDeathsDiv', piechartdataTotalDeaths, plotlayout);



</script>
<!-- hitwebcounter Code START -->
<a href="https://www.hitwebcounter.com" target="_blank">
<img src="https://hitwebcounter.com/counter/counter.php?page=7206213&style=0038&nbdigits=9&type=page&initCount=0" title="User Stats" Alt="webcounterwebsite"   border="0" >
</a> 
</body>
</html>
    """
    return str1 + "'" + str2 + "';" + str3

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



