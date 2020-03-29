from math import sin, cos, sqrt, atan2, radians

r_earth = 6373.0


def meters(p1, p2):    
    
    dlat = radians(p2[0]-p1[0])
    dlon = radians(p2[1]-p1[1])
    
    a = sin(dlat / 2)**2 + cos(p1[0]) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = r_earth * c * 1000

    return distance


def nearest_msg(msg_list, current_msg, max_distance):

    smallest_msg = None
    smallest_distance = None

    for msg in msg_list:

        # Wenn die msg gleich der current_msg ist wird diese msg übersprungen
        if current_msg.msg_id == msg.msg_id:
            continue

        # Distanz zwichen dem Aktuellen und dem Punkt in der Liste bestimmen
        distance = meters([msg.latitude, msg.longitude], [current_msg.latitude, current_msg.longitude])

        # Ist die ermittelte Distanze kleiner als die bisherige kleineste Distanze,
        # so wird die kleineste Distanze angepasst.
        if smallest_distance == None or distance < smallest_distance:
            smallest_msg = msg
            smallest_distance = distance

    if smallest_msg != None and smallest_distance <= max_distance:
        return smallest_msg, smallest_distance
    
    return None, None


def msg_cluster(msg_list, max_distance):

    cluster = []
    
    while len(msg_list) > 1:

        # Temporäre Liste in der die Messages pro Cluster rein kommen.
        tmp_msg_list = []

        # Ersten nähstgelegenen Punkt finden 
        n_msg, n_distance = nearest_msg(msg_list, msg_list[0], max_distance)

        # Erste Message hinzufügen und von der msg_list entfernen
        tmp_msg_list.append(msg_list[0])
        msg_list.remove(msg_list[0])
        
        while n_msg and len(msg_list) > 1:

            #nähstgelegenen Punkt von der Liste entfernen
            msg_list.remove(n_msg)

            # nähstgelegenen Punkt ermittlen
            n_msg, n_distance = nearest_msg(msg_list, n_msg, max_distance)

            # Wenn es einen nähstgelegenen Punkt gibt wird dieser zum aktuellen Polygon hinzugefügt.
            if n_msg:
                tmp_msg_list.append(n_msg)

        # Wenn mehr als 2 Messages in der temporären Liste drinnen sind wird sie zum cluster hinzugefügt.
        if len(tmp_msg_list) > 2:
            cluster.append(tmp_msg_list)
    
    return cluster


def nearest_msg_to_gateway(msg_list, gateway):

    smallest_msg = None
    smallest_distance = None

    for msg in msg_list:

        # Distanz zwichen dem Aktuellen und dem Punkt in der Liste bestimmen
        distance = meters([msg.latitude, msg.longitude], [gateway.latitude, gateway.longitude])

        # Ist die ermittelte Distanze kleiner als die bisherige kleineste Distanze,
        # so wird die kleineste Distanze angepasst.
        if smallest_distance == None or distance < smallest_distance:
            smallest_msg = msg
            smallest_distance = distance

    return smallest_msg