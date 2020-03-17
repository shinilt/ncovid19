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
import html5lib
import json


class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("within auto refresh thread")
        get_new_data_every(1800.0)



app = Flask(__name__)
mydataframe = ""
dataframejson = ""
mapdatajson=""

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
    df2['New Cases'] = df2['New Cases'].str.replace(',', '')
    df2['New Cases'] = df2['New Cases'].str.replace('+', '')
    df2 = df2.fillna(0)
    df2[cols] = df2[cols].fillna(0).applymap(np.int64)
    """
    #commenting the entire section as the plot and table generation moved to javascript
    #plot the bar chart of top 25 countries in logarithmic scale
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
    global mydataframe
    #save the dataframe as varable for use from anywhere
    mydataframe=df2
    return dfJson




@app.route("/", methods=['GET'])
def Index():
    return render_template("index.html")


@app.route("/getdata", methods=['GET'])
def getdata():
    # this method will fetch the current value of the complete dataframe json and return
    global dataframejson
    if len(dataframejson) > 1:
        return Response(dataframejson, 200)
    else:
        dataframejson = GenerateResources()
        return Response(dataframejson, 200)

@app.route("/manualrefresh", methods=['GET'])
def manualrefresh():
    # this is to manually verify the data correctness
    global dataframejson
    dataframejson = GenerateResources()
    return GenerateResources()

@app.route("/maps", methods=['GET'])
def maps():
    # this is to render the map page with details
    return render_template("maps.html")

@app.route("/getmapdata", methods=['GET'])
def getmapdata():
    # this is to supply the info for plotting data on the map
    global mydataframe
    global mapdatajson
    returndata = '{'
    try:
        for country in mydataframe['Country Or Location']:
            #the latlondata is the location data for all the countries
            latlondata = {"Andorra": {"lat": "42.546245", "lon": "1.6015540000000001"},
                      "UAE": {"lat": "23.424076", "lon": "53.847818000000004"},
                      "Afghanistan": {"lat": "33.93911", "lon": "67.709953"},
                      "Antigua and Barbuda": {"lat": "17.060816", "lon": "-61.796428000000006"},
                      "Anguilla": {"lat": "18.220554", "lon": "-63.068615"},
                      "Albania": {"lat": "41.153332", "lon": "20.168331"},
                      "Armenia": {"lat": "40.069099", "lon": "45.038189"},
                      "Netherlands Antilles": {"lat": "12.226078999999999", "lon": "-69.060087"},
                      "Angola": {"lat": "-11.202691999999999", "lon": "17.873887"},
                      "Antarctica": {"lat": "-75.250973", "lon": "-0.071389"},
                      "Argentina": {"lat": "-38.416097", "lon": "-63.616671999999994"},
                      "American Samoa": {"lat": "-14.270972", "lon": "-170.132217"},
                      "Austria": {"lat": "47.516231", "lon": "14.550072"},
                      "Australia": {"lat": "-25.274398", "lon": "133.775136"},
                      "Aruba": {"lat": "12.52111", "lon": "-69.968338"},
                      "Azerbaijan": {"lat": "40.143105", "lon": "47.576927000000005"},
                      "Bosnia and Herzegovina": {"lat": "43.915886", "lon": "17.679076000000002"},
                      "Barbados": {"lat": "13.193887", "lon": "-59.543198"},
                      "Bangladesh": {"lat": "23.684994", "lon": "90.35633100000001"},
                      "Belgium": {"lat": "50.503887", "lon": "4.469936"},
                      "Burkina Faso": {"lat": "12.238333", "lon": "-1.561593"},
                      "Bulgaria": {"lat": "42.733883", "lon": "25.48583"},
                      "Bahrain": {"lat": "25.930414000000003", "lon": "50.637772"},
                      "Burundi": {"lat": "-3.3730559999999996", "lon": "29.918885999999997"},
                      "Benin": {"lat": "9.30769", "lon": "2.315834"},
                      "Bermuda": {"lat": "32.321384", "lon": "-64.75737"},
                      "Brunei": {"lat": "4.535277", "lon": "114.72766899999999"},
                      "Bolivia": {"lat": "-16.290154", "lon": "-63.588653"},
                      "Brazil": {"lat": "-14.235004", "lon": "-51.92528"},
                      "Bahamas": {"lat": "25.03428", "lon": "-77.39628"},
                      "Bhutan": {"lat": "27.514162", "lon": "90.433601"},
                      "Bouvet Island": {"lat": "-54.423199", "lon": "3.4131940000000003"},
                      "Botswana": {"lat": "-22.328474", "lon": "24.684866"},
                      "Belarus": {"lat": "53.709807", "lon": "27.953389"},
                      "Belize": {"lat": "17.189877", "lon": "-88.49765"},
                      "Canada": {"lat": "56.130366", "lon": "-106.34677099999999"},
                      "Cocos [Keeling] Islands": {"lat": "-12.164164999999999", "lon": "96.870956"},
                      "DRC": {"lat": "-4.038333000000001", "lon": "21.758664000000003"},
                      "CAR": {"lat": "6.611111", "lon": "20.939444"},
                      "Congo [Republic]": {"lat": "-0.228021", "lon": "15.827658999999999"},
                      "Switzerland": {"lat": "46.818188", "lon": "8.227511999999999"},
                      "Ivory Coast": {"lat": "7.539989", "lon": "-5.54708"},
                      "Cook Islands": {"lat": "-21.236735999999997", "lon": "-159.777671"},
                      "Chile": {"lat": "-35.675146999999996", "lon": "-71.542969"},
                      "Cameroon": {"lat": "7.369722", "lon": "12.354722"},
                      "China": {"lat": "35.86166", "lon": "104.195397"},
                      "Colombia": {"lat": "4.570868", "lon": "-74.297333"},
                      "Costa Rica": {"lat": "9.748917", "lon": "-83.753428"},
                      "Cuba": {"lat": "21.521757", "lon": "-77.78116700000001"},
                      "Cape Verde": {"lat": "16.002082", "lon": "-24.013197"},
                      "Christmas Island": {"lat": "-10.447525", "lon": "105.690449"},
                      "Cyprus": {"lat": "35.126413", "lon": "33.429859"},
                      "Czechia": {"lat": "49.817492", "lon": "15.472961999999999"},
                      "Germany": {"lat": "51.165690999999995", "lon": "10.451526"},
                      "Djibouti": {"lat": "11.825138", "lon": "42.590275"},
                      "Denmark": {"lat": "56.26392", "lon": "9.501785"},
                      "Dominica": {"lat": "15.414999", "lon": "-61.370976"},
                      "Dominican Republic": {"lat": "18.735692999999998", "lon": "-70.162651"},
                      "Algeria": {"lat": "28.033886", "lon": "1.6596259999999998"},
                      "Ecuador": {"lat": "-1.8312389999999998", "lon": "-78.183406"},
                      "Estonia": {"lat": "58.595271999999994", "lon": "25.013607"},
                      "Egypt": {"lat": "26.820553000000004", "lon": "30.802497999999996"},
                      "Western Sahara": {"lat": "24.215526999999998", "lon": "-12.885834"},
                      "Eritrea": {"lat": "15.179383999999999", "lon": "39.782334000000006"},
                      "Spain": {"lat": "40.463667", "lon": "-3.7492199999999998"},
                      "Ethiopia": {"lat": "9.145", "lon": "40.489672999999996"},
                      "Finland": {"lat": "61.92411", "lon": "25.748151"},
                      "Fiji": {"lat": "-16.578193", "lon": "179.414413"},
                      "Falkland Islands [Islas Malvinas]": {"lat": "-51.796253", "lon": "-59.523613"},
                      "Micronesia": {"lat": "7.425553999999999", "lon": "150.550812"},
                      "Faeroe Islands": {"lat": "61.892635", "lon": "-6.9118059999999995"},
                      "France": {"lat": "46.227638", "lon": "2.213749"},
                      "Gabon": {"lat": "-0.803689", "lon": "11.609444"},
                      "UK": {"lat": "55.378051", "lon": "-3.435973"},
                      "Grenada": {"lat": "12.262775999999999", "lon": "-61.604170999999994"},
                      "Georgia": {"lat": "42.315407", "lon": "43.356891999999995"},
                      "French Guiana": {"lat": "3.9338889999999997", "lon": "-53.125781999999994"},
                      "Channel Islands": {"lat": "49.465691", "lon": "-2.5852779999999997"},
                      "Ghana": {"lat": "7.946527000000001", "lon": "-1.0231940000000002"},
                      "Gibraltar": {"lat": "36.137741", "lon": "-5.345374"},
                      "Greenland": {"lat": "71.706936", "lon": "-42.604303"},
                      "Gambia": {"lat": "13.443182", "lon": "-15.310139000000001"},
                      "Guinea": {"lat": "9.945587", "lon": "-9.696645"},
                      "Guadeloupe": {"lat": "16.995971", "lon": "-62.067641"},
                      "Equatorial Guinea": {"lat": "1.6508009999999997", "lon": "10.267895"},
                      "Greece": {"lat": "39.074208", "lon": "21.824312"},
                      "South Georgia and the South Sandwich Islands": {"lat": "-54.429579000000004",
                                                                       "lon": "-36.587909"},
                      "Guatemala": {"lat": "15.783470999999999", "lon": "-90.23075899999999"},
                      "Guam": {"lat": "13.444304", "lon": "144.793731"},
                      "Guinea-Bissau": {"lat": "11.803749", "lon": "-15.180413"},
                      "Guyana": {"lat": "4.860416000000001", "lon": "-58.93018000000001"},
                      "Gaza Strip": {"lat": "31.354676", "lon": "34.308825"},
                      "Hong Kong": {"lat": "22.396428", "lon": "114.10949699999999"},
                      "Heard Island and McDonald Islands": {"lat": "-53.08181", "lon": "73.50415799999999"},
                      "Honduras": {"lat": "15.199998999999998", "lon": "-86.241905"},
                      "Croatia": {"lat": "45.1", "lon": "15.2"},
                      "Haiti": {"lat": "18.971187", "lon": "-72.28521500000001"},
                      "Hungary": {"lat": "47.162494", "lon": "19.503304"},
                      "Indonesia": {"lat": "-0.789275", "lon": "113.921327"},
                      "Ireland": {"lat": "53.41291", "lon": "-8.243889999999999"},
                      "Israel": {"lat": "31.046051000000002", "lon": "34.851612"},
                      "Isle of Man": {"lat": "54.236107", "lon": "-4.548056"},
                      "India": {"lat": "20.593684", "lon": "78.96288"},
                      "British Indian Ocean Territory": {"lat": "-6.343194", "lon": "71.87651899999999"},
                      "Iraq": {"lat": "33.223191", "lon": "43.679291"},
                      "Iran": {"lat": "32.427908", "lon": "53.68804599999999"},
                      "Iceland": {"lat": "64.96305100000001", "lon": "-19.020835"},
                      "Italy": {"lat": "41.87194", "lon": "12.56738"},
                      "Jersey": {"lat": "49.214439", "lon": "-2.13125"},
                      "Jamaica": {"lat": "18.109581", "lon": "-77.297508"},
                      "Jordan": {"lat": "30.585164000000002", "lon": "36.238414"},
                      "Japan": {"lat": "36.204824", "lon": "138.252924"},
                      "Kenya": {"lat": "-0.023559", "lon": "37.906193"},
                      "Kyrgyzstan": {"lat": "41.20438", "lon": "74.766098"},
                      "Cambodia": {"lat": "12.565679", "lon": "104.990963"},
                      "Kiribati": {"lat": "-3.3704169999999998", "lon": "-168.734039"},
                      "Comoros": {"lat": "-11.875001", "lon": "43.872219"},
                      "Saint Kitts and Nevis": {"lat": "17.357822", "lon": "-62.782998"},
                      "North Korea": {"lat": "40.339852", "lon": "127.510093"},
                      "S. Korea": {"lat": "35.907757000000004", "lon": "127.766922"},
                      "Kuwait": {"lat": "29.311659999999996", "lon": "47.481766"},
                      "Cayman Islands": {"lat": "19.513469", "lon": "-80.566956"},
                      "Kazakhstan": {"lat": "48.019573", "lon": "66.923684"},
                      "Laos": {"lat": "19.856270000000002", "lon": "102.495496"},
                      "Lebanon": {"lat": "33.854721000000005", "lon": "35.862285"},
                      "Saint Lucia": {"lat": "13.909444", "lon": "-60.97889300000001"},
                      "Liechtenstein": {"lat": "47.166000000000004", "lon": "9.555373"},
                      "Sri Lanka": {"lat": "7.873054", "lon": "80.77179699999999"},
                      "Liberia": {"lat": "6.4280550000000005", "lon": "-9.429499"},
                      "Lesotho": {"lat": "-29.609988", "lon": "28.233608"},
                      "Lithuania": {"lat": "55.169438", "lon": "23.881275"},
                      "Luxembourg": {"lat": "49.815273", "lon": "6.129583"},
                      "Latvia": {"lat": "56.879635", "lon": "24.603189"},
                      "Libya": {"lat": "26.3351", "lon": "17.228331"},
                      "Morocco": {"lat": "31.791702", "lon": "-7.09262"},
                      "Monaco": {"lat": "43.750298", "lon": "7.412841"},
                      "Moldova": {"lat": "47.411631", "lon": "28.369884999999996"},
                      "Montenegro": {"lat": "42.708678000000006", "lon": "19.37439"},
                      "Madagascar": {"lat": "-18.766947000000002", "lon": "46.869107"},
                      "Marshall Islands": {"lat": "7.131474000000001", "lon": "171.184478"},
                      "North Macedonia": {"lat": "41.608635", "lon": "21.745275"},
                      "Mali": {"lat": "17.570692", "lon": "-3.9961660000000006"},
                      "Myanmar [Burma]": {"lat": "21.913965", "lon": "95.956223"},
                      "Mongolia": {"lat": "46.862496", "lon": "103.84665600000001"},
                      "Macao": {"lat": "22.198745000000002", "lon": "113.543873"},
                      "Northern Mariana Islands": {"lat": "17.33083", "lon": "145.38468999999998"},
                      "Martinique": {"lat": "14.641528", "lon": "-61.024174"},
                      "Mauritania": {"lat": "21.00789", "lon": "-10.940835"},
                      "Montserrat": {"lat": "16.742498", "lon": "-62.187366000000004"},
                      "Malta": {"lat": "35.937496", "lon": "14.375416"},
                      "Mauritius": {"lat": "-20.348404000000002", "lon": "57.552152"},
                      "Maldives": {"lat": "3.202778", "lon": "73.22068"},
                      "Malawi": {"lat": "-13.254307999999998", "lon": "34.301525"},
                      "Mexico": {"lat": "23.634501", "lon": "-102.552784"},
                      "Malaysia": {"lat": "4.210483999999999", "lon": "101.97576600000001"},
                      "Mozambique": {"lat": "-18.665695", "lon": "35.529562"},
                      "Namibia": {"lat": "-22.957639999999998", "lon": "18.49041"},
                      "New Caledonia": {"lat": "-20.904304999999997", "lon": "165.618042"},
                      "Niger": {"lat": "17.607789", "lon": "8.081666"},
                      "Norfolk Island": {"lat": "-29.040834999999998", "lon": "167.954712"},
                      "Nigeria": {"lat": "9.081999", "lon": "8.675277000000001"},
                      "Nicaragua": {"lat": "12.865416", "lon": "-85.207229"},
                      "Netherlands": {"lat": "52.132633", "lon": "5.291266"},
                      "Norway": {"lat": "60.472024", "lon": "8.468946"},
                      "Nepal": {"lat": "28.394857000000002", "lon": "84.12400799999999"},
                      "Nauru": {"lat": "-0.522778", "lon": "166.931503"},
                      "Niue": {"lat": "-19.054445", "lon": "-169.867233"},
                      "New Zealand": {"lat": "-40.900557", "lon": "174.88597099999998"},
                      "Oman": {"lat": "21.512583", "lon": "55.923255000000005"},
                      "Panama": {"lat": "8.537981", "lon": "-80.782127"},
                      "Peru": {"lat": "-9.189967", "lon": "-75.015152"},
                      "French Polynesia": {"lat": "-17.679742", "lon": "-149.40684299999998"},
                      "Papua New Guinea": {"lat": "-6.314993", "lon": "143.95555"},
                      "Philippines": {"lat": "12.879721", "lon": "121.77401699999999"},
                      "Pakistan": {"lat": "30.375321000000003", "lon": "69.345116"},
                      "Poland": {"lat": "51.919438", "lon": "19.145135999999997"},
                      "Saint Pierre and Miquelon": {"lat": "46.941936", "lon": "-56.27111"},
                      "Pitcairn Islands": {"lat": "-24.703615", "lon": "-127.43930800000001"},
                      "Puerto Rico": {"lat": "18.220833", "lon": "-66.590149"},
                      "Palestine": {"lat": "31.952162", "lon": "35.233154"},
                      "Portugal": {"lat": "39.399871999999995", "lon": "-8.224454"},
                      "Palau": {"lat": "7.51498", "lon": "134.58252"},
                      "Paraguay": {"lat": "-23.442503", "lon": "-58.44383199999999"},
                      "Qatar": {"lat": "25.354826", "lon": "51.183884"},
                      "Réunion": {"lat": "-21.115141", "lon": "55.536384"},
                      "Romania": {"lat": "45.943160999999996", "lon": "24.96676"},
                      "Serbia": {"lat": "44.016521000000004", "lon": "21.005859"},
                      "Russia": {"lat": "61.52401", "lon": "105.31875600000001"},
                      "Rwanda": {"lat": "-1.940278", "lon": "29.873888"},
                      "Saudi Arabia": {"lat": "23.885942", "lon": "45.079162"},
                      "Solomon Islands": {"lat": "-9.645710000000001", "lon": "160.156194"},
                      "Seychelles": {"lat": "-4.679574", "lon": "55.491977"},
                      "Sudan": {"lat": "12.862807", "lon": "30.217636"},
                      "Sweden": {"lat": "60.128161", "lon": "18.643501"},
                      "Singapore": {"lat": "1.352083", "lon": "103.819836"},
                      "Saint Helena": {"lat": "-24.143473999999998", "lon": "-10.030696"},
                      "Slovenia": {"lat": "46.151241", "lon": "14.995463"},
                      "Svalbard and Jan Mayen": {"lat": "77.553604", "lon": "23.670272"},
                      "Slovakia": {"lat": "48.669026", "lon": "19.699023999999998"},
                      "Sierra Leone": {"lat": "8.460555000000001", "lon": "-11.779889"},
                      "San Marino": {"lat": "43.94236", "lon": "12.457777"},
                      "Senegal": {"lat": "14.497401000000002", "lon": "-14.452361999999999"},
                      "Somalia": {"lat": "5.152149", "lon": "46.199616"},
                      "Suriname": {"lat": "3.9193050000000005", "lon": "-56.02778299999999"},
                      "São Tomé and Príncipe": {"lat": "0.18636", "lon": "6.613081"},
                      "El Salvador": {"lat": "13.794185", "lon": "-88.89653"},
                      "Syria": {"lat": "34.802075", "lon": "38.996815000000005"},
                      "Swaziland": {"lat": "-26.522503000000004", "lon": "31.465866"},
                      "Turks and Caicos Islands": {"lat": "21.694025", "lon": "-71.797928"},
                      "Chad": {"lat": "15.454166", "lon": "18.732207"},
                      "French Southern Territories": {"lat": "-49.280366", "lon": "69.348557"},
                      "Togo": {"lat": "8.619543", "lon": "0.824782"},
                      "Thailand": {"lat": "15.870032", "lon": "100.992541"},
                      "Tajikistan": {"lat": "38.861034000000004", "lon": "71.276093"},
                      "Tokelau": {"lat": "-8.967363", "lon": "-171.855881"},
                      "Timor-Leste": {"lat": "-8.874217", "lon": "125.727539"},
                      "Turkmenistan": {"lat": "38.969719", "lon": "59.556278000000006"},
                      "Tunisia": {"lat": "33.886917", "lon": "9.537499"},
                      "Tonga": {"lat": "-21.178986", "lon": "-175.198242"},
                      "Turkey": {"lat": "38.963745", "lon": "35.243322"},
                      "Trinidad and Tobago": {"lat": "10.691803", "lon": "-61.222503"},
                      "Tuvalu": {"lat": "-7.109535", "lon": "177.64933"},
                      "Taiwan": {"lat": "23.69781", "lon": "120.96051499999999"},
                      "Tanzania": {"lat": "-6.369028", "lon": "34.888822"},
                      "Ukraine": {"lat": "48.379433", "lon": "31.16558"},
                      "Uganda": {"lat": "1.373333", "lon": "32.290275"},
                      "U.S. Minor Outlying Islands": {"lat": "nan", "lon": "nan"},
                      "USA": {"lat": "37.09024", "lon": "-95.712891"},
                      "Uruguay": {"lat": "-32.522779", "lon": "-55.765834999999996"},
                      "Uzbekistan": {"lat": "41.377491", "lon": "64.585262"},
                      "Vatican City": {"lat": "41.902916", "lon": "12.453389"},
                      "St. Vincent Grenadines": {"lat": "12.984305", "lon": "-61.287228000000006"},
                      "Venezuela": {"lat": "6.42375", "lon": "-66.58973"},
                      "British Virgin Islands": {"lat": "18.420695000000002", "lon": "-64.63996800000001"},
                      "U.S. Virgin Islands": {"lat": "18.335765", "lon": "-64.896335"},
                      "Vietnam": {"lat": "14.058323999999999", "lon": "108.277199"},
                      "Vanuatu": {"lat": "-15.376706", "lon": "166.959158"},
                      "Wallis and Futuna": {"lat": "-13.768752", "lon": "-177.156097"},
                      "Samoa": {"lat": "-13.759029", "lon": "-172.10462900000002"},
                      "Kosovo": {"lat": "42.602636", "lon": "20.902977"},
                      "Yemen": {"lat": "15.552726999999999", "lon": "48.516388"},
                      "Mayotte": {"lat": "-12.8275", "lon": "45.166244"},
                      "South Africa": {"lat": "-30.559482", "lon": "22.937506"},
                      "Zambia": {"lat": "-13.133897", "lon": "27.849332"},
					  "Saint Martin": {"lat": "18.070829", "lon": "-63.050079"},
					  "Eswatini": {"lat": "-26.606630", "lon": "31.478365"},
					  "St. Barth": {"lat": "17.898781", "lon": "-62.824279"},
					  "Curaçao": {"lat": "12.138120", "lon": "-68.927072"},
                      "Zimbabwe": {"lat": "-19.015438", "lon": "29.154857"}}

            #below for loop drama is to read the cell value from df- for the current countrys activecases. this will always return only one row
            for activecase in mydataframe[mydataframe["Country Or Location"] == country]["Active Cases"]:

                currentActiveCase = str(activecase)
            # below for loop drama is to read the cell value from df- for the current countrys total cases. this will always return only one row
            for totalcase in mydataframe[mydataframe["Country Or Location"] == country]["Total Cases"]:

                currentTotalCase = str(totalcase)

            # below for loop drama is to read the cell value from df- for the current countrys total cases. this will always return only one row
            for Newcase in mydataframe[mydataframe["Country Or Location"] == country]["New Cases"]:
                currentNewCase = str(Newcase)
                #currentNewCase = ((str(Newcase)[1:]).replace('+', '')).replace(',', '')

            # prepare the map data only if the current country has lat-lon info is available
            if (country in latlondata):
                returndata = returndata + '"' + country + '":{"lat":"' + latlondata[country]['lat'] + '","lon":"' + latlondata[country]['lon'] + '","activecases":"' + currentActiveCase + '","totalcases":"' + currentTotalCase + '","newcases":"' + currentNewCase +'"},'
            else:
                pass
        #to remove the last comma
        returndata = returndata[:-1] + '}'
        global mapdatajson
        mapdatajson = returndata
        return mapdatajson
    except:

        return mapdatajson

@app.route("/bounties", methods=['GET'])
def bounties():
    # this is to render the map page with details
    return render_template("bounties.html")


if __name__ == "__main__":
    # create new thread for auto refresh of the dataframe
    GenerateResources()
    thread1 = myThread(1, "AutoLoadThread")
    # Start new Threads
    thread1.setDaemon(True)
    thread1.start()

    # do all the shit u want to do before app run below
    app.run(debug=True)



