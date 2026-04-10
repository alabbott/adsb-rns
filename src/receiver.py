#!/usr/bin/env python3
"""
receiver.py

NOT Claude Code - this slop is human produced
"""

import sys
import argparse
import time
import RNS

import proto

APP_NAME = "adsb-rns"

announce_handler = None
server_link = None

def client(config=None, name=None, lat=None, lon=None, range=None):
    global announce_handler

    reticulum = RNS.Reticulum(config)

    identity = RNS.Identity()

    announce_handler = ExampleAnnounceHandler(aspect_filter="adsb-rns.request")

    RNS.Transport.register_announce_handler(announce_handler)

    while not announce_handler.has_destinations():
        RNS.log('Waiting for announces, press enter to check again')
        entered = input()


    # get the first known destination and unpack the hash, name tuple

    (server_hash, server_name) = announce_handler.known_destinations[0]

    server_identity = RNS.Identity.recall(server_hash)

    RNS.log('Linking with server')

    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "request"
    )

    link = RNS.Link(server_destination)

    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    client_loop()

def client_loop():
    global announce_handler
    global server_link

    while not server_link:
        time.sleep(0.1)

    should_quit = False

    while not should_quit:
        try:
            print('> ', end=' ')
            text = input()

            if text == 'quit' or text == 'q' or text == 'exit':
                should_quit = True
                server_link.teardown()

            else:
                server_link.request(
                    "/random/text",
                    data = None,
                    response_callback = got_response,
                    failed_callback = request_failed
                )
        except Exception as e:
            RNS.log('Error while sending request over the link: '+str(e))
            should_quit = True
            server_link.teardown()

def got_response(request_receipt):
    request_id = request_receipt.request_id
    response = request_receipt.response

    RNS.log('Got response for request ' + RNS.prettyhexrep(request_id)+': '+str(response))

def request_received(request_receipt):
    RNS.log('The request '+RNS.prettyhexrep(request_receipt.request_id)+' was received by the remote server')

def request_failed(request_receipt):
    RNS.log('The request '+RNS.prettyhexrep(request_receipt.request_id)+' failed')


def link_established(link):
    global server_link
    server_link = link
    RNS.log('Link established with the server')

def link_closed(link):
    if link.teardown_reason == RNS.Link.TIMEOUT:
        RNS.log('Link timeout')
    elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
        RNS.log('Server closed link')
    else:
        RNS.log('Link closed, exiting')

    time.sleep(1.5)
    sys.exit(0)



class ExampleAnnounceHandler:
    def __init__(self, aspect_filter=None):
        self.aspect_filter = aspect_filter
        self.known_destinations = []

    def received_announce(self, destination_hash, announced_identity, app_data):
        RNS.log('Announce rx: ' + RNS.prettyhexrep(destination_hash))

        if app_data:
            lat, lon, range, name = proto.decode_announce(app_data)

            RNS.log(f'name: {name} lat: {lat} lon: {lon} range: {range}')

        if not name:
            name = ''

        self.known_destinations.append((destination_hash, name))

        RNS.log(self.known_destinations[0])

    def has_destinations(self):
        return len(self.known_destinations) > 0


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
    
        client(
            name=name,
            config=config,
            lat=lat,
            lon=lon,
            range=range
        )

    except KeyboardInterrupt:
        print('')
        sys.exit(0)