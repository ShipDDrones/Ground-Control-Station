import time
from concurrent.futures import ThreadPoolExecutor
from controller import Controller
from gui import ShipD


class Application:

    def __init__(self):
        self.app = ShipD()
        self.controller = Controller()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.setup()
        self.executor.submit(self.status)

    def setup(self):
        self.app.destinationButton.bind(on_press=self.destinationSet)
        self.app.droneStartButton.bind(on_press=self.droneSet)
        self.app.connectButton.bind(on_press=self.connectDrone)
        self.app.armButton.bind(on_press=self.armDrone)
        self.app.disarmButton.bind(on_press=self.disarmDrone)
        self.app.takeoffButton.bind(on_press=self.takeoffDrone)
        self.app.landButton.bind(on_press=self.landDrone)
        self.app.launchButton.bind(on_press=self.launchDrone)

    def setDuration(self):
        if self.controller.droneCoords != (None, None) and self.controller.destinationCoords != (None, None):
            self.app.arrivalTime.text = "Arrives in " + str(self.controller.getDuration()) + " minutes"
            self.app.batteryLeft.text = self.controller.getBattery()

    def droneSet(self, _):
        lat, lon = self.controller.getDroneAddress(self.app.droneStart.text)
        if (lat, lon) != (None, None):
            self.app.map.center_on(lat, lon)
            self.app.startLabel.text = "Takeoff - " + self.app.droneStart.text
            self.app.markerStart.lat = lat
            self.app.markerStart.lon = lon
            self.setDuration()
        else:
            self.app.startLabel.text = "Invalid takeoff position"

    def destinationSet(self, _):
        lat, lon = self.controller.getDestinationAddress(self.app.destination.text)
        if (lat, lon) != (None, None):
            self.controller.setWeather(lat, lon)

            self.app.endLabel.text = "Arrival - " + self.app.destination.text
            self.app.weather.text = self.controller.getWeather()
            self.app.wind.text = "Wind - " + self.controller.getWind()

            self.app.map.center_on(lat, lon)
            self.app.markerEnd.lat = lat
            self.app.markerEnd.lon = lon
            self.setDuration()
        else:
            self.app.endLabel.text = "Invalid arrival position"

    def connectDrone(self, _):
        self.executor.submit(self.controller.callConnect)

    def armDrone(self, _):
        self.controller.callArm()

    def disarmDrone(self, _):
        self.controller.callDisarm()

    def takeoffDrone(self, _):
        self.controller.callTakeoff()

    def landDrone(self, _):
        self.controller.callLand()

    def launchDrone(self, _):
        self.controller.callLaunchMission()

    def updateDroneOnMap(self):
        lat, lon = self.controller.drone.position
        self.app.map.center_on(lat, lon)
        self.app.markerStart.lat = lat
        self.app.markerStart.lon = lon

    def status(self):
        while self.app.running:
            self.app.errorLabel.text = self.controller.drone.output
            self.updateDroneOnMap()
            time.sleep(1)
        self.controller.loop.stop()
        self.executor.shutdown()

    def run(self):
        self.app.run()
