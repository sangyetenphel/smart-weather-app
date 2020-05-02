import requests
from django.shortcuts import render
from datetime import datetime
from timezonefinder import TimezoneFinder

# Create your views here.
def index(request):
    return render(request, 'smart_weather/index.html')


def weather(request, city_id):

    url = 'https://api.openweathermap.org/data/2.5/weather?id={}&units=imperial&appid=8650b978cd17f0a0eb65c73e957bf584'


    r = requests.get(url.format(city_id)).json()

    temperature = r['main']['temp']
    weather = r['weather'][0]['main']

    lon = lat = r['coord']['lon']
    lat = r['coord']['lat']

    tf = TimezoneFinder()
    latitude, longitude = lat, lon
    time_zone = tf.timezone_at(lng=longitude, lat=latitude) # returns 'Europe/Berlin'
    
    time_zone_url = 'http://worldtimeapi.org/api/timezone/{}'
    new_r = requests.get(time_zone_url.format(time_zone)).json()
    week_day = new_r['day_of_week']

    if week_day == 0:
        day = 'Sun'
    elif week_day == 1:
        day = 'Mon'
    elif week_day == 2:
        day = 'Tue'
    elif week_day == 3:
        day = 'Wed'
    elif week_day == 4:
        day = 'Thu'
    elif week_day == 5:
        day = 'Fri'
    elif week_day == 6:
        day = 'Sat'
    else:
        day = ''

    date_time = new_r['datetime']
    m_time = date_time[11:16]
    time = datetime.strptime(m_time,"%H:%M").strftime("%I:%M %p")

    day_time = day + ", " + time

    # Generate different wallpaper for different weather
    if weather == 'Clear':
        weather = 'clear'
    elif weather == 'Thunderstorm':
        weather = 'thunderstorm'
    elif weather == 'Drizzle':
        weather = 'drizzle'
    elif weather == 'Rain':
        weather ='rain'
    elif weather == 'Snow':
        weather = 'snow'
    elif weather == 'Clouds':
        weather = 'clouds'
    else:
        weather = 'atmosphere'
    
    city_weather = {
        'city': r['name'],
        'temperature': temperature,
        'max': r['main']['temp_max'],
        'min': r['main']['temp_min'],
        'description': r['weather'][0]['description'],
        'icon': r['weather'][0]['icon'],
        'day_time': day_time                       

    }

    # What clothes to wear based on the temperature
    if temperature < 40:
        outfit = "30"
    elif temperature < 50:
        outfit = "40"
    elif temperature < 60:
        outfit = "50"
    elif temperature < 70:
        outfit = "60"
    elif temperature < 80:
        outfit = "70"
    elif temperature > 80 :
        outfit = "80"

    context = {"city_weather": city_weather, "outfit": outfit, "weather": weather}

    return render(request, "smart_weather/weather.html", context)