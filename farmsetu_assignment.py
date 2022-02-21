from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import io
import json
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np

app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:yukth@localhost/weather'
app.debug= True
db = SQLAlchemy(app)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.get_option("display.max_rows")
np.set_printoptions(threshold=np.inf)

# we can take region dynamically as input
region = 'UK'
# region = 'England'

req = Request('https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmax/date/' + region + '.txt',
              headers={'User-Agent': 'Mozilla/5.0'})
web_response = urlopen(req).read()
str1 = web_response.decode('UTF-8')
information_res = str1.partition('year')[0]
data_response = str1.replace(information_res, "")

df = pd.read_fwf(io.StringIO(data_response), engine='python')

weather_response = json.loads(df.to_json(orient="records"))

# we can use looping to fetch each row yearly wise and store in some child table also wirh reference
# for monthly_whether_data in result:
#     print(monthly_whether_data)

class form_setu_weather_forecast(db.Model):
    __tablename__= "form_setu_weather_forecast"
    country = db.Column(db.String(),primary_key=True)
    information = db.Column(db.String(),nullable=False)
    weather_result = db.Column(db.JSON(),nullable=False)

    def __init__(self,country,information,weather_result):
        self.country = country
        self.information = information
        self.weather_result = weather_result

@app.route("/weather", methods=["GET"])
def weather():
    output = []
    forcast = {}
    forcast['country'] = region
    forcast['information'] = information_res
    forcast['weather_result'] = weather_response
    output.append(forcast)
    return jsonify(output)


if __name__ =='__main__':
    app.run()
