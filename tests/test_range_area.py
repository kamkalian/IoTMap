import pytest
import json
from app.models import Polygon, Polygonpoint


def test_create_and_add_range_point_list(range_area):
    
    range_point_list = []
    for i in range(10):
        range_point = range_area.range_point(i, i, i, i, 'kurm')
        range_point_list.append(range_point)

    range_area.add_range_point_list(range_point_list)
    
    assert len(range_area.range_point_list) == 10


def test_geo_json_created(range_area):
    '''
    Testet ob das Rangearea Objekt ein GeoJSON zurück gibt.
    '''

    geo_json = range_area.geo_json()

    assert type(geo_json) is str

    geo_json_dict = json.loads(geo_json)
    
    assert geo_json_dict['type'] == 'FeatureCollection'


def test_create_and_add_range_point_list(range_area):
    '''
    Testet ob sich ein range_point_list erstellen und hinzufügen lässt.
    '''

    range_point_list = [range_area.range_point(99, 99, 99, 99, 'kurm')]

    range_area.add_range_point_list(range_point_list)

    assert len(range_area.range_point_list) == 1


def test_geo_json_contains_feature_from_polygon_list(range_area):
    '''
    Testet ob in dem zurück gegebenen GeoJSON mehrere Features enthalten sind.
    Dabei werden die Daten über das polygon_list Layer eingefüllt.
    '''

    range_area.add_polygon(
        'kurm',
        '#ff0000',
        [(10,10), (20,20), (20,39)]
    )

    range_area.add_polygon(
        'kurm1',
        '#ff0000',
        [(10,5), (20,5), (20,39)]
    )

    geo_json = range_area.geo_json()
    geo_json_dict = json.loads(geo_json)

    assert 'features' in geo_json_dict

    assert len(geo_json_dict['features']) == 2


def test_geo_json_contains_feature_created_from_range_point_list(range_area):
    '''
    Testet ob in dem zurück gegebenen GeoJSON mehrere Features enthalten sind.
    Dabei werden die Daten über das range_point_list Layer eingefüllt.
    '''
    
    range_point_list = [
        range_area.range_point(10, 20, 10, -120, 'kurm2'),
        range_area.range_point(10, 30, 10, -110, 'kurm2'),
        range_area.range_point(20, 20, 30, -90, 'kurm2')
    ]

    range_area.add_gateway('kurm2', 9, 19)
    range_area.add_range_point_list(range_point_list)

    range_area.analyse()

    geo_json = range_area.geo_json()
    geo_json_dict = json.loads(geo_json)

    assert 'features' in geo_json_dict

    assert len(geo_json_dict['features']) == 1


def test_analyse(range_area):
    '''
    Testet ob die Analyse nach hinzufügen der range_point_list richtig funktioniert.
    '''
    
    range_point_list = [
        range_area.range_point(50.820329, 7.141111, 10, -120, 'kurm'),
        range_area.range_point(50.820329, 7.142111, 10, -120, 'kurm'),
        range_area.range_point(50.821329, 7.143111, 10, -120, 'kurm'),
        range_area.range_point(50.811329, 7.143111, 10, -110, 'kurm'),
        range_area.range_point(50.811329, 7.144111, 30, -90, 'kurm'),
        range_area.range_point(50.811329, 7.145111, 30, -90, 'kurm'),
        range_area.range_point(50.812329, 7.146111, 30, -90, 'kurm'),
        range_area.range_point(51.820329, 7.141111, 10, -120, 'kurm1'),
        range_area.range_point(51.820329, 7.142111, 10, -120, 'kurm1'),
        range_area.range_point(51.821329, 7.143111, 10, -120, 'kurm1'),
        range_area.range_point(51.811329, 7.143111, 10, -110, 'kurm1'),
        range_area.range_point(51.811329, 7.144111, 30, -90, 'kurm1'),
        range_area.range_point(51.811329, 7.145111, 30, -90, 'kurm1'),
        range_area.range_point(51.812329, 7.146111, 30, -90, 'kurm1'),
    ]

    range_area.add_gateway('kurm', 51.820329, 7.146111)
    range_area.add_gateway('kurm1', 51.810329, 7.146111)
    range_area.add_range_point_list(range_point_list)

    range_area.add_rssi_range(-121, -100, '#ff0000')
    range_area.add_rssi_range(-101, -80, '#00ff00')

    range_area.analyse()

    # Teste ob alle Gateways erkannt werden
    assert len(range_area.gateway_list) == 2

    # Teste ob alle RSSI Bereiche richtig erkannt werden
    assert len(range_area.polygon_list) == 4


def test_analyse_with_invalid_points(range_area):
    '''
    Testet ob die Analyse nach hinzufügen einer range_point_list mit Punkten,
    die die selben Koordinaten haben und somit ungültig sind, richtig funktioniert.
    '''

    range_point_list = [
        range_area.range_point(10, 20, 10, -120, 'kurm'),
        range_area.range_point(10, 20, 10, -120, 'kurm'),
        range_area.range_point(10, 20, 10, -120, 'kurm'),
        range_area.range_point(10, 20, 10, -110, 'kurm'),
        range_area.range_point(10, 20, 30, -90, 'kurm'),
        range_area.range_point(10, 20, 30, -90, 'kurm'),
        range_area.range_point(10, 20, 30, -90, 'kurm')]

    range_area.add_gateway('kurm', 9, 19)
    range_area.add_range_point_list(range_point_list)

    range_area.analyse()

    # Es muss 0 rauskommen, da es keine validen Punkte/Polygone gibt
    assert len(range_area.polygon_list) == 0


