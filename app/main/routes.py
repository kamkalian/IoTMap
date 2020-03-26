#!/venv/bin/python3
from flask import render_template
from flask import json
from app.main import bp
import requests
from datetime import datetime


r_earth = 6373.0


@bp.route('/')
@bp.route('/index')
def index():
    '''
    Route für die Startseite.
    '''

    # troisdorf 50.820329, 7.141111
    center_lat = '50.820329'
    center_lon = '7.141111'
    distance = '25000'

    # center al tuple
    center = (center_lat, center_lon)

    # Gateways von thethingsnetwork.org holen
    gateways = requests.get('https://www.thethingsnetwork.org/gateway-data/location?latitude=' + center_lat + '&amp;longitude=' + center_lon + '&amp;distance='+distance)
    gateways_json = gateways.json()
    # print(gateways_json)

    # GeoJSON erstellen
    geo_json = { 'type': 'FeatureCollection' }
    features = []
    for gw_key in gateways_json:
        try:
            lat = gateways_json[gw_key]['location']['latitude']
            lon = gateways_json[gw_key]['location']['longitude']
            
            # Prüfen welche Daten vorhanden sind, um KeyErrors zu verhindern
            if 'description' not in gateways_json[gw_key]:
                gateways_json[gw_key]['description'] = '-'
            if 'owner' not in gateways_json[gw_key]:
                gateways_json[gw_key]['owner'] = '-'
            if 'brand' not in gateways_json[gw_key]['attributes']:
                gateways_json[gw_key]['attributes']['brand'] = '-'
            if 'model' not in gateways_json[gw_key]['attributes']:
                gateways_json[gw_key]['attributes']['model'] = '-'
            if 'antenna_model' not in gateways_json[gw_key]['attributes']:
                gateways_json[gw_key]['attributes']['antenna_model'] = '-'
            if 'placement' not in gateways_json[gw_key]['attributes']:
                gateways_json[gw_key]['attributes']['placement'] = '-'
            if 'last_seen' not in gateways_json[gw_key]:
                print(gw_key)
                gateways_json[gw_key]['last_seen'] = '-'
            
            # feature aus allen Daten zusammensetzen und dem features dict hinzufügen
            
            feature = { 
                'type': 'Feature', 
                'geometry': {'type': 'Point', 'coordinates': [lon, lat] },
                'properties': {
                    'id': gw_key, 
                    'gw_state': gateway_state(gateways_json[gw_key]),
                    'description': gateways_json[gw_key]['description'],
                    'owner': gateways_json[gw_key]['owner'],
                    'last_seen': gateways_json[gw_key]['last_seen'],
                    'brand': gateways_json[gw_key]['attributes']['brand'],
                    'model': gateways_json[gw_key]['attributes']['model'],
                    'antenna_model': gateways_json[gw_key]['attributes']['antenna_model'],
                    'placement': gateways_json[gw_key]['attributes']['placement']
                    },
            }
            features.append(feature)
            
        except KeyError as e:
            print(gw_key)
            print(e)

            pass
            #print('KeyError')

    geo_json['features'] = features

    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
        geo_json=json.dumps(geo_json))


def gateway_state(json_data):
    '''
    Ermittelt anhand von 'last_seen' den Status eines Gateways.
    >5 Tage -> Gateway ist tot
    <=5 Tage und >10 Minuten -> Gateway ist offline
    <=10 Minuten -> Gateway ist online
    '''

    # Aktuelle Zeit holen
    now_dt = datetime.now()
    
    # last_seen aus json extrahieren und daraus ein datetime objekt machen
    last_seen = json_data['last_seen']
    try:
        last_seen_dt = datetime.strptime(last_seen, '%Y-%m-%dT%H:%M:%SZ')
    except:
        return 'unknown'
    
    # Anzahl Tage zwichen last_seen und jetzt ausrechnen
    diff_days = (now_dt - last_seen_dt).days

    # Anzahl Sekunden zwichen last_seen und jetzt ausrechnen.
    # Mit -3600 wird noch eine Stunde für die Zeitverschiebung abgezogen
    # TODO Problem mit der Zeitverschiebung muss noch anders gelöst werden
    diff_seconds = (now_dt - last_seen_dt).seconds-3600
    
    # Abfragen und entsprechende Rückgabewerte
    if diff_days > 5:
        return 'deceased'
    else:
        if diff_seconds > 600: # 10 minutes
            return 'offline'
        else:
            return 'online'
    
    # An dieser stelle wird 'unknown' zurückgegeben, wenn die anderen Regeln nicht gegriffen haben.
    return 'unknown'