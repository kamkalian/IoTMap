from math import pi, cos, radians, sin, sqrt, pi
from app.models import MessageLink, Message


class GridViewPreparation():


    def __init__(self):
        self.r_equator = 6378,137
        self.r_pole = 6356,752

        # Entfernung um einen gemessenen Punkt
        self.distance_in_a_circle = 10

        # Entfernung zwischen den Breitenkreisen
        self.distance_circle_of_width = 111300

        # Schritt für Latitude mit angegebener distance_in_a_circle
        self.lat_step = self.distance_in_a_circle / self.distance_circle_of_width

        self.load_messages()

    
    def u_earth(self, lat):
        """Umfang der Erde in abhängigkeit vom Breitengrad(Latitude) ausrechnen"""
        # Formel R = √ [ (r1² * cos(B))² + (r2² * sin(B))² ] / [ (r1 * cos(B))² + (r2 * sin(B))² ] 
        u_earth_tmp = (self.r_equator^2 * cos(lat))^2
        u_earth_tmp1 = (self.r_pole^2 * sin(lat))^2
        u_earth_tmp2 = (self.r_equator * cos(lat))^2
        u_earth_tmp3 = (self.r_pole * sin(lat))^2

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
            Message.dev_id
            ).all()

        self.message_link_dict = {}
        for message_link in message_link_query_result:

            gtw_id = message_link[0]
            rssi = message_link[1]
            lat = message_link[2]
            lon = message_link[3]
            dev_id = message_link[4]
            print(dev_id)

            # TODO lat und lon beschneiden, so das alle Punkte ein Raster bilden.

            # Dict zusammenbauen
            # TODO bei doppelten Einträgen braucht es eine extra Behandlung
    
            lat_dict = None
            lon_dict = None
            gtw_dict = None
            if lat in self.message_link_dict:
                lat_dict = self.message_link_dict[lat]
            if lat_dict and lon in lat_dict:
                lon_dict = lat_dict[lon]
            if lon_dict and gtw_id in lon_dict:
                gtw_dict = lon_dict[gtw_id]
            
            if gtw_dict and rssi < gtw_dict['rssi']:
                gtw_dict['rssi'] = rssi
            
            if lon_dict and not gtw_dict:
                print(lon_dict)
                lon_dict[gtw_id] = {
                            "rssi": rssi,
                            "dev_id": dev_id
                        }

            if lat_dict and lon_dict and gtw_dict:
                pass
            else:
                self.message_link_dict[lat] = {
                    lon: {
                        gtw_id: {
                            "rssi": message_link[1],
                            "dev_id": message_link[4]
                        }
                    }
                }

        for lat in self.message_link_dict:
            print(lat)
            for lon in self.message_link_dict[lat]:
                print("   ", lon)
                for gtw_id in self.message_link_dict[lat][lon]:
                    print("      ", gtw_id)
                    print("         ", 
                        self.message_link_dict[lat][lon][gtw_id]['rssi'],
                        self.message_link_dict[lat][lon][gtw_id]['dev_id']
                        )
            


    def join_messages(self):
        pass


    def cut_lon(self, lon, meters):
        pass


    def lon_step(self, lat):
        """Rechnet den Schritt mit der eingestellte Entfernung in Abhängigkeit des
        Umfangs der Erde aus.
        
        Dabei ist der Umfang der Erde wiederum abhängig von der Latitude des Punktes.
        """
        lon_step = (360 * self.distance_in_a_circle) / self.u_earth(lat)
        return lon_step
