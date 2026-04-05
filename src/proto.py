#!/usr/bin/env python3
"""
proto.py - Shared functions for encode / decode of aircraft frames, announce data, and view requests

Originally written by Claude Code, adapted during review and rewrite,
functions are noted if taken verbatim from the original proto.py
"""

# imports
import requests
import struct
import math
import warnings

# constants
DEFAULT_AIRCRAFT_JSON_URL = 'http://localhost:8080/data/aircraft.json'

# Generic Chicago Location as default - Delilah's 41.93230° N, 87.65804° W
CENTER_LAT = 41.93
CENTER_LON = -87.66 # Negative for west
MAX_RANGE = 50
MAX_AC = 40
CALL_MAX = 7

# Default Grid Dimensions
GRID_WIDTH = 72
GRID_HEIGHT = 36

ARROWS = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]

# Frame format
MAGIC = b'\xad\xb5' # a nod to ADS-b
VERSION = 1 # resetting version to 1 in the migration to non-vibe coded app

# magic(2s) version(B) timestamp(I) count(B) clat(h) clon(h) = 12 bytes
# might remove clat / clon - should be handled by announces?
HEADER_FMT = '!2sBIBhh'
HEADER_SZ = struct.calcsize(HEADER_FMT) # 12

# icao(3s) lat(h) lon(h) alt(h) track(B) gs(B) vrate(b) flags(B)
# TO DO: add aircraft type
AIRCRAFT_FMT = '!3shhhBBbB'
AIRCRAFT_SZ = struct.calcsize(AIRCRAFT_FMT) #13

TRACK_NONE = 0xFF
GS_NONE = 0xFF
VRATE_NONE = -128

FL_ALT = 0x01
FL_TRACK = 0x02
FL_GS = 0x04
FL_VRATE = 0x08
FL_CALLSIGN = 0x10
FL_GS_OVF = 0x20
FL_VR_OVF = 0x40
FL_EMRG = 0x80

VIEW_REQUEST_MAGIC = b'\xad\xb6'
VIEW_REQ_FMT = '!2shhH' # magic(2s) clat_i(h) clon_i(h) range_nm(H)
VIEW_REQ_SIZE = struct.calcsize(VIEW_REQ_FMT) # 8

ANNOUNCE_FMT = '!hhH8s'
ANNOUNCE_SZ = struct.calcsize(ANNOUNCE_FMT)


# fetch aircraft
def fetch_aircraft(url=DEFAULT_AIRCRAFT_JSON_URL):
    """Fetch aircraft list from url and return ac or aircraft dictionary"""
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    try:
        ac_json = r.json()
        return ac_json.get('ac') or ac_json.get('aircraft') or []
    except requests.exceptions.JSONDecodeError:
        return {}
    
# distance helper    
def get_dist(lat, lon, center_lat=CENTER_LAT, center_lon=CENTER_LON):
    """Returns the approximate distance in nautical miles between two (lat, lon) points"""
    d_lat = center_lat - lat
    d_lon = (center_lon - lon) * math.cos(math.radians(center_lat))
    return math.sqrt(d_lat**2 + d_lon**2) * 60

# filter aircraft
def _filter_aircraft(aircraft_list, center_lat=CENTER_LAT, center_lon=CENTER_LON, range_nm=MAX_RANGE):
    """
    Filters the aircraft list to only currently flying, with position, and within range

    Function written by Claude Code - pulled from adsb-radar written using Claude Code
    """

    result = []
    for ac in aircraft_list or []:
        lat, lon = ac.get('lat'), ac.get('lon')
        if lat is None or lon is None:
            continue
        if ac.get('seen_pos', 0) > 60:
            continue
        if ac.get('alt_baro') == 'ground':
            continue
        dist = get_dist(lat, lon, center_lat, center_lon)
        if dist > range_nm:
            continue
        result.append((dist, ac))
    result.sort(key=lambda x: x[0])
    return [ac for _, ac in result[:MAX_AC]]

# encode frame
def encode_frame(aircraft_list, center_lat=CENTER_LAT, center_lon=CENTER_LON, range_nm=MAX_RANGE):
    frame = struct.pack()



    return frame

# decode frame
def decode_frame(data):
    pass

# encode announce
def encode_announce(lat, lon, range_nm, name='adsb-rns'):
    """Encode data for announce"""
    clat_i = max(-32768, min(32767, int(round(lat * 200))))
    clon_i = max(-32768, min(32767, int(round(lon * 200))))
    r = max(1, min(65535, int(range_nm)))
    name_b = name.encode('ascii', errors='replace')
    if len(name_b) > 8:
        warnings.warn(
            f'Sender name {name!r} exceeds 8-byte announce limit and will be '
            f'truncated to {name_b[:8].decode('ascii', errors='replace')!r}',
            stacklevel=2
        )
    name_b = name_b[:8].ljust(8, b'\x00')
    return struct.pack(ANNOUNCE_FMT, clat_i, clon_i, r, name_b)

# decode announce
def decode_announce():
    """Decode data for announce"""

    return None

# encode view request
def encode_view_request():
    pass

# decode view request
def decode_view_request():
    pass
