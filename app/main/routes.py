#!/venv/bin/python3
from flask import render_template, redirect, flash, url_for, request
from flask import json
from app.main import bp
import requests
from datetime import datetime, timedelta
from app.models import Gateway, MessageLink, Message, Device
from sqlalchemy import and_
from app.polygon_builder.Rangearea import Rangearea


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

    try:
        gateway_list = Gateway.query.all()
    except:
        return """Datenbank Fehler!"""

    # GeoJSON erstellen
    geo_json = { 'type': 'FeatureCollection' }
    features = []
    for gateway in gateway_list:
        
        # Hat das Gateway Koordinaten?
        if gateway.latitude and gateway.longitude:
            # print(gateway.gtw_id, gateway.last_seen)

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

    # Ein Rangearea Object anlegen
    range_area = Rangearea()

    # RSSI Bereiche definieren
    range_area.add_rssi_range(-99, 0, '#ff0000')
    range_area.add_rssi_range(-104, -100, '#FF7F00')
    range_area.add_rssi_range(-109, -105, '#ffff00')
    range_area.add_rssi_range(-114, -110, '#00ff00')
    range_area.add_rssi_range(-119, -115, '#00ffff')
    range_area.add_rssi_range(-200, -120, '#0000ff')
    

    # Alle Gateways durchgehen
    for gateway in gateway_list:

        polygon_list = []

        # Gateway hinzufügen
        range_area.add_gateway(
            gateway.gtw_id,
            gateway.latitude,
            gateway.longitude)

        for polygon_db in gateway.polygons:

            coords = []
            for polygon_point_db in polygon_db.polygon_points:
                coords.append([polygon_point_db.longitude, polygon_point_db.latitude])
        
            range_area.add_polygon(
                gateway.gtw_id,
                polygon_db.fill_color,
                coords
            )


    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
        geo_json=json.dumps(geo_json),
        geo_json_polys=range_area.geo_json(),
        site='index')


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
        if diff_seconds > 3600: # 60 minutes
            return 'offline'
        else:
            return 'online'
    
    # An dieser stelle wird 'unknown' zurückgegeben, wenn die anderen Regeln nicht gegriffen haben.
    return 'unknown'


@bp.route('/log')
def log():
    """
    Route zur Log Seite
    """

    last_messages = []
    try:
        # letzte Messages aus der Datenbank holen
        last_messages = Message.query.order_by(Message.time.desc()).limit(50).all()

        # for message in last_messages:
            # new_time = message.time + + timedelta(seconds=7200)
            # message.time = new_time
            #print(message.time, new_time)

    except:
        flash('Datenbank Fehler!')

    return render_template(
        'log.html',
        title=u'Log', last_messages=last_messages, site='log')