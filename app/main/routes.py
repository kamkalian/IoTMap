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

    # GeoJson für die Polygone bauen
    # Dazu müssen die Daten von den Tracker geholt und ausgewertet werden.
    geo_json_polys = { 'type': 'FeatureCollection' }
    poly_features = []
    gtw_list = Gateway.query.all()
    #gtw_list = []
    for gtw in gtw_list:

        #if gtw.gtw_id != 'eui-313532352e005300':
        #    continue

        gateway_feature_per_rssi(gtw, -200, -120, poly_features, '#0000ff')
        gateway_feature_per_rssi(gtw, -120, -115, poly_features, '#00ffff')
        gateway_feature_per_rssi(gtw, -115, -110, poly_features, '#00ff00')
        gateway_feature_per_rssi(gtw, -110, -105, poly_features, '#ffff00')
        gateway_feature_per_rssi(gtw, -105, -100, poly_features, '#FF7F00')
        gateway_feature_per_rssi(gtw, -100, 0, poly_features, '#ff0000')
        
        
        
    geo_json_polys['features'] = poly_features

    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
        geo_json=json.dumps(geo_json),
        geo_json_polys=json.dumps(geo_json_polys))


def gateway_feature_per_rssi(gtw, min_rssi, max_rssi, poly_features, fill_color):
    
    # Alle Messages für ein Gateway und in einem bestimmte Empfangsstärkebereich selektieren.
    msg_list = [r.message for r in gtw.message_links.filter(
        and_(
            MessageLink.rssi <= max_rssi,
            MessageLink.rssi > min_rssi,
            MessageLink.gtw_id == gtw.gtw_id
        )
    ).all()]

    if len(msg_list) > 2:
        msg_cluster = geo_functions.msg_cluster(msg_list, 300)
        for cluster in msg_cluster:
            poly_features.append(geo_functions.feature(cluster, gtw, fill_color))


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