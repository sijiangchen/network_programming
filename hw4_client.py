import sys
import socket
import math
import select


class ListItem:
    def __init__(self, id, x, y):
        self.x = x
        self.y = y
        self.id = id

    def idMatch(self, id):
        return self.id == id

    ##implamented for sorting to break ties in lexographical order
    def __lt__ (self, other):
    	return self.id < other.id


class Sensor:
    def __init__(self, controlAddress, controlPort, id, range, x, y):
        self.controlAddress = controlAddress
        self.controlPort = controlPort
        self.id = id
        self.range = range
        self.x = x
        self.y = y
        self.reachable = []
        self.NumReachable = 0
    
    def __str__(self):
        return "Sensor::<addr: {}, port: {}, id: {}, range: {}, x: {}, y: {}>".format(
            self.controlAddress, self.controlPort, self.id, self.range, self.x, self.y
        )
    def UPDATEPOSITION(self):
     	return "UPDATEPOSITION "+ self.id + " "+ str(self.range) + " " + str(self.x)+ " " + str(self.y)

    def buildList(self, received):
        recvList = received.decode('utf-8').split(" ")
        self.NumReachable = int(recvList[1])
        recvList.pop(0)
        recvList.pop(0)
        tmp = []
        self.reachable.clear()
        for item in recvList:
            if len(tmp) == 3:
            	self.reachable.append(ListItem(tmp[0], int(tmp[1]), int(tmp[2])))
            	tmp = []
            tmp.append(item)
        self.reachable.sort()
        	

    def printReachable(self):
        for item in self.reachable:
            print(item.id)

    def sendDataMessageIntitial(self, destionID, nextID, server_socket):
    	hopList = []
    	server_socket.sendall(sensor.UPDATEPOSITION().encode('utf-8'))
    	recv_string = server_socket.recv(1024)
    	self.buildList(recv_string)
    	hopList.append(self.id)
    	nextID = self.GetNextId(self.HandleWhere(destionID, server_socket))
    	destionID = destionID.strip()
    	if nextID == 0:
    		print_str = self.id + ": Message from " + self.id + " to " + destionID + " could not be delivered."
    		print(print_str)
    	elif (nextID.strip()) == (destionID.strip()):
    		print(self.id + ": Sent a new message directly to " + destionID +".")
    	else:
    		print_str = self.id + ": Message from " + self.id + " to " + destionID + " being fowarded through " + nextID + "."
    		print(print_str)
    	str_send = "DATAMESSAGE " + self.id + " " + nextID + " " + destionID + " " + str(len(hopList)) + " " + " ".join(hopList)+"\n"
    	server_socket.sendall(str_send.encode('utf-8'))

    def HandleWhere(self, destionID, server_socket):
        server_socket.sendall(("WHERE " + destionID).encode('utf-8'))
        recv_string = server_socket.recv(1024).decode('utf-8')
        thereArgs = recv_string.split(" ")
        return thereArgs

    def distanceFormula(self, x, y):
        return math.sqrt(((self.x - x)**2) + ((self.y - y)**2))

    def removeBrackets(string):
    	ret = ""
    	i = 1
    	while string[i] != ']':
    		ret += string[i]
    		i+=1
    	return ret

    def GetNextId(self, thereArgs):
        destionID = removeBrackets(thereArgs[1])
        destx = int(removeBrackets(thereArgs[2]))
        desty= int(removeBrackets(thereArgs[3]))
        dist = 0
        currentID= 0
        distSet = 0
        for item in sensor.reachable:
    	    if item.id == destionID:
    	       return item.id
    	    elif  distSet == 0:
               distSet = 1
               dist = distanceFormula(destx,desty,item.x, item.y)
               currentID = item.id
    	    elif distanceFormula(destx,desty,item.x, item.y) < dist:
               dist = distanceFormula(destx,desty,item.x, item.y)
               currentID = item.id
        return currentID



    def AllInHopLists(self, hopList):
    	allInList = True
    	for item in self.reachable:
        	allInList = allInList and (item.id in hopList)
    	return allInList


    def HandleDataMessage(self, dataMessageArgs, server_socket):
    	orginID = dataMessageArgs[1]
    	nextID = dataMessageArgs[2]
    	destionID = dataMessageArgs[3]
    	hopList = dataMessageArgs[5]
    	server_socket.sendall(sensor.UPDATEPOSITION().encode('utf-8'))
    	recv_string = server_socket.recv(1024)
    	self.buildList(recv_string)
    	hopList.append(self.id)
    	if nextID == 0:
    		print_str = self.id + ": Message from " + self.id + " to " + destionID + " could not be delivered."
    		print(print_str)
    	elif destionID == self.id:
    		print_str = self.id+": Message from " + orginID + " to " + destionID + "successfully received."
    		print(print_str)
    	elif AllInHopList(hopList):
    		print_str = self.id +": Message from " + orginID + " to " + destionID + "could not be delivered."
    		print(print_str)
    	else:
    		nextID = self.GetNextId(self.HandleWhere(destionID, server_socket))
    		str_send = "DATAMESSAGE " + self.id + " " + nextID + " " + destionID + " " + str(len(hopList)) + " ".join(hopList)+"\n"
    		server_socket.sendall(str_send.encode('utf-8'))
    		if nextID == destionID:
    			print(self.id + ": Sent a new message directly to " + destionID +".")
    		else:
    			print_str = self.id + ": Message from " + orginID + " to " + destionID + " being fowarded through " + nextID+"."
    			print(print_str)



    def GetNextId(self, thereArgs):
	    destionID = thereArgs[1]
	    sensor.printReachable()
	    destx = int(removeBrackets(thereArgs[2]))
	    desty= int(removeBrackets(thereArgs[3]))
	    dist = 0
	    currentID= 0
	    distSet = 0
	    for item in sensor.reachable:
	    	if item.id == destionID:
	    		return item.id
	    	elif  distSet == 0:
	    		distSet = 1
	    		dist = distanceFormula(destx,desty,item.x, item.y)
	    		currentID = item.id
	    	elif distanceFormula(destx,desty,item.x, item.y) < dist:
	    		dist = distanceFormula(destx,desty,item.x, item.y)
	    		currentID = item.id
	    return currentID

