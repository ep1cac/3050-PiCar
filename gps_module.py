import serial
from math import radians, sin, cos, sqrt, atan2

GPS_PORT = '/dev/serial0'
GPS_BAUD = 9600

ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)


def distance(lat1, lon1, lat2, lon2):
    R = 6371e3
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = radians(lat1), radians(lat2)
    dlambda = radians(lon2 - lon1)

    y = sin(dlambda) * cos(phi2)
    x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(dlambda)
    brng = atan2(y, x)

    return (brng * 180 / 3.1415926 + 360) % 360


def parse_lat_lon(nmea):
    parts = nmea.split(',')

    if parts[0] not in ["$GPRMC", "$GPGGA"]:
        return None, None

    try:
        raw_lat = parts[3]
        lat_dir = parts[4]
        raw_lon = parts[5]
        lon_dir = parts[6]

        if raw_lat == "" or raw_lon == "":
            return None, None

        lat_deg = float(raw_lat[:2])
        lat_min = float(raw_lat[2:])
        lat = lat_deg + lat_min / 60.0
        if lat_dir == "S":
            lat = -lat

        lon_deg = float(raw_lon[:3])
        lon_min = float(raw_lon[3:])
        lon = lon_deg + lon_min / 60.0
        if lon_dir == "W":
            lon = -lon

        return lat, lon

    except:
        return None, None


def get_current_location():
    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        lat, lon = parse_lat_lon(line)
        if lat is not None:
            return lat, lon

# can now use it like this in main script
#from gps_module import get_current_location, distance, bearing

#lat, lon = get_current_location()
#print(lat, lon)

#dist = distance(lat, lon, 38.64835, -90.30322)
#brng = bearing(lat, lon, 38.64835, -90.30322)

#print(dist, brng)
