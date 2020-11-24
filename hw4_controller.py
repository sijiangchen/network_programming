import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('wrong')
        sys.exit(1)
    controlPort = sys.argv[1]
    baseStationFile = sys.argv[2]
    print(controlPort, baseStationFile)
