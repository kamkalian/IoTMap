#!/venv/bin/python3
from flask import render_template, redirect, flash
from flask import json
from app.main import bp
import requests
from datetime import datetime
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
    
    range_point_list = []

    # Alle Gateways durchgehen
    for gateway in gateway_list:

        # Gateway hinzufügen
        range_area.add_gateway(
            gateway.gtw_id,
            gateway.latitude,
            gateway.longitude)

        # Alle message_links des Gateways durchgehen und eine range_point_list erstellen

        for message_link in gateway.message_links.order_by(MessageLink.rssi).limit(50).all():

            range_point = Rangearea.range_point(
                message_link.message.latitude,
                message_link.message.longitude,
                message_link.message.altitude, 
                message_link.rssi,
                gateway.gtw_id)

            range_point_list.append(range_point)

    print(len(range_point_list))

    # Die erstellte range_point_list dem range_area Objekt hinzufügen
    range_area.add_range_point_list(range_point_list)

    # Analyse des Rangearea Objekts starten
    range_area.analyse()   

    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
        geo_json=json.dumps(geo_json),
        geo_json_polys=range_area.geo_json())


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