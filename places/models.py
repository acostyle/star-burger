import requests

from django.db import models
from django.utils import timezone

from star_burger import settings


class Place(models.Model):
    address = models.CharField(max_length=256, unique=True, verbose_name='адресс доставки')
    lat = models.FloatField(blank=True, null=True, verbose_name='широта')
    lon = models.FloatField(blank=True, null=True, verbose_name='долгота')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='дата создания')


    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'


    def __str__(self):
        return self.address

    @staticmethod
    def fetch_coordinates(address):
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": settings.YA_API_KEY,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

        return lon, lat
