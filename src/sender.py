#!/usr/bin/env python3
"""
sender.py

NOT Claude Code - this slop is human produced
"""

import proto

import RNS
import sys
import argparse

APP_NAME = "adsb-rns"

latest_client_link = None

def server(config=None, name=None, lat=None, lon=None, range=None):

    reticulum = RNS.Reticulum(config)

    server_identity = RNS.Identity()

    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "request"
    )

    server_destination.set_link_established_callback(client_connected)

    server_destination.register_request_handler(
        "/random/text",
        response_generator=response_func,
        allow = RNS.Destination.ALLOW_ALL
    )

    announce_data = proto.encode_announce(lat, lon, range, name)

    announce_loop(server_destination, announce_data)


def announce_loop(destination, announce_data):
    RNS.log(f'Request server {RNS.prettyhexrep(destination.hash)} is running, waiting for connection')

    RNS.log('Announce example running, hit enter to announce - Ctrl + C to quit')

    while True:
        entered = input()
        destination.announce(app_data=announce_data)
        RNS.log(f'Sent announce from: {RNS.prettyhexrep(destination.hash)} {destination.name}')

def client_connected(link):
    global latest_client_link

    RNS.log('Client connected')

    link.set_link_closed_callback(client_disconnected)
    latest_client_link = link

def client_disconnected(link):
    RNS.log('Client disconnected')

def response_func(path, data, request_id, link_id, remote_identity, requested_at):
    return "This is a response"

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(
            description='ADS-B sender for Reticulum Network Stack'
        )

        parser.add_argument(
            '--config',
            action='store',
            default=None,
            help='name of sender for announces',
            type=str
        )

        parser.add_argument(
            '--lat',
            action='store',
            default=None,
            help='name of sender for announces',
            type=float
        )

        parser.add_argument(
            '--lon',
            action='store',
            default=None,
            help='name of sender for announces',
            type=float
        )

        parser.add_argument(
            '--range',
            action='store',
            default=None,
            help='name of sender for announces',
            type=int
        )

        parser.add_argument(
            '--name',
            action='store',
            default=None,
            help='name of sender for announces',
            type=str
        )

        args = parser.parse_args()

        config = args.config if args.config else None
        name = args.name if args.name else None
        lat = args.lat if args.lat else None
        lon = args.lon if args.lon else None
        range = args.range if args.range else None
    
        server(
            name=name,
            config=config,
            lat=lat,
            lon=lon,
            range=range
        )

    except KeyboardInterrupt:
        print('')
        sys.exit(0)