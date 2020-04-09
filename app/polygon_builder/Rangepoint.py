



class Rangepoint():
    '''
    Ein Rangepoint ist ein einzelner Punkt mit Latitude, Longitude und Altitude 
    der zusätlich die Empfangsstärke(RSSI) zu einem Gateway und einen Zeitstempel definiert hat.
    Als Gateway wird eine eindeutige ID angegeben.
    '''

    def __init__(self, latitude, longitude, altitude, rssi, gateway_id):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.rssi = rssi
        self.gateway_id = gateway_id
