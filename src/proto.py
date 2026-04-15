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
import time

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
VERSION = 4 # bumping version to 4 in the migration to non-vibe coded app

# magic(2s) version(B) timestamp(I) count(B) clat(h) clon(h) = 12 bytes
# might remove clat / clon - should be handled by announces?
HEADER_FORMAT = '!2sBIBhh'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) # 12

# icao(3s) lat(h) lon(h) type(4s) alt(h) track(B) gs(B) vrate(b) flags(B)
# TO DO: add aircraft type
AIRCRAFT_FORMAT = '!3shhhBBbB'
AIRCRAFT_SIZE = struct.calcsize(AIRCRAFT_FORMAT) #13

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
VIEW_REQ_FORMAT = '!2shhH' # magic(2s) clat_i(h) clon_i(h) range_nm(H)
VIEW_REQ_SIZE = struct.calcsize(VIEW_REQ_FORMAT) # 8

ANNOUNCE_FORMAT = '!hhH8s'
ANNOUNCE_SIZE = struct.calcsize(ANNOUNCE_FORMAT)

SHRT_MAX = 32767
SHRT_MIN = -32767

USHRT_MAX = 65535
USHRT_MIN = 0

SCHAR_MAX = 127
SCHAR_MIN = -127

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
    """Returns the approximate distance in nautical miles between two (lat, lon) points - Written by Claude"""
    d_lat = center_lat - lat
    d_lon = (center_lon - lon) * math.cos(math.radians(center_lat))
    return math.sqrt(d_lat**2 + d_lon**2) * 60

def bearing_to(lat, lon, center_lat=CENTER_LAT, center_lon=CENTER_LON):
    """Return bearing from center lat/lon to aircraft lat/lon - Written by Claude"""
    cos_lat = math.cos(math.radians(center_lat))
    dlat = lat - center_lat
    dlon = (lon - center_lon) * cos_lat
    return math.degrees(math.atan2(dlon, dlat)) % 360

def get_arrow(track):
    """Returns the appropriate arrow for a given aircraft heading - Written by Claude"""
    if track is None:
        return '?'
    return ARROWS[round(track / 45) % 8]

def vrate_symbol(vr):
    """Returns the appropriate arrow for a given vertical rate - Written by Claude"""
    if vr is None or abs(vr) < 200:
        return '→'
    return '↑' if vr > 0 else '↓'

def encode_degs(deg):
    """Encodes degrees as integer - Returns deg_i"""
    return max(SHRT_MIN, min(SHRT_MAX, int(round(deg * 200))))

