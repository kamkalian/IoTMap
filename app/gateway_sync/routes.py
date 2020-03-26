#!/venv/bin/python3
from app.gateway_sync import bp
from flask import render_template
from app.gateway_sync import ttn_sync

@bp.route('/run_ttn_sync')
def run_ttn_sync():
    
    center_lat = '50.820329'
    center_lon = '7.141111'
    distance = '25000'

    new_gw_list, update_gw_list = ttn_sync.ttn_sync(center_lat, center_lon, distance)

    return render_template(
        'result_ttn_sync.html',
        title=u'FFRS-TTN-Map',
        new_gw_list=new_gw_list,
        update_gw_list=update_gw_list)