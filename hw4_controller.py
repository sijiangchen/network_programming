import sys
import socketserver

class BaseStation:
    def __init__(self, controller, baseId, x, y, links):
        self.controller = controller
        self.id = baseId
        self.x = x
        self.y = y
        self.links = links
    
    @staticmethod
    def create(controller, line):
        line = line.split(' ')
        return BaseStation(controller, line[0], line[1], line[2], line[4:])

    @staticmethod
    def createAll(controller, path):
        l = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                l.append(BaseStation.create(controller, line))
        return l

    def __str__(self):
        return "BaseStation::<id: {}, x: {}, y: {}, links: [{}]>".format(self.baseId, self.x, self.y, ", ".join(self.links))

class Controller:
    def __init__(self, port, baseStationFile):
        self.port = port
        self.baseStations = BaseStation.createAll(self, baseStationFile)

        class RequestHandler(socketserver.BaseRequestHandler):
            def handle(self):
                # Read TCP Request for
                # WHERE <Id>
                #     Responds with THERE <NodeId> <X> <Y> 
                # UPDATEPOSITION
                #     Responds with REACHABLE <NumReachable> <ReachableList>
                pass
        self.server = socketserver.TCPServer(("localhost", port), RequestHandler)
    
    def listen(self):
        self.server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('wrong')
        sys.exit(1)
    controlPort = int(sys.argv[1])
    baseStationFile = sys.argv[2]

    controller = Controller(controlPort, baseStationFile)
    
    # read stdin here for
    # SENDDATA <originId> <destinationId>
    # QUIT
    for line in sys.stdin:
        if line.startswith("SENDDATA "):
            print('senddata')
        elif line.startswith("QUIT"):
            print('shutting down.')
            sys.exit(0)
        else:
            print('unknown command')
