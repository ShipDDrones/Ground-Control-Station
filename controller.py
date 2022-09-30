import asyncio
import threading

from drone import *
from utils.database import Database
from utils.weatherapi import Weather
from utils.map import *


class Controller:

    def __init__(self):
        self.drone = Drone()
        self.database = Database()
        self.loop = asyncio.get_event_loop()
        self.weather = Weather()
        self.destinationCoords = (None, None)
        self.droneCoords = (None, None)

    def checkIfAttached(self):
        return self.database.isAttached()

    def setWeather(self, lat, lon):
        self.weather.requestInfo(lat, lon)

    def getWind(self):
        speed, degrees = self.weather.getWind()
        if speed is None or degrees is None:
            return "Couldn't get wind"
        return str(speed) + " km/h " + convert(degrees)

    def getWeather(self):
        desc, temp = self.weather.getWeather()
        if desc is None or temp is None:
            return "Couldn't get weather"
        return str(desc) + " - " + str(temp) + " C"

    def getDistance(self):
        return distance(self.droneCoords, self.destinationCoords)

    def getDuration(self):
        bearing = compass(self.droneCoords, self.destinationCoords)
        dist = distance(self.droneCoords, self.destinationCoords)
        windSpeed, windDirection = self.weather.getWind()
        droneSpeed = 60
        if opposite(bearing, windDirection):
            droneSpeed -= windSpeed
        return arrivalTime(droneSpeed, dist)

    def getBattery(self):
        dist = distance(self.droneCoords, self.destinationCoords)
        left = computeBattery(self.drone.battery, dist)
        if left <= 0:
            return "Not enough battery"
        return str(left) + "% battery on arrival"

    def getDestinationAddress(self, address):
        s = str(address)
        lat, lon = createCoord(s)
        self.destinationCoords = (lat, lon)
        return self.destinationCoords

    def getDroneAddress(self, address):
        s = str(address)
        lat, lon = createCoord(s)
        self.droneCoords = (lat, lon)
        return self.droneCoords

    def callLaunchMission(self):
        if not self.drone.onMission:
            t = threading.Thread(target=self.loop.run_until_complete, args=(self.drone.launch(self.destinationCoords),))
            t.start()
        else:
            self.drone.output = "A mission is already en route"

    def callUpdateDroneLocation(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.get_start_position(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.get_start_position())

    def checkLocation(self):
        self.droneCoords = self.drone.position

    def callTakeoff(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.takeOff(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.takeOff())

    def callLand(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.land(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.land())

    def callConnect(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.connect(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.connect())

    def callArm(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.arm(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.arm())

    def callDisarm(self):
        if self.drone.onMission:
            asyncio.run_coroutine_threadsafe(self.drone.disarm(), self.loop)
        else:
            self.loop.run_until_complete(self.drone.disarm())
