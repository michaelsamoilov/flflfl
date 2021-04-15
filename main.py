from flask import Flask, request
import os
import json
# импортируем функции из нашего второго файла geo
import requests
from math import sin, cos, sqrt, atan2, radians


def get_coordinates(city):
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
    }

    response = requests.get(url, params)
    json = response.json()
    point_str = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    point_array = [float(x) for x in point_str.split(' ')]

    return point_array


def get_country(city):
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
    }

    response = requests.get(url, params)
    json = response.json()

    return \
        json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData'][
            'AddressDetails']['Country']['CountryName']


def get_distance(p1, p2):
    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


app = Flask(__name__)


# Добавляем логирование в файл.
# Чтобы найти файл, перейдите на pythonwhere в раздел files,
# он лежит в корневой папке


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Я могу показать город или сказать расстояние между городами!'
        return
    # Получаем города из нашего
    cities = get_cities(req)
    if not cities:
        res['response']['text'] = 'Ты не написал название не одного города!'
    elif len(cities) == 1:
        res['response']['text'] = 'Этот город в стране - ' + \
                                  get_country(cities[0])
    elif len(cities) == 2:
        distance = get_distance(get_coordinates(
            cities[0]), get_coordinates(cities[1]))
        res['response']['text'] = 'Расстояние между этими городами: ' + \
                                  str(round(distance)) + ' км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
