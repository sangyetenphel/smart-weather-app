import requests
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from timezonefinder import TimezoneFinder

# Create your views here.
def index(request):
    return render(request, 'smart_weather/index.html')


def render_error(request, message, status):
    """Show the city search page again with a friendly error message."""
    return render(request, 'smart_weather/index.html', {'error': message}, status=status)


def weather(request, city_id):

    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        return render_error(request, "The weather service isn't set up yet (OPENWEATHER_API_KEY is missing).", 500)

    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'id': city_id, 'units': 'imperial', 'appid': api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        return render_error(request, "Couldn't reach the weather service. Please try again in a moment.", 502)

    if response.status_code == 404:
        return render_error(request, "We couldn't find that city. Please choose another one.", 404)
    if response.status_code != 200:
        return render_error(request, "Couldn't load the weather right now. Please try again in a moment.", 502)

    r = response.json()

    temperature = r['main']['temp']
    weather = r['weather'][0]['main']

    lon = r['coord']['lon']
    lat = r['coord']['lat']

    tf = TimezoneFinder()
    latitude, longitude = lat, lon
    time_zone = tf.timezone_at(lng=longitude, lat=latitude) # returns 'Europe/Berlin'

    time_zone_url = 'http://worldtimeapi.org/api/timezone/{}'

    try:
        new_r = requests.get(time_zone_url.format(time_zone), timeout=10).json()
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
    except:
        day_time = ''
    

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
    else:
        outfit = "80"

    context = {"city_weather": city_weather, "outfit": outfit, "weather": weather}

    return render(request, "smart_weather/weather.html", context)