import requests
from django.shortcuts import render
from datetime import datetime

# Create your views here.
def index(request):
    return render(request, 'smart_weather/index.html')


def weather(request, city_id):

    url = 'https://api.openweathermap.org/data/2.5/weather?id={}&units=imperial&appid=8650b978cd17f0a0eb65c73e957bf584'


    r = requests.get(url.format(city_id)).json()

    temperature = r['main']['temp']
    weather = r['weather'][0]['main']
    unix_time = int(r['dt'])
    day_time = datetime.utcfromtimestamp(unix_time).strftime('%a, %I:%M %p')
    
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

    print(temperature)

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