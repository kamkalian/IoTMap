from app.polygon_builder.Rangepoint import Rangepoint
import json
from shapely.geometry import Polygon, MultiPolygon
from math import sin, cos, sqrt, atan2, radians
import time


class Rangearea():
    '''
    Mit dieser Klassen kann man mehrere Polygone von einem gemeinsamen Startpunkt aus generieren, 
    die dann zur Darstellung z.B. auf einer Leaflet Karte im GeoJson Format abgerufen werden.
    Der Startpunkt ist z.B. ein Gateway bei dem die Empfangsreichweiten dargestellt werden sollen.
    Mehrere Rangepoints die als Liste übergeben werden, 
    enthalten die GPS Koordinaten und die Empfangsstärke(RSSI) des empfangenen Gateways.
    Weit ausseinander liegende Rangepoint-Wolken werden in seperate Polygone aufgeteilt.
    Auch für unterschiedlichen RSSI Bereiche können seperate Polygone erstellt werden. 
    '''

    def __init__(self):
        self.rssi_area_list = []
        self.range_point_list = []
        self.range_point_cluster_list = []
        self.polygon_list = []
        self.gateway_list = []
        self.shapely_polygon_list = []


    @staticmethod
    def range_point(latitude, longitude, altitude, rssi, gateway_id):
        return Rangepoint(latitude, longitude, altitude, rssi, gateway_id)


    def add_range_point_list(self, range_point_list):
        '''
        Fügt eine Liste mit Rangepoints hinzu.
        '''

        self.range_point_list = range_point_list


    def add_rssi_range(self, rssi_min, rssi_max, fill_color):
        '''
        Fügt einen weiteren Empfangsstärkebereich hinzu, bei dem das Polygon,
        in der mit fill_color angegebenen Farbe gefüllt wird.
        Alles was größer als rssi_min und kleiner als rssi_max ist fällt in diesen Bereich.
        '''

        self.rssi_area_list.append({
            'rssi_min': rssi_min,
            'rssi_max': rssi_max,
            'fill_color': fill_color, 
            'temp_point_list': []
        })

    
    def add_polygon(self, gtw_id, fill_color, coord_list):
        self.polygon_list.append({
            'gtw_id': gtw_id,
            'fill_color': fill_color,
            'coords': coord_list
            }
        )

    
    def add_gateway(self, gtw_id, latitude, longitude):
        self.gateway_list.append(
            {
                'gtw_id': gtw_id,
                'latitude': latitude,
                'longitude': longitude
            }
        )


    def analyse(self):
        '''
        Dies ist das Herzstück der Klasse, hier werden die range_points analysiert
        und auf Gateways, RSSI Bereiche und Cluster aufgeteilt.
        '''

        start_time = time.time()
        print('[', 0, ']: ', 'Start analyse()')

        # Ermittle Gateways
        #self.gateway_id_list = []

        '''
        for range_point in self.range_point_list:
            if range_point.gateway_id not in self.gateway_id_list:
                self.gateway_id_list.append(range_point.gateway_id)
        '''

        # print('Anzahl Gateways: ', len(self.gateway_list))

        # Schleife über alle Gateways, dabei wird die polygon_list geleert
        self.polygon_list = []
        i = 0
        for gateway in self.gateway_list:

            # if gateway['gtw_id'] != 'eui-313532352e005300':
            #    continue

            i += 1

            # print('### ', i, gateway['gtw_id'])

            # Variable für temporäre Koordinaten, 
            # die benutzt werden wenn alle Punkte in ein Polygon rein kommen (keine RSSI Bereiche).
            temp_coords = []

            # Prüfen ob es mehrere RSSI Bereiche gibt.
            rssi_split = False
            if len(self.rssi_area_list) > 0:

                rssi_split = True

                # Die temporären Koordinaten Listen in rssi_area müssen für jede Gateway entleert werden
                for rssi_area in self.rssi_area_list:
                    rssi_area['temp_point_list'] = []

            # Schleife über alle Rangepoints:
            c = 0
        current_time = time.time()
        diff_time = round(time.time() - start_time, 2)
        total_time = round(time.time() - start_time, 2)
        print('[', diff_time, total_time, ']: ', 'Anzahl range_point:', len(self.range_point_list))
            for range_point in self.range_point_list:


                # Nur die Punkte nehemen die zum aktuell selektierten Gateway gehören
                if range_point.gateway_id == gateway['gtw_id']:

                    c += 1

                    # Wenn es RSSI Bereiche gibt werden die Punkte auf die RSSI Bereich aufgeteilt
                    if rssi_split:
                        
                        # Prüfen in welchen RSSI Bereich der Punkt fällt
                        for rssi_area in self.rssi_area_list:
                            
                            if (range_point.rssi >= rssi_area['rssi_min'] and range_point.rssi <= rssi_area['rssi_max']) or range_point.rssi == 0:

                                rssi_area['temp_point_list'].append([range_point.longitude, range_point.latitude])
                                
                                if range_point.rssi != 0:
                                    break

                    # Ansonste wird alles in ein Polygon gesteckt 
                    else:

                        temp_coords.append([range_point.longitude, range_point.latitude])

        diff_time = round(time.time() - current_time, 2)
        total_time = round(time.time() - start_time, 2)
        current_time = time.time()
        # print('Anzahl Points: ', c)
        print('[', diff_time, total_time, ']: ', 'Points per RSSI: ', [len(r['temp_point_list']) for r in self.rssi_area_list])

            # Hier wird die polygon_list gefüllt, entweder für jeden RSSI Bereich ein Polygon,
            # oder nur ein Polygon mit allen Punkten
            if rssi_split: 

                # RSSI Bereiche durchgehen und jeweils die Koordinaten raus holen
                prio = 100
                for rssi_area in self.rssi_area_list:

                    # Priorität nach runterzählen
                    prio -= 1

                    if len(rssi_area['temp_point_list']) > 2:

                    diff_time = round(time.time() - current_time, 2)
                    total_time = round(time.time() - start_time, 2)
                    current_time = time.time()
                    print('[', diff_time, total_time, ']: ', rssi_area['rssi_min'], '-', rssi_area['rssi_max'])
                    print('[', diff_time, total_time, ']: ', 'Anzahl temp_point_list:', len(rssi_area['temp_point_list']))
                    diff_time = round(time.time() - current_time, 2)
                    total_time = round(time.time() - start_time, 2)
                    current_time = time.time()
                    print('[', diff_time, total_time, ']: ', 'Anzahl Cluster:', len(cluster_list))
                        for cluster in cluster_list:

                            convex_polygon = None

                            try:
                            
                                # Convexe Hülle generieren, dazu wird mit Shapely ein Polygon erstellt.
                                # An den Cluster wird noch der Punkt vom Gateway dran gehangen.
                                # polygon = Polygon(cluster + [[gateway['longitude'], gateway['latitude']]])
                                polygon = Polygon(cluster)

                                convex_polygon = polygon.convex_hull

                            except:
                                print('error in analyse')

                            # Nur das Polygon hinzufügen wenn es auch ein Polygon ist.
                            if type(convex_polygon) is Polygon:
                                
                                # Das Polygon der shapely_polygon_list hinzufügen
                                self.shapely_polygon_list.append(
                                    {
                                        'prio': prio, 
                                        'polygon': convex_polygon,
                                        'fill_color': rssi_area['fill_color'],
                                        'gtw_id': gateway['gtw_id']
                                    }
                                )
                                '''
                                elif type(convex_polygon) is MultiPolygon:

                                    for poly in convex_polygon:

                                        self.shapely_polygon_list.append(
                                        {
                                            'prio': prio, 
                                            'polygon': poly,
                                            'fill_color': rssi_area['fill_color']})
                                '''

                            else:
                                print(type(convex_polygon))

        diff_time = round(time.time() - current_time, 2)
        total_time = round(time.time() - start_time, 2)
        current_time = time.time()
        print('[', diff_time, total_time, ']: ', 'Anzahl shapely Polygone: ', len(self.shapely_polygon_list))
        
        for shapely_polygon in self.shapely_polygon_list:

            for shapely_polygon1 in self.shapely_polygon_list:

                if shapely_polygon1['prio'] > shapely_polygon['prio']:
                    try:
                        
                        shapely_polygon['polygon'] = shapely_polygon['polygon'].difference(shapely_polygon1['polygon'])
                    except Exception as e:
                        print('difference nicht möglich')

            if type(shapely_polygon['polygon']) is Polygon:
                temp_coords = [[r[0], r[1]] for r in shapely_polygon['polygon'].exterior.coords]

                self.polygon_list.append({
                    'gtw_id': shapely_polygon['gtw_id'],
                    'fill_color': shapely_polygon['fill_color'],
                    'coords': temp_coords
                })
        
        diff_time = round(time.time() - current_time, 2)
        total_time = round(time.time() - start_time, 2)
        current_time = time.time()
        print('[', diff_time, total_time, ']: ', 'Anzahl final shapely Polygons: ', len(self.polygon_list))

        '''
        if len(temp_coords) > 2:

            cluster_list = self._cluster_list(temp_coords, 300)

            for cluster in cluster_list:

                # Convexe Hülle generieren, dazu wird mit Shapely ein Polygon erstellt
                polygon = Polygon(cluster + [[gateway['longitude'], gateway['latitude']]])
                convex_polygon = polygon.convex_hull

                # Nur das Polygon hinzufügen wenn es auch ein Polygon ist.
                if type(convex_polygon) is Polygon:
                    
                    temp_coords = [[r[0], r[1]] for r in convex_polygon.exterior.coords]

                    # Polygon mit allen ermittelten Punkten zur Liste hinzufügen
                    self.polygon_list.append({
                        'fill_color': '#ff0000',
                        'coords': temp_coords
                    })
        
        '''

    
    def _cluster_list(self, temp_point_list, max_distance):
        '''
        Bildet mehrere sogenannte Cluster, die im Prinzip Wolken von nahe beieinander 
        liegenden Punkten enthalten und gibt sie als Liste zurück. 
        Dabei entscheidet max_distance wie weit die Punkte
        maximal von einander entfernt sein dürfen.
        '''

        # print('####### _cluster_list()')

        # print('##########')
        # print(temp_point_list)
        # print('##########')

        # Liste mit Polygonen je Bereich
        cluster_list = []

        # Temporäre Liste in der die Punkte pro Cluster rein kommen.
        cluster_points = []
        
        # Solange die temp_point_list durchgehen bis keine Punkte mehr da sind.
        while len(temp_point_list) > 0:

            # print('Anzahl temp_point_list: ', len(temp_point_list))
        
            # nähstgelegenen Punkt finden 
            n_point, n_distance = self._nearest_point(temp_point_list, cluster_points, max_distance)
            # print('nearest: ', n_point, n_distance)

            # Wurde ein nächstegelegener Punkt gefunden?
            if n_point != None:

                # Punkt hinzufügen und von der temp_point_list entfernen
                cluster_points.append(n_point)
                temp_point_list.remove(n_point)

            # Wenn kein nächstegelegener Punkt gefunden wurde, 
            # werden die bisherigen Punkte der cluster_list hinzugefügt
            else:

                # Wenn mehr als 2 Messages in der temporären Liste drinnen sind wird sie zum cluster hinzugefügt.
                if len(cluster_points) > 2:
                    cluster_list.append(cluster_points)

                    # print('----------------------')
                    # print('cluster: ', cluster_list)
                    # print('----------------------')

                # cluster_points entleeren
                cluster_points = []

        # Sind noch Punkte im Cluster drinnen werden diese auch noch zur cluster_list hinzugefügt.
        if len(cluster_points) > 2:

            cluster_list.append(cluster_points)
        # print('cluster_list: ', cluster_list)
        # print('')
        # print('')
        return cluster_list

    
    def _nearest_point(self, temp_point_list, cluster_points, max_distance):

        smallest_point = None
        smallest_distance = None

        for point in temp_point_list:

            if len(cluster_points) > 0:

                for cp in cluster_points:

                    # Distanz zwichen dem cp Punke und dem Punktpoint aus der Liste bestimmen
                    distance = self._meters(cp, point)

                    # Ist die ermittelte Distanze kleiner als die bisherige kleineste Distanze,
                    # so wird die kleineste Distanze angepasst.
                    if smallest_distance == None or distance < smallest_distance:
                        smallest_point = point
                        smallest_distance = distance


            else:
                return temp_point_list[0], None

        if smallest_point != None and smallest_distance <= max_distance:
            return smallest_point, smallest_distance
        
        return None, None


    def _meters(self, p1, p2):  

        # print('meters ', p1, p2)
        r_earth = 6373.0
    
        dlat = radians(p2[0]-p1[0])
        dlon = radians(p2[1]-p1[1])
        
        a = sin(dlat / 2)**2 + cos(p1[0]) * sin(dlon / 2)**2
        # print('a: ', a)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = r_earth * c * 1000
        # print(distance)
        return distance


    def _feature(self, polygon_coords, fill_color):
        '''
        Gibt ein GeoJson Feature zurück.
        '''

        # Feature erstellen und zu poly_features hinzufügen
        feature = {
            'type': 'Feature',
            'fill_color': fill_color,
            'geometry': {'type': 'Polygon', 'coordinates': [
                polygon_coords
                ]}
        }
    
        return feature

    
    def _features(self):
        '''
        Erstellt aus mehreren features eine Liste.
        '''

        feature_list = []
        for polygon in self.polygon_list: 
            feature_list.append(self._feature(polygon['coords'], polygon['fill_color']))

        return feature_list


    def geo_json(self):

        geo_json_dict = { 'type': 'FeatureCollection' }

        geo_json_dict['features'] = self._features()

        return json.dumps(geo_json_dict)