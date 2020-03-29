import requests
from app.models import Gateway, MessageLink, Message, Device
from flask import json
from app import db
from datetime import datetime, timedelta


def think_positive(value):
    if value < 0:
        value *= -1
    return value


def ttn_sync(center_lat, center_lon, distance):
    '''
    Holt alle Gateways von TheThingsNetwork und vergleich sie mit der Datenbank.
    Fehlende Informationen werden dann in der Datenbank ergänzt.
    '''
    
    # Gateways von thethingsnetwork.org holen
    gateways = requests.get('https://www.thethingsnetwork.org/gateway-data/location?latitude=' + center_lat + '&amp;longitude=' + center_lon + '&amp;distance='+distance)
    gateways_json = gateways.json()
    # print(gateways_json)

    # Listen für neue und aktualisierte Gateways anlegen. Diese werden später zurückgegeben
    new_gw_list = []
    update_gw_list = []

    for gw_key in gateways_json:

        gw_db = Gateway.query.get(gw_key)

        # Prüfen ob ein Gateway existiert
        if gw_db:

            # Eine Variable um zu sehen ob das Gateway geupdatet wurde
            is_updated = False

            lat = None
            lon = None
            alt = None
            description = None
            owner = None
            brand = None
            model = None
            antenna_model = None
            placement = None
            last_seen_dt = None

            try:

                if 'latitude' in gateways_json[gw_key]['location']:
                    lat = gateways_json[gw_key]['location']['latitude']
                if 'longitude' in gateways_json[gw_key]['location']:
                    lon = gateways_json[gw_key]['location']['longitude']
                if 'altitude' in gateways_json[gw_key]['location']:
                    alt = gateways_json[gw_key]['location']['altitude']

                if 'description' in gateways_json[gw_key]:
                    description = gateways_json[gw_key]['description']
                if 'owner' in gateways_json[gw_key]:
                    owner = gateways_json[gw_key]['owner']
                if 'brand' in gateways_json[gw_key]['attributes']:
                    brand = gateways_json[gw_key]['attributes']['brand']
                if 'model' in gateways_json[gw_key]['attributes']:
                    model = gateways_json[gw_key]['attributes']['model']
                if 'antenna_model' in gateways_json[gw_key]['attributes']:
                    antenna_model = gateways_json[gw_key]['attributes']['antenna_model']
                if 'placement' in gateways_json[gw_key]['attributes']:
                    placement = gateways_json[gw_key]['attributes']['placement']

                if 'last_seen' in gateways_json[gw_key]:
                    last_seen_dt = datetime.strptime(gateways_json[gw_key]['last_seen'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=3600)

            except Exception as e:
                print(e)

            # Prüfen ob die Koordinaten abweichen, ansonsten aktualisieren
            tolerance = 0.001
            
            # Latitude
            if lat and ( gw_db.latitude == None or ( think_positive(gw_db.latitude - lat) > tolerance ) ):
                gw_db.latitude = lat
                is_updated = True

            # Longitude
            if lon and ( gw_db.longitude == None or ( think_positive(gw_db.longitude - lon) > tolerance ) ):
                gw_db.longitude = lon
                is_updated = True

            # Altitude
            if alt and ( gw_db.altitude == None or ( think_positive(gw_db.altitude - alt) > tolerance ) ):
                gw_db.altitude = alt
                is_updated = True

            # Prüfen ob die anderen Daten abweichen, ansonsten aktualisieren
            # last_seen
            if last_seen_dt and gw_db.last_seen == None:
                gw_db.last_seen = last_seen_dt
                is_updated = True
            elif last_seen_dt and (last_seen_dt + timedelta(seconds=3600) - gw_db.last_seen).total_seconds() > 30:
                gw_db.last_seen = last_seen_dt + timedelta(seconds=3600)
                is_updated = True

            # Description
            if description and ( gw_db.description == None or ( description != gw_db.description ) ):
                gw_db.description = description
                is_updated = True
            
            # Owner
            if owner and ( gw_db.owner == None or ( owner != gw_db.owner ) ):
                gw_db.owner = owner
                is_updated = True

            # Brand
            if brand and ( gw_db.brand == None or ( brand != gw_db.brand ) ):
                gw_db.brand = brand
                is_updated = True

            # Model
            if model and ( gw_db.model == None or ( model != gw_db.model ) ):
                gw_db.model = model
                is_updated = True

            # Antenna Model
            if antenna_model and ( gw_db.antenna_model == None or ( antenna_model != gw_db.antenna_model ) ):
                gw_db.antenna_model = antenna_model
                is_updated = True

            # Placement
            if placement and ( gw_db.placement == None or ( placement != gw_db.placement ) ):
                gw_db.placement = placement
                is_updated = True

            # Wenn sich mindestens ein Wert geändert hat, wird comittet
            if is_updated:
                db.session.commit()
                update_gw_list.append(gw_key)
        
        else:

            # Neue Gateways zur Datenbank hinzufügen
            new_gw = Gateway(gtw_id = gw_key)
            db.session.add(new_gw)
            db.session.commit()
            new_gw_list.append(gw_key)

    return new_gw_list, update_gw_list

'''



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

'''


