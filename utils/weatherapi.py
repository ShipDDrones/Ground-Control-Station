import requests


class Weather:

    def __init__(self):
        self.baseUrl = "https://api.openweathermap.org/data/2.5/weather?"
        self.key = "582d8a44e66d23a96cbe0ad7689c8d36"
        self.data = None

    def requestInfo(self, lat, lon):
        url = self.baseUrl + "lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + self.key + "&units=metric"
        self.data = requests.get(url).json()

    def getWeather(self):
        if self.data["cod"] != "404":
            temp = self.data["main"]["temp"]
            desc = self.data["weather"][0]["description"]
            return desc, temp
        return None, None

    def getWind(self):
        if self.data["cod"] != "404":
            speed = self.data["wind"]["speed"]
            speed = speed * 3.6
            speed = f'{speed:g}'
            degrees = self.data["wind"]["deg"]
            return float(speed), degrees
        return None, None
