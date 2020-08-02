from math import pi, cos, radians, sin, sqrt, pi, fmod
from app.models import MessageLink, Message
from sqlalchemy import desc


class GridViewPreparation():


    def __init__(self):
        self.r_equator = 6378.137
        self.r_pole = 6356.752

        # Entfernung um einen gemessenen Punkt
        self.distance_in_a_circle = 5

        # Entfernung zwischen den Breitenkreisen
        self.distance_circle_of_width = 111300

        # Schritt für Latitude mit angegebener distance_in_a_circle
        self.lat_step = self.distance_in_a_circle / self.distance_circle_of_width *2

        self.load_messages()

    
    def u_earth(self, lat):
        """Umfang der Erde in abhängigkeit vom Breitengrad(Latitude) ausrechnen"""
        # Formel R = √ [ (r1² * cos(B))² + (r2² * sin(B))² ] / [ (r1 * cos(B))² + (r2 * sin(B))² ] 
        u_earth_tmp = (self.r_equator**2 * cos(lat))**2
        u_earth_tmp1 = (self.r_pole**2 * sin(lat))**2
        u_earth_tmp2 = (self.r_equator * cos(lat))**2
        u_earth_tmp3 = (self.r_pole * sin(lat))**2

        u_earth = ((u_earth_tmp + u_earth_tmp1) / (u_earth_tmp2 + u_earth_tmp3)) * pi

        return u_earth


    def load_messages(self):
        message_link_query_result = MessageLink.query.join(
            Message
            ).with_entities(
            MessageLink.gtw_id,
            MessageLink.rssi,
            Message.latitude, 
            Message.longitude,
            Message.dev_id,
            Message.time
            ).order_by(desc(Message.time)).limit(20000).all()

        self.message_link_list = []
        for message_link in message_link_query_result:
            gtw_id = message_link[0]
            rssi = message_link[1]
            lat = float(message_link[2])
            lon = float(message_link[3])
            dev_id = message_link[4]
            time = message_link[5]

            # Latitude beschneiden
            trimmed_lat = lat - fmod(lat, self.lat_step)

            # Step für Longitude bestimmen und dann damit die Longitude trimmen            
            lon_step = self.lon_step(trimmed_lat)
            trimmed_lon = lon - fmod(lon, lon_step)

            # List mit Messages als Dict zusammenbauen,
            # dabei wird geschaut ob es doppelte Koordinaten gibt.
            equal_item = None
            for item in self.message_link_list:
                if item.get('lat', 0) == trimmed_lat and item.get('lon', 0) == trimmed_lon:
                    equal_item = item

            if not equal_item:     
                item_dict = {
                    "lat": trimmed_lat,
                    "lon": trimmed_lon,
                    "rssi": rssi,
                    "time": time
                }
                self.message_link_list.append(item_dict)
            else:
                new_rssi = (equal_item.get("rssi", 0) + rssi) / 2
                equal_item.update({"rssi": new_rssi})


    def lon_step(self, lat):
        """Rechnet den Schritt mit der eingestellte Entfernung in Abhängigkeit des
        Umfangs der Erde aus.
        
        Dabei ist der Umfang der Erde wiederum abhängig von der Latitude des Punktes.
        """
        lon_step = (360 * self.distance_in_a_circle) / self.u_earth(lat)*10
        print(lon_step)
        return lon_step


    def geo_json(self):
        """Gibt von den konsolidierten Messages ein GeoJson zurück"""
        geo_json = { 'type': 'FeatureCollection' }
        features = []

        for item in self.message_link_list:

            # Farben über den RSSI Wert festlegen
            rssi = item["rssi"]
            color = "#999999"
            if rssi <= 0 and rssi > -99:
                color = "#FF0000"
            if rssi <= -99 and rssi > -104:
                color = "#FF7F00"
            if rssi <= -104 and rssi > -109:
                color = "#FFFF00"
            if rssi <= -109 and rssi > -114:
                color = "#00FF00"
            if rssi <= -114 and rssi > -119:
                color = "#00FFFF"
            if rssi <= -114 and rssi > -200:
                color = "#0000FF"

            # feature aus allen Daten zusammensetzen und dem features dict hinzufügen
            feature = { 
                'type': 'Feature', 
                'geometry': {'type': 'Point', 'coordinates': [item["lon"], item["lat"]] },
                'properties': {
                    'time': item["time"],
                    'rssi': rssi,
                    'color': color,
                    },
            }
            features.append(feature)
    
        geo_json['features'] = features

        return geo_json