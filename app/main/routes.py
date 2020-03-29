#!/venv/bin/python3
from flask import render_template
from flask import json
from app.main import bp
import requests
from datetime import datetime
from app.models import Gateway, MessageLink, Message, Device
from app.main import geo_functions
from sqlalchemy import and_


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

    gateway_list = Gateway.query.all()

    # GeoJSON erstellen
    geo_json = { 'type': 'FeatureCollection' }
    features = []
    for gateway in gateway_list:
        
        # Hat das Gateway Koordinaten?
        if gateway.latitude and gateway.longitude:
            print(gateway.gtw_id, gateway.last_seen)

            lat = gateway.latitude
            lon = gateway.longitude
        
            # feature aus allen Daten zusammensetzen und dem features dict hinzufügen
            feature = { 
                'type': 'Feature', 
                'geometry': {'type': 'Point', 'coordinates': [lon, lat] },
                'properties': {
                    'id': gateway.gtw_id, 
                    'gw_state': gateway_state(gateway.last_seen),
                    'description': gateway.description,
                    'owner': gateway.owner,
                    'last_seen': gateway.last_seen,
                    'brand': gateway.brand,
                    'model': gateway.model,
                    'antenna_model': gateway.antenna_model,
                    'placement': gateway.placement
                    },
            }
            features.append(feature)
        

    geo_json['features'] = features

            pass
            #print('KeyError')

    geo_json['features'] = features

    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
def meters(p1, p2):    
    
    dlat = radians(p2[0]-p1[0])
    dlon = radians(p2[1]-p1[1])
    
    a = sin(dlat / 2)**2 + cos(p1[0]) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = r_earth * c * 1000

    return distance


def gateway_state(last_seen):
    '''
    Ermittelt anhand von 'last_seen' den Status eines Gateways.
    >5 Tage -> Gateway ist tot
    <=5 Tage und >10 Minuten -> Gateway ist offline
    <=10 Minuten -> Gateway ist online
    '''

    if not last_seen:
        return 'unkown'

    # Aktuelle Zeit holen
    now_dt = datetime.now()
    
    # Anzahl Tage zwichen last_seen und jetzt ausrechnen
    diff_days = (now_dt - last_seen).days

    # Anzahl Sekunden zwichen last_seen und jetzt ausrechnen.
    # Mit -3600 wird noch eine Stunde für die Zeitverschiebung abgezogen
    # TODO Problem mit der Zeitverschiebung muss noch anders gelöst werden
    diff_seconds = (now_dt - last_seen).total_seconds()
    
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