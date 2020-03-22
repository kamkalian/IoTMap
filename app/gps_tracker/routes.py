from app.gps_tracker import bp
from flask import request
import json
from app.models import Gateway, MessageLink, Message, Device
from app import db
from datetime import datetime


@bp.route('/receive_uplink', methods=['POST'])
def receive_upink():

    msg = request.data
    msg_dict = json.loads(msg)

    # Prüfen ob Device in der Datenbank vorhanden ist
    dev = Device.query.filter_by(dev_id=msg_dict['dev_id']).first()
    if not dev:

        # Neues Device anlegen
        dev_new = Device(dev_id=msg_dict['dev_id'], hardware_serial=msg_dict['hardware_serial'])
        print('New device: ', dev_new)
        db.session.add(dev_new)
        db.session.commit()
        dev = dev_new

    # datetime erstellen
    time_str = msg_dict['time'].split('.')
    time_dt = datetime.strptime(time_str[0], '%Y-%m-%dT%H:%M:%S')
    time_str = time_dt.strftime('%Y-%m-%d %H:%M:%S')

    # Message in die Datenbank schreiben
    msg_new = Message(
        app_id=msg_dict['app_id'],
        port=msg_dict['port'],
        counter=msg_dict['counter'],
        payload_raw=msg_dict['payload_raw'],
        altitude=msg_dict['altitude'],
        hdop=msg_dict['hdop'],
        latitude=msg_dict['latitude'],
        longitude=msg_dict['longitude'],
        sats=msg_dict['sats'],
        time=time_str,
        frequency=msg_dict['frequency'],
        modulation=msg_dict['modulation'],
        data_rate=msg_dict['data_rate'],
        airtime=msg_dict['airtime'],
        coding_rate=msg_dict['coding_rate'],
        dev_id=msg_dict['dev_id'],
    )
    print('New message: ', msg_new)
    db.session.add(msg_new)
    db.session.commit()


    # Prüfen ob die Gateways in der Datenbank vorhanden sind
    for link in msg_dict['links']:
        #print(link)
        
        if 'gtw_id' in link:
            
            gtw_db = Gateway.query.filter_by(gtw_id=link['gtw_id']).first()

            # Neues Getway in die Datenbank schreiben
            if not gtw_db:

                gtw_trusted = link['gtw_trusted']
                latitude = link['latitude']
                longitude = link['longitude']
                altitude = link['altitude']

                gtw_new = Gateway(
                    gtw_id=link['gtw_id'], 
                    gtw_trusted=gtw_trusted,
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude)
                
                print('New gateway: ', gtw_new)

                db.session.add(gtw_new)
                db.session.commit()
                gtw_db = gtw_new


        # MessageLink in die Datenbank schreiben
        link_new = MessageLink(
            timestamp=link['timestamp'],
            channel=link['channel'],
            rssi=link['rssi'],
            snr=link['snr'],
            rf_chain=link['rf_chain'],
            msg_id=msg_new.msg_id,
            gtw_id=gtw_db.gtw_id
        )
        print('New message_link: ', link_new)
        db.session.add(link_new)
        db.session.commit()

    return {'ok': 1}
