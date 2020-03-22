
import time
import ttn
from app import Config
from flask import redirect, url_for
from flask import current_app
import requests
import json

class TTNMQTTClient():
    

    @staticmethod
    def uplink_callback(msg, client):
        
        # print("Received uplink from ", msg.dev_id)
        # print(msg)
        try:
            msg_dict = {}
            msg_dict['app_id'] = getattr(msg, 'app_id', None)
            msg_dict['dev_id'] = getattr(msg, 'dev_id', None)
            msg_dict['hardware_serial'] = getattr(msg, 'hardware_serial', None)
            msg_dict['port'] = getattr(msg, 'port', None)
            msg_dict['counter'] = getattr(msg, 'counter', None)
            msg_dict['payload_raw'] = getattr(msg, 'payload_raw', None)
            msg_dict['altitude'] = getattr(msg.payload_fields, 'altitude', None)
            msg_dict['hdop'] = getattr(msg.payload_fields, 'hdop', None)
            msg_dict['latitude'] = getattr(msg.payload_fields, 'latitude', None)
            msg_dict['longitude'] = getattr(msg.payload_fields, 'longitude', None)
            msg_dict['sats'] = getattr(msg.payload_fields, 'sats', None)
            msg_dict['time'] = getattr(msg.metadata, 'time', None)
            msg_dict['frequency'] = getattr(msg.metadata, 'frequency', None)
            msg_dict['modulation'] = getattr(msg.metadata, 'modulation', None)
            msg_dict['data_rate'] = getattr(msg.metadata, 'data_rate', None)
            msg_dict['airtime'] = getattr(msg.metadata, 'airtime', None)
            msg_dict['coding_rate'] = getattr(msg.metadata, 'coding_rate', None)

            # links
            msg_dict['links'] = []
            for gtw in msg.metadata.gateways:
                link_dict = {}
                link_dict['timestamp'] = getattr(gtw, 'timestamp', None)
                link_dict['channel'] = getattr(gtw, 'channel', None)
                link_dict['rssi'] = getattr(gtw, 'rssi', None)
                link_dict['snr'] = getattr(gtw, 'snr', None)
                link_dict['rf_chain'] = getattr(gtw, 'rf_chain', None)
                link_dict['gtw_id'] = getattr(gtw, 'gtw_id', None)     

                link_dict['gtw_trusted'] = getattr(gtw, 'gtw_trusted', False)
                link_dict['latitude'] = getattr(gtw, 'latitude', None)
                link_dict['longitude'] = getattr(gtw, 'longitude', None) 
                link_dict['altitude'] = getattr(gtw, 'altitude', None) 

                msg_dict['links'].append(link_dict)
           
            msg_json = json.dumps(msg_dict)
            r = requests.post('http://localhost:5000/receive_uplink', data=msg_json)
            # print(r)
        except Exception as e:
            print(e)



    def __init__(self, app_id, access_key):
        handler = ttn.HandlerClient(app_id, access_key)

        # using mqtt client
        mqtt_client = handler.data()
        mqtt_client.set_uplink_callback(TTNMQTTClient.uplink_callback)
        mqtt_client.connect()
        #time.sleep(60)
        #mqtt_client.close()        

    
    



'''

'''