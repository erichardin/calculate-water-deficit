"""CalculateWaterDeficit.py: A little script that calculates water deficit for a
garden. The script uses the Weather Underground API, which requires an API key 
that can be obtained at https://www.wunderground.com/. The script assumes that 
gardens need 1 in of rain per week 
(https://bonnieplants.com/library/how-much-water-do-vegetables-need/). The 
script then computes how much rain was received over the last three days and 
how much is expected in the next three days. The water deficit is the difference 
between what is needed and what was received/expected. """

import ConfigParser
import requests
import time
from numpy import mean
import sys

def isNumber(s):
    has_a_decimal = s.count('.') <= 1
    all_numbers = s.replace('.','').isdigit()
    return has_a_decimal and all_numbers


config = ConfigParser.ConfigParser()
config.read('user_data.cfg')
api_key = config.get('user_data', 'api_key')
city = config.get('user_data', 'city')
state = config.get('user_data', 'state')


# Get forecast data
r = requests.get("http://api.wunderground.com/api/%s/forecast/q/%s/%s.json"%(api_key,state,city))
response = r.json()['response']
if 'error' in response.keys():
    print('Error contacting Weather Underground with: ' + "http://api.wunderground.com/api/%s/forecast/q/%s/%s.json"%(api_key,state,city))
    print(response['error'])
    sys.exit(1)

forecast = r.json()
forecast = forecast['forecast']['simpleforecast']['forecastday']
precip_future = 0 # Quantitative Precipitation Forecast (in)
high = [] # Daily high temperature (f)
for item in forecast:
    precip_future += float(item['qpf_day']['in']) # qpf = Quantitative Precipitation Forecast
    high.append( float(item['high']['fahrenheit']) )

high_ave_future = mean(high)


# Get past data
precip_past = 0
high = []
date = int(time.strftime("%Y%m%d"))
for i in range(1,4):
    time.sleep(0.5)
    r = requests.get("http://api.wunderground.com/api/%s/history_%i/q/%s/%s.json"%(api_key,date-i,state,city))
    response = r.json()['response']
    if 'error' in response.keys():
        print('Error contacting Weather Underground with: ' + "http://api.wunderground.com/api/%s/forecast/q/%s/%s.json"%(api_key,state,city))
        print(response['error'])
        sys.exit(1)
    reccord = r.json()
    precip = reccord['history']['dailysummary'][0]['precipi']
    if isNumber(precip): # got T for trace, possibly other non-numeric results too
        precip_past += float(precip)
    high.append( float(reccord['history']['dailysummary'][0]['maxtempi']) )

high_ave_past = mean(high)


rain_possible = mean([precip_past,precip_future])
high_possible = mean([high_ave_past,high_ave_future])

rain_needed = 1.0 # inch per week
rain_deficit = max(rain_needed - rain_possible, 0)

print('Rain deficit is %.2f in' % rain_deficit)

sys.exit(0)


