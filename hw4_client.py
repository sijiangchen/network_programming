# A client is a base station

class Client:
    def __init__(self, baseId, x, y, links):
        self.baseId = baseId
        self.x = x
        self.y = y
        self.links = links
    
    @staticmethod
    def create(line):
        line = line.split(' ')
        return Client(line[0], line[1], line[2], line[4:])

    @staticmethod
    def createAll(path):
        l = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                l.append(Client.create(line))
        return l


    def __str__(self):
        return "Client::<baseId: {}, x: {}, y: {}, links: [{}]>".format(self.baseId, self.x, self.y, ", ".join(self.links))

if __name__ == "__main__":
    baseStations = Client.createAll("base_stations.txt")
    for baseStation in baseStations:
        print(baseStation)
