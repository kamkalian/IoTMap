import requests
from app.models import Gateway, MessageLink, Message, Device, Polygon, Polygonpoint
from flask import json
from app import db, scheduler
from datetime import datetime, timedelta
from app.polygon_builder.Rangearea import Rangearea


# @scheduler.task('interval', id='do_job_2', seconds=3600)
def run_polygon_builder():

    with scheduler.app.app_context():

        # Erstmal alle Gatewas holen
        try:
            gateway_list = Gateway.query.all()
        except:
            print('Datenbank Fehler!')

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

            # print(gateway)

            # Gateway hinzufügen
            range_area.add_gateway(
                gateway.gtw_id,
                gateway.latitude,
                gateway.longitude)

            for message_link in gateway.message_links:

                    range_point = Rangearea.range_point(
                        message_link.message.latitude,
                        message_link.message.longitude,
                        message_link.message.altitude, 
                        message_link.rssi,
                        gateway.gtw_id)

                    range_point_list.append(range_point)

        # Die erstellte range_point_list dem range_area Objekt hinzufügen
        range_area.add_range_point_list(range_point_list)

        # Analyse des Rangearea Objekts starten
        range_area.analyse()   

        # Nach der Analyse werden die ermittelten Polygone in der Datenbank gespeichert.
        # Dazu wird werden die Datenbanktabellen Polygon und Polygonpoints geleert.
        Polygonpoint.query.delete()
        Polygon.query.delete()
        db.session.commit()

        
        for polygon in range_area.polygon_list:

            new_polygon = Polygon(
                gtw_id=polygon['gtw_id'],
                fill_color=polygon['fill_color']
            )
            
            db.session.add(new_polygon)
            db.session.commit()

            for point in polygon['coords']:

                new_polygonpoint = Polygonpoint(
                    latitude=point[1],
                    longitude=point[0],
                    polygon_id=new_polygon.poly_id
                )
                
                db.session.add(new_polygonpoint)

            db.session.commit()


        print('Alle Polygone gespeichert.')
        
