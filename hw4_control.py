import sys
import socketserver
import math
import socket
import select




class BaseStation:
    def __init__(self, baseId, x, y, links):
        self.id = baseId
        self.x = x
        self.y = y
        self.links = links

    @staticmethod
    def create(line):
        line = line.split(' ')
        return BaseStation(line[0], line[1], line[2], line[4:])

    @staticmethod
    def createAll(path):
        l = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                l.append(BaseStation.create(line))
        return l
    #for debug
    def __str__(self):
        return "BaseStation::<id: {}, x: {}, y: {}, links: [{}]>".format(self.id, self.x, self.y,
                                                                         ", ".join(self.links))


class Sensor:
    def __init__(self):
        self.id = 0
        self.range = 0
        self.x = 0
        self.y = 0
        self.sd= -1
    #for debug
    def __str__(self):
        return "Sensor::<id: {}, range: {}, x: {}, y: {}, sd: {}>".format(
            self.id, self.range, self.x, self.y, self.sd
        )


#this function is used to find a sensor or base station of a specific id
def find_object(base_stations,sensors,id):
    for s in base_stations:
        if s.id==id:
            return s
    for s in sensors:
        if s.id==id:
            return s

#calculate the distance between different sensors/base stations
def get_distance(x1,y1,x2,y2):
    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)
    dis_square=math.pow((x2-x1),2)+math.pow((y2-y1),2)
    dis=math.sqrt(dis_square)
    return dis



#assuming that a base station isn't the destination,
# base station needs to make decisions about what is the next id
def next_id_decision(base_stations,sensors,current_id,dest,hoplist):
    sort_list=[]
    current_base=find_object(base_stations,sensors,current_id)
    #all base stations it can connect to
    for s in current_base.links:
        found=0
        if len(hoplist)>0:
            # check if it has been visited before
            for i in hoplist:
                if s == i:
                    found=1
        if found==0:
            for k in base_stations:
                if s==k.id:
                    sort_list.append(k)
                    break
    #all sensors it can reach
    for s in sensors:
        found=0
        if len(hoplist)>0:
            #check if it has been visited before
            for i in hoplist:
                if s.id == i:
                    found=1
        if found==0:
            #check if it's in range
            if get_distance(s.x,s.y,current_base.x,current_base.y) <= s.range:
                sort_list.append(s)
            break
    if len(sort_list)==0 :
        return
    else:
        # sorts all in-range sensors and base stations by distance to the destination
        sort_list.sort(key=lambda a:(get_distance(a.x,a.y,dest.x,dest.y),a.id))
        nextid=sort_list[0]
        return nextid.id




#this function represents the internal process when a data message start from a base station and loop until it find the
#next sensor to send tcp messages
def base_station_mes(base_stations,sensors,origin_base_id,origin_id,dest,message):
    current_id=origin_base_id
    while True:
        current_base=find_object(base_stations,sensors,current_id)
        #if this base station is the destination
        if current_id==dest.id:
            print(f"{current_id}: Message from {origin_id} to {dest.id} succesfully received.")
            return
        #otherwise
        next_id=next_id_decision(base_stations,sensors,current_id,dest,message[4])
        print(f"{current_id}: Message from {origin_id} to {dest.id} being forwarded through {current_id}")
        if next_id:
            # print(f"next id is:{next_id}")
            message[1] = next_id
            message[3]+=1
            message[4].append(current_id)
            is_base=0
            for s in base_stations:
                if s.id== next_id:
                    is_base=1
                    break
            current_id=next_id
            if is_base==0:
                for s in sensors:
                    if next_id==s.id:

                        return s
        else:
            print(f"{current_id}: Message from {origin_id} to {dest.id} could not be delivered.")
            return




#this function is used to implement the SENDDATA command
def senddata(base_stations,sensors,origin_id,dest_id):
    dest=find_object(base_stations,sensors,dest_id)
    if origin_id == "CONTROL":
        sort_list=[]
        hoplist=[]
        for s in base_stations:
            sort_list.append(s)
        sort_list.sort(key=lambda a: (get_distance(a.x, a.y, dest.x, dest.y),a.id))
        nextid = sort_list[0]
        hoplist.append("CONTROL")
        message = ["CONTROL",nextid , dest_id, 1, hoplist]
        next_sensor=base_station_mes(base_stations,sensors,nextid,"CONTROL",dest,message)
        if next_sensor:
            mes_send = "DATAMESSAGE {} {} {} {} {}\n".format(message[0], message[1], message[2], message[3],
                                                           " ".join(message[4]))
            next_sensor.sd.send(mes_send.encode('utf-8'))
    #if the origin is a base station
    else:
        hoplist = []
        message=[origin_id,origin_id , dest_id, 0, hoplist]
        current_base=find_object(base_stations,sensors,origin_id)
    # check if the message can be delivered directly
        for s in current_base.links:  #if the destination is a base station
            if s==dest_id:
                print(f"{origin_id}: Sent a new message directly to {dest_id}.")
                return
             # if the destination is a sensor
        dis=get_distance(current_base.x,current_base.y,dest.x,dest.y)
        if dis <= dest.range:
            print(f"{origin_id}: Sent a new message directly to {dest_id}.")
            message[1]=dest_id
            message[3]+=1
            message[4].append(origin_id)
            mes_send = "DATAMESSAGE {} {} {} {} {}\n".format(message[0], message[1], message[2], message[3],
                                                                     " ".join(message[4]))
            dest.sd.send(mes_send.encode('utf-8'))
            return
        #if the message cannot be delivered directly
        print(f"{origin_id}: Sent a new message bound for {dest_id}.")

        next_sensor=base_station_mes(base_stations,sensors,origin_id,origin_id,dest,message)
        if next_sensor:
            mes_send = "DATAMESSAGE {} {} {} {} {}\n".format(message[0], message[1], message[2], message[3],
                                                             " ".join(message[4]))
            next_sensor.sd.send(mes_send.encode('utf-8'))




