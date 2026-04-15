# adsb-rns

The goal of this project is to create sender and receiver applications that will allow ADS-B feeders to advertise and make available their data to receivers on any Reticulum network.

## To do's

 - sender functions (simpler, not using textual)
    - initialize RNS (both)
    - load or create identity (both)
    - create destination for sender (sender)
    - encode and send announce (sender)
    - wait for links from receivers (sender)
    - refresh aircraft information every 5s (sender)
    - encode frames for each receiver based on view request (sender)
    - send frames to each receiver (sender)
    - receive view request packets
    - update receiver list with view request info
- receiver functions
    - receive announces from senders
    - update sender list with announce data
    - maybe prepopulate known senders? Need to decide on path requests
    - for each sender, decide whether to connect or wait
    - connect to sender, send view request
    - handle packets from senders, update aircraft list
    - clean aircraft list - remove stale data, only show active aircraft
    - update aircraft list table
    - update radar grid - redraw foreground
    - pan and zoom functions
    - update grid and aircraft list when panning and zooming
    - send view requests to each sender after debounce

## Files Overview

### proto.py

This file contains the functions for encoding and decoding the aircraft frames, view request packets, and announce data.


### sender.py

Sender app.

Does the sender need concurrency? or can it manage everything in one loop?


### receiver_app.py

The TUI built using Textual, to be renamed and marged with receiver.py once all functions are added.

Textual supports both async and threaded concurrency. RNS is built to be threaded and not async so I will use threaded workers when working with RNS. Although, looking at the RNS code, it seems like it should create and manage its own threads. I should make sure that callback functions don't directly manipulate the UI, since I'm not sure in which thread the callback functions will be run.

The TUI app will need some concurrency and some initialization.

Initialize:
 - Create RNS instance and store globally
 - Load or create identity for receiver
 - Create announce handler for announces
 - Define callback function that will process announces
    - When an announce is received
    - Check if sender known, update if so
    - If new, add to list
    - Will list need to be thread locked?
 - Register announce handler
 - Should sender list be integrated with the announce handler as in the examples: No it should pass to a global list.
 - A separate function will evaluate the list and decide if a connection should be made and manage the connections.
 - sources list and link list should be thread locked? aircraft_list?

Concurrently:
 - Announces processed and added to sources list (thread = RNS, lock = sources_list)
 - Links managed, create or close connections, (Textual thread worker, lock = sources_list, link_list)
 - Frames received, process frame and update aircraft list (RNS?)
 - Redraw the radar grid and update the aircraft list (Textual event on_ function? Can RNS send a message?)

