import sys

class Sensor:
    def __init__(self, controlAddress, controlPort, id, range, x, y):
        self.controlAddress = controlAddress
        self.controlPort = controlPort
        self.id = id
        self.range = range
        self.x = x
        self.y = y
    
    def __str__(self):
        return "Sensor::<addr: {}, port: {}, id: {}, range: {}, x: {}, y: {}>".format(
            self.controlAddress, self.controlPort, self.id, self.range, self.x, self.y
        )

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print('wrong')
        sys.exit(1)
    controlAddress = sys.argv[1]
    controlPort = sys.argv[2]
    id = sys.argv[3]
    range = sys.argv[4]
    x = sys.argv[5]
    y = sys.argv[6]
    sensor = Sensor(controlAddress, controlPort, id, range, x, y)
    print(sensor)

    # read stdin here for
    # MOVE <newX> <newY>
    # SENDDATA <destinationId>
    # WHERE <SensorId/BaseId>
    #     Note: Blocks until THERE is received
    # QUIT
    for line in sys.stdin:
        if line.startswith("MOVE "):
            print('move')
        elif line.startswith("SENDDATA "):
            print('senddata')
        elif line.startswith("WHERE "):
            print('where')
        elif line.startswith("QUIT"):
            print('shutting down.')
            sys.exit(1)
        else:
            print('unknown command')
