from emulator import MicromanagerSimulator
simulator=MicromanagerSimulator()
host='localhost'
port=4827
simulator.setHostPort(host,port)
simulator.connect()