#close all sensor sockets
def close_sockets(sensors):
    for s in sensors:
        s.sd.close()


#this function is used to implement UPDATAPOSITION request
def updateposition(base_stations,sensors,current_sensor,id,range,x,y):
    current_sensor.id = id
    current_sensor.range = range
    current_sensor.x = x
    current_sensor.y = y
    reachable_list = []
    #check all in-range base stations
    for s in base_stations:
        distance = get_distance(x, y, s.x, s.y)
        if distance <= range:
            new_entry = [s.id, s.x, s.y]
            reachable_list.append(" ".join(new_entry))
    #check all in-range sensors
    for s in sensors:
        if s.id == id:
            continue
        distance = get_distance(x, y, s.x, s.y)
        if distance <= range and distance <= s.range:
            new_entry = [s.id, s.x, s.y]
            reachable_list.append(" ".join(new_entry))
    mes_send = "REACHABLE {} {}\n".format(len(reachable_list), " ".join(reachable_list))
    # print(mes_send)
    return mes_send



#this function is used to implement WHERE request
def where(base_stations,sensors,nodeid):
    for s in base_stations:
        if s.id==nodeid:
            return "THERE [{}] [{}] [{}]".format(nodeid,s.x,s.y)
    for s in sensors:
        if s.id==nodeid:
            return "THERE [{}] [{}] [{}]".format(nodeid,s.x,s.y)


#this function is used to implement DATAMESSAGE request
def datames(base_stations,sensors,originid,nextid,destid,hoplength,hoplist):
    #If the server receives a data message with a [NextID] that is a sensor’s ID,
    # the server is acting as a sensor-to-sensor relay
    for s in sensors:
        if s.id==nextid:
            mes_send = "DATAMESSAGE {} {} {} {} {}\n".format(originid, nextid, destid,hoplength," ".join(hoplist))
            s.sd.send(mes_send.encode('utf-8'))
            return
    #If a base station receives a data message
    for s in base_stations:
        if s.id==nextid:
            message = [originid,nextid, destid, hoplength, hoplist]#this list is used to store content of messages
            dest = find_object(base_stations, sensors, destid)
            next_sensor = base_station_mes(base_stations, sensors, nextid,originid, dest, message,)
            if next_sensor:
                mes_send = "DATAMESSAGE {} {} {} {} {}\n".format(message[0], message[1], message[2], message[3],
                                                             " ".join(message[4]))
                next_sensor.sd.send(mes_send.encode('utf-8'))





if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('wrong')
        sys.exit(1)
    controlPort = int(sys.argv[1])
    baseStationFile = sys.argv[2]

    base_stations=BaseStation.createAll(baseStationFile)
    #debug
    # for l in base_stations:
    #     print(l.__str__())

    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('', controlPort))
    listening_socket.listen(5)

    sensors=[] #list used to store all sensors
    fd_set=[] #list used to store all file desciptor
    fd_set.append(sys.stdin)
    fd_set.append(listening_socket)
    while True:
        # if len(sensors) > 0 :
        #     for s in sensors:
        #         fd_set.append(s.sd)

        (rl,wl,el)=select.select(fd_set,[],[])
        for r in rl:
            #command from stdin
            if r is sys.stdin:
                command=sys.stdin.readline()
                command=command.split()
                # print("command is: {}".format(command))
                if command[0] == "SENDDATA":
                    senddata(base_stations,sensors,command[1],command[2])
                if command[0] == "QUIT":
                    close_sockets(sensors)
                    listening_socket.close()
                    sys.exit(0)
            #listen for coming sensors
            elif r is listening_socket:
                (sensor_socket, address) = listening_socket.accept()
                fd_set.append(sensor_socket)
                new_sensor = Sensor()
                new_sensor.sd=sensor_socket
                sensors.append(new_sensor)
            #deal with tcp messages from sensors
            else:
                for s in sensors:
                    if r is s.sd:
                        message = s.sd.recv(128)
                        message = message.decode('utf-8')
                        if message[-1] is '\n':
                            message=message[:-1]
                        message = message.split(' ')
                        # print("message is: {}".format(message))
                        if message[0] == "UPDATEPOSITION":
                            mes_send=updateposition(base_stations,sensors,s,message[1],int(message[2]),message[3],message[4])
                            s.sd.send(mes_send.encode('utf-8'))
                        if message[0] == "WHERE":
                            mes_send=where(base_stations,sensors,message[1])
                            s.sd.send(mes_send.encode('utf-8'))
                        if message[0] == "DATAMESSAGE":
                            datames(base_stations,sensors,message[1],message[2],message[3],int(message[4]),message[5:])