def distanceFormula(destx,desty,x, y):
    return math.sqrt(((destx - x)**2) + ((desty - y)**2))

def removeBrackets(string):
	ret = ""
	i = 1
	while string[i] != ']':
		ret += string[i]
		i+=1
	return ret

def GetNextId(sensor, thereArgs):
	destionID = removeBrackets(thereArgs[1])
	destx = int(removeBrackets(thereArgs[2]))
	desty= int(removeBrackets(thereArgs[3]))
	dist = 0
	currentID= 0
	distSet = 0
	for item in sensor.reachable:
		if item.id == destionID:
			return item.id
		elif  distSet == 0:
			dist = distanceFormula(destx,desty,item.x, item.y)
			if dist < sensor.range:
				currentID = item.id
				distSet = 1
		elif distanceFormula(destx,desty,item.x, item.y) < dist:
			dist = distanceFormula(destx,desty,item.x, item.y)
			if dist < sensor.range:
				currentID = item.id
	return currentID



if __name__ == "__main__":
	##argument check
    if len(sys.argv) < 7:
        print('wrong')
        sys.exit(1)
    controlAddress = sys.argv[1]
    controlPort = int(sys.argv[2])
    id = sys.argv[3]
    range = int(sys.argv[4])
    x = sys.argv[5]
    y = sys.argv[6]
    sensor = Sensor(controlAddress, controlPort, id, range, x, y)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(controlAddress)
    server_socket.connect((ip, controlPort))
    server_socket.sendall(sensor.UPDATEPOSITION().encode('utf-8'))
    sensor.buildList(server_socket.recv(1024))
    fd_set = []
    fd_set.append(sys.stdin)
    fd_set.append(server_socket)
    while True:
    	(rl,wl,el)=select.select(fd_set,[],[])
    	for r in rl:
    		#from command line
            if r is sys.stdin:
                line=sys.stdin.readline()
                if line.startswith("MOVE "):
             	   line = line.split(" ")
             	   sensor.x = int(line[1])
             	   sensor.y = int(line[2])
             	   server_socket.sendall(sensor.UPDATEPOSITION().encode('utf-8'))
             	   recv_string = server_socket.recv(1024)
             	   sensor.buildList(recv_string)
                elif line.startswith("SENDDATA "):
                	server_socket.sendall(sensor.UPDATEPOSITION().encode('utf-8'))
                	recv_string = server_socket.recv(1024)
                	sensor.buildList(recv_string)
                	line = line.split(" ")
                	##sendDataMessageIntitial(self, destionID, nextID, server_socket):
                	sensor.sendDataMessageIntitial(line[1],"", server_socket)
                elif line.startswith("WHERE "):
                    sensor.HandleWhere(line.split(" ")[1], server_socket)
                elif line.startswith("QUIT"):
                    server_socket.close()
                    sys.exit(0)
                else:
                    print('unknown command')
            #from server
            elif r is server_socket:
                sensor.HandleDataMessage(server_socket.recv(1024).decode('utf-8').split(" "), server_socket)
                
