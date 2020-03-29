#!/venv/bin/python3
from flask import render_template
from flask import json
from app.main import bp
import requests
from datetime import datetime
from app.models import Gateway, MessageLink, Message, Device
from app.main import geo_functions
from sqlalchemy import and_


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
    for gtw in gtw_list:

        # Zum testen wird nur auf mein Gateway geschaut
        # if gtw.gtw_id != 'eui-313532352e005300':
        #     continue

        locked_list = []

        
        # Alle Messages für ein Gateway und in einem bestimmte Empfangsstärkebereich selektieren.
        msg_list = [r.message for r in gtw.message_links.filter(
            and_(
                MessageLink.rssi > -150, 
                MessageLink.rssi < -10,
                MessageLink.gtw_id == gtw.gtw_id
            )
        ).all()]
        

        '''
        # Message Liste nur zum Testen
        msg_list = []

        msg_list.append(Message(msg_id=0, latitude=50.831100, longitude=7.110354))
        msg_list.append(Message(msg_id=1, latitude=50.831676, longitude=7.109839))
        msg_list.append(Message(msg_id=2, latitude=50.831764, longitude=7.109968))
        msg_list.append(Message(msg_id=3, latitude=50.830929, longitude=7.110590))
        msg_list.append(Message(msg_id=4, latitude=50.831314, longitude=7.109968))
        msg_list.append(Message(msg_id=5, latitude=50.831229, longitude=7.111590))
        '''

        # Nahe Punkte verwerfen
        erasable_msg_list = []
        for msg in msg_list:
            if geo_functions.meters([msg.latitude, msg.longitude], [gtw.latitude, gtw.longitude]) < 100:
                erasable_msg_list.append(msg)

        for erasable_msg in erasable_msg_list:
            msg_list.remove(erasable_msg)

        # Falls es keine Messages zu einem Gateway gibt wird mit dem nächsten Gateway weiter gemacht
        if len(msg_list) == 0:
            continue

        # Liste nur mit IDs rausziehen.
        msg_id_list = [r.msg_id for r in msg_list]
        # print(msg_id_list)
        
        # dict für polygon
        polygon = []

        # Gateway Punkt als ersten Punkt einfügen
        polygon.append([gtw.longitude, gtw.latitude])

        # aktueller Punkt
        # zum Start wird der nächstgelegene Punkt zum Gateway ermittelt
        current_msg = geo_functions.nearest_msg_to_gateway(msg_list, gtw)
        polygon.append([current_msg.longitude, current_msg.latitude])
        msg_id_list.remove(current_msg.msg_id)
        msg_list.remove(current_msg)

        # Eine Schleife geht so lange alle Punkte durch bis keine mehr in der Liste sind.
        while(len(msg_id_list)>1):

            # Finde den nächstgelegenen Punkt
            nearest_msg, distance = geo_functions.nearest_msg(msg_list, current_msg)

            # Den nächstgelegenen Punkt dem Polygon hinzufügen
            polygon.append([nearest_msg.longitude, nearest_msg.latitude])
            
            # Entfernt die ID und msg den nächstgelegenen Punktes aus den Listen.
            msg_id_list.remove(nearest_msg.msg_id)
            msg_list.remove(nearest_msg)

            # print(current_msg.msg_id, nearest_msg.msg_id, distance, len(msg_list))

            # Wenn noch IDs vorhanden sind wird die aktuelle ID zwichen gespeichert.
            current_msg =  nearest_msg

            # Sollte der letzte Punkt erreicht sein wird dieser noch zum Polygon hinzugefügt
            if len(msg_list) == 1:
                polygon.append([msg_list[0].longitude, msg_list[0].latitude])


        if len(polygon) > 0:     
            feature = {
                'type': 'Feature',
                'geometry': {'type': 'Polygon', 'coordinates': [
                    polygon
                    ]}
            }
            poly_features.append(feature)


    geo_json_polys['features'] = poly_features
    # print(geo_json_polys)


    return render_template(
        'index.html',
        title=u'FFRS-TTN-Map',
        geo_json=json.dumps(geo_json),
        geo_json_polys=json.dumps(geo_json_polys))


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