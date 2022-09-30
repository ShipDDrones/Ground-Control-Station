from geopy.geocoders import Nominatim
import pyproj
import geopy.distance


def createCoord(address):
    loc = Nominatim(user_agent="GetLoc")
    s = str(address)
    getLoc = loc.geocode(s)
    if getLoc is not None:
        return getLoc.latitude, getLoc.longitude
    else:
        return None, None


def computeBattery(current, dist):
    usage = int(dist * 100 / 15)
    left = current - usage
    return left


def arrivalTime(speed, dist):
    hours = dist / speed
    minutes = hours * 60 + 0.5
    return round(minutes, 1)


def opposite(direction, wind):
    val = abs(direction - wind)
    if 150 < val < 210:
        return True
    return False


def convert(degrees):
    compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    compass_lookup = round(degrees / 45)
    return compass_brackets[compass_lookup]


def distance(coord1, coord2):
    return round(geopy.distance.geodesic(coord1, coord2).km, 2)


def compass(coord1, coord2):
    geodesic = pyproj.Geod(ellps='WGS84')
    forward, _, _ = geodesic.inv(coord1[1], coord1[0], coord2[1], coord2[0])
    return int(forward) + 360
