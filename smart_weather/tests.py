from unittest import mock

import requests
from django.test import TestCase, override_settings


# django_heroku enables WhiteNoise's manifest storage, which needs collectstatic;
# tests use plain static file URLs instead
PLAIN_STATIC = 'django.contrib.staticfiles.storage.StaticFilesStorage'


def fake_response(status_code=200, data=None):
    response = mock.Mock(status_code=status_code)
    response.json.return_value = data or {}
    return response


def weather_data(temperature, condition='Clear'):
    return {
        'name': 'Testville',
        'coord': {'lon': -73.99, 'lat': 40.73},
        'main': {'temp': temperature, 'temp_max': temperature + 2, 'temp_min': temperature - 2},
        'weather': [{'main': condition, 'description': 'clear sky', 'icon': '01d'}],
    }


def time_data():
    return {'day_of_week': 4, 'datetime': '2026-10-29T15:37:00.000000-04:00'}


@override_settings(OPENWEATHER_API_KEY='test-key', STATICFILES_STORAGE=PLAIN_STATIC)
class WeatherPageTests(TestCase):

    def get_weather(self, temperature, condition='Clear'):
        responses = [fake_response(data=weather_data(temperature, condition)), fake_response(data=time_data())]
        with mock.patch('smart_weather.views.requests.get', side_effect=responses) as get:
            response = self.client.get('/5128581')
        return response, get

    def test_shows_weather_and_outfit(self):
        response, get = self.get_weather(32.02, 'Clouds')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testville')
        self.assertContains(response, 'images/men30.jpg')
        self.assertContains(response, 'images/clouds.jpg')
        self.assertContains(response, 'Thu, 03:37 PM')
        self.assertEqual(get.call_args_list[0].kwargs['params']['appid'], 'test-key')

    def test_exactly_80_degrees_suggests_the_warmest_outfit(self):
        response, _ = self.get_weather(80)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'images/men80.jpg')

    def test_temperature_bands(self):
        for temperature, outfit in ((39.9, '30'), (40, '40'), (59.9, '50'), (79.9, '70'), (95, '80')):
            response, _ = self.get_weather(temperature)
            self.assertContains(response, f'images/men{outfit}.jpg', msg_prefix=str(temperature))

    def test_unknown_city_shows_a_friendly_message(self):
        with mock.patch('smart_weather.views.requests.get', return_value=fake_response(404)):
            response = self.client.get('/1')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "We couldn&#x27;t find that city", status_code=404)

    def test_weather_service_errors_show_a_friendly_message(self):
        with mock.patch('smart_weather.views.requests.get', return_value=fake_response(500)):
            response = self.client.get('/5128581')
        self.assertContains(response, "Couldn&#x27;t load the weather", status_code=502)

        with mock.patch('smart_weather.views.requests.get', side_effect=requests.ConnectionError):
            response = self.client.get('/5128581')
        self.assertContains(response, "Couldn&#x27;t reach the weather service", status_code=502)

    def test_still_works_when_the_local_time_lookup_fails(self):
        responses = [fake_response(data=weather_data(70)), requests.ConnectionError()]
        with mock.patch('smart_weather.views.requests.get', side_effect=responses):
            response = self.client.get('/5128581')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testville')


@override_settings(OPENWEATHER_API_KEY='', STATICFILES_STORAGE=PLAIN_STATIC)
class MissingApiKeyTests(TestCase):

    def test_missing_key_shows_a_setup_message(self):
        with mock.patch('smart_weather.views.requests.get') as get:
            response = self.client.get('/5128581')

        get.assert_not_called()
        self.assertContains(response, 'OPENWEATHER_API_KEY is missing', status_code=500)
