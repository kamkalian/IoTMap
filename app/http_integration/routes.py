from app.http_integration import bp
from flask import request, jsonify
import json


@bp.route('/ttn_tracker', methods=['POST'])
def ttn_tracker():

    data = request.get_json()
    try:
        #payload_fields = json.loads(data["payload_fields"])
        payload_fields = data["payload_fields"]
        latitude = payload_fields["latitude"]
        longitude = payload_fields["longitude"]

        print(latitude, longitude)

    except KeyError as e:
        print("error:",e)
    
    

    return {"ok": 1}