# filter aircraft
def filter_aircraft(aircraft_list, center_lat=CENTER_LAT, center_lon=CENTER_LON, range_nm=MAX_RANGE):
    """
    Filters the aircraft list to only currently flying, with position, and within range - Returns [aircraft]

    Function written by Claude Code
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
    """
    Encodes a frame containing the aircraft for a given view - Returns bytes
    
    Written largely by Claude Code, modified for readibility and added aircraft type to frame
    """
    filtered_list = filter_aircraft(aircraft_list, center_lat, center_lon, range_nm)
    timestamp = int(time.time())
    clat_i = encode_degs(center_lat)
    clon_i = encode_degs(center_lon)
    # magic(2s) version(B) timestamp(I) count(B) clat(h) clon(h) = 12 bytes
    # HEADER_FORMAT = '!2sBIBhh'
    parts = [struct.pack(HEADER_FORMAT, MAGIC, VERSION, timestamp, len(filtered_list), clat_i, clon_i)]

    # icao(3s) lat(h) lon(h) type(4s) alt(h) track(B) gs(B) vrate(b) flags(B)
    # AIRCRAFT_FORMAT = '!3shhhBBbB'

    for ac in filtered_list:
        lat = ac['lat']
        lon = ac['lon']
        alt = ac.get('alt_baro')
        trk = ac.get('track')
        gs = ac.get('gs')
        vr = ac.get('baro_rate') if ac.get('baro_rate') is not None else ac.get('geom_rate')
        call = (ac.get('flight') or '').strip()[:CALL_MAX]
        icao_hex = ac.get('hex', '000000').lower().zfill(6)

        flags = 0

        try:
            icao_bytes = bytes.fromhex(icao_hex[:6])
        except ValueError:
            icao_bytes = b'\x00\x00\x00'

        lat_i = encode_degs(lat)
        lon_i = encode_degs(lon)

        if isinstance(alt, (int, float)):
            alt_i = max(-32768, min(32768, round(alt / 10)))    
            flags |= FL_ALT
        else:
            alt_i = 0

        if trk is not None:
            trk_i = int(trk) // 2
            flags |= FL_TRACK
        else:
            gs_i = GS_NONE
        
        if gs is not None:
            gs_raw = int(gs)
            if gs_raw >= 510:
                flags |= FL_GS_OVF
            gs_i = min(254, gs_raw // 2)
            flags |= FL_GS
        else:
            gs_i = GS_NONE
        
        if vr is not None:
            vr_clamped = max(SCHAR_MIN, min(SCHAR_MAX, int(vr) // 64))
            if abs(int(vr)) > 8128:
                flags |= FL_VR_OVF
            vr_i = vr_clamped
            flags |= FL_VRATE
        else:
            vr_i = VRATE_NONE

        sqk = str(ac.get('squawk') or '')
        if sqk in ('7700', '7500', '7600'):
            flags |= FL_EMRG

        if call:
            flags |= FL_CALLSIGN

        parts.append(struct.pack(AIRCRAFT_FORMAT, icao_bytes, lat_i, lon_i, alt_i, gs_i, vr_i, flags))
        if call:
            call_bytes = call.encode('ascii', errors='replace')
            parts.append(struct.pack('B', len(call_bytes)) + call_bytes)

        return b''.join(parts)

# decode frame
def decode_frame(data):
    """
    Decodes frame into aircraft and sender data - Returns {'timestamp', 'aircraft', 'sender_center'}
    
    Written by Claude Code, modified to add aircraft type
    """
    if len(data) < HEADER_SIZE:
        raise ValueError('Frame too short')
    
    magic, version, timestamp, count, clat_i, clon_i = struct.unpack_from(HEADER_FORMAT, data, 0)
    if magic != MAGIC:
        raise ValueError(f'Bad magic: {magic!r}')
    
    if version == 4:
        if len(data) < HEADER_SIZE:
            raise ValueError(f'v{version} frame too short for header')
        sender_center = (clat_i / 200.0, clon_i / 200.0)
        offset = HEADER_SIZE
    elif version in (1, 2, 3):
        raise ValueError(f'Unsupported version: {version} Please upgrade to non-vibe coded version of this program')
    else:
        raise ValueError(f'Unsupported version: {version}')
    
    aircraft = []

    for _ in range(count):
        if offset + AIRCRAFT_SIZE > len(data):
            break
        icao_bytes, lat_i, lon_i, alt_i, trk_i, gs_i, vr_i, flags = struct.unpack_from(
            AIRCRAFT_FORMAT, data, offset
        )

        icao = icao_bytes.hex().upper()
        lat = lat_i / 200.0
        lon = lon_i / 200.0
        if flags & FL_ALT:
            alt = (alt_i * 10)
        else:
            alt = None
        trk = trk_i * 2 if flags & FL_TRACK else None
        gs = gs_i *2 if flags & FL_GS else None
        vr = vr_i * 64 if flags & FL_VRATE else None

        gs_ovf = bool(flags & FL_GS_OVF)
        vr_ovf = bool(flags & FL_VR_OVF)
        emrg = bool(flags & FL_EMRG)

        call = ''
        if flags & FL_CALLSIGN:
            if offset < len(data):
                call_len = data[offset]
                offset += 1
                call_len = min(call_len, len(data) - offset)
                call = data[offset : offset + call_len].decode('ascii', errors='replace')
                offset += call_len

        s_lat, s_lon = sender_center
        dist = get_dist(lat, lon, s_lat, s_lon)
        brg = bearing_to(lat, lon, s_lat, s_lon)

        aircraft.append(
            {
                'icao': icao,
                'hex': icao.lower(),
                'lat': lat,
                'lon': lon,
                'alt_baro': alt,
                'track': trk,
                'gs': gs,
                'baro_rate': vr,
                'flight': call,
                'sender_dist': round(dist, 1),
                'sender_brg': round(brg),
                'flags': flags,
                'gs_ovf': gs_ovf,
                'vr_ovf': vr_ovf,
                'emrg': emrg,
            }
        )
    
    return {'timestamp': timestamp, 'aircraft': aircraft, 'sender_center': sender_center}
        

# encode announce
def encode_announce(lat, lon, range_nm, name='adsb-rns'):
    """Encode data for announce - Returns bytes - Written by Claude"""
    clat_i = encode_degs(lat)
    clon_i = encode_degs(lon)
    r = max(1, min(USHRT_MAX, int(range_nm)))
    name_b = name.encode('ascii', errors='replace')
    if len(name_b) > 8:
        warnings.warn(
            f'Sender name {name!r} exceeds 8-byte announce limit and will be '
            f'truncated to {name_b[:8].decode('ascii', errors='replace')!r}',
            stacklevel=2
        )
    name_b = name_b[:8].ljust(8, b'\x00')
    return struct.pack(ANNOUNCE_FORMAT, clat_i, clon_i, r, name_b)

# decode announce
def decode_announce(app_data):
    """Decode data for announce - Returns (lat, lon, range, name) - Written by Claude"""
    if not app_data or len(app_data) < ANNOUNCE_SIZE:
        return None
    try:
        clat_i, clon_i, r, name_b = struct.unpack_from(ANNOUNCE_FORMAT, app_data, 0)
    except struct.error:
        return []
    lat_f = clat_i / 200.0
    lon_f = clon_i / 200.0
    if not (-90 <= lat_f <= 90) or not (-180.0 <= lon_f <= 180.0):
        return None
    return (lat_f, lon_f, int(r), name_b.rstrip(b'\x00').decode('ascii', errors='replace'))
    
# encode view request
def encode_view_request(center_lat, center_lon, range_nm):
    """Encode a view request packet - Rerturns bytes - Written by Claude"""
    clat_i = encode_degs(center_lat)
    clon_i = encode_degs(center_lon)
    r = max(1, min(USHRT_MAX, int(range_nm)))
    return struct.pack(VIEW_REQ_FORMAT, VIEW_REQUEST_MAGIC, clat_i, clon_i, r)

# decode view request
def decode_view_request(data):
    """Decode a view request packet - Returns (center lat, center lon, range) - Written by Claude"""
    if len(data) < VIEW_REQ_SIZE:
        return None
    try:
        magic, clat_i, clon_i, range_nm = struct.unpack_from(VIEW_REQ_FORMAT, data, 0)
    except struct.error:
        return None
    if magic != VIEW_REQUEST_MAGIC:
        return None
    return (clat_i / 200.0, clon_i / 200.0, int(range_nm))