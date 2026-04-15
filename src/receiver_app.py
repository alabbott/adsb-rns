#!/usr/bin/env python3
"""
receiver_app.py - Textual based TUI application for receiving ADS-B data over RNS
"""

import math
import time
from pathlib import Path

from rich.text import Text
from rich.style import Style

from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import *
from textual.containers import *
from textual.coordinate import Coordinate
from textual.worker import Worker, get_current_worker

import RNS

AIRCRAFT_ROWS = [
    ("CALLSIGN", "ALT", "SPD", "DIST", "BRG", "TRK", "V", "LAT", "LON"),
    ("a5f581", "3575", "0", "0", "270.0", "→", "41.965958", "-87.698492", "N483UA"),
    ("a06aba", "4900", "0", "0", "270.0", "→", "41.965818", "-87.605747", "N126HQ"),
    ("a73a1c", "3875", "0", "0", "269.27", "→", "41.98807", "-87.680799", "N565GJ"),
    ("a0fe7a", "4000", "0", "0", "270.0", "→", "42.002501", "-87.67703", "N163SY"),
    ("a4495d", "5225", "0", "0", "90.0", "→", "41.883957", "-87.564219", "N37542"),
    ("a53b2b", "4225", "0", "0", "270.0", "→", "42.002335", "-87.59493", "N436UA"),
    ("aa7e7b", "2975", "0", "0", "270.0", "→", "42.002701", "-87.732759", "N77537"),
    ("a6dc42", "2475", "0", "0", "270.73", "→", "41.965911", "-87.780251", "N541GJ"),
    ("a10d56", "2650", "0", "0", "270.36", "→", "41.98821", "-87.765049", "N167SY"),
    ("a0e751", "5200", "0", "0", "90.0", "→", "41.883682", "-87.539624", "N15751"),
    ("a12732", "5225", "0", "0", "270.36", "→", "41.987686", "-87.534943", "N17336"),
    ("a846d1", "7900", "0", "0", "90.18", "→", "41.884398", "-87.795389", "N632SY"),
    ("acd838", "4225", "0", "0", "267.38", "→", "42.002563", "-87.482445", "N927AN"),
    ("ad7f96", "9400", "0", "0", "76.18", "→", "41.729324", "-87.520149", "N969WN"),
    ("abb76d", "11150", "0", "0", "157.15", "→", "41.707221", "-87.767476", "N854NN"),
    ("abb440", "16525", "0", "0", "87.41", "→", "42.100983", "-87.429886", "N853UA"),
    ("aa0ec7", "35000", "0", "0", "81.33", "→", "41.691925", "-87.102481", "N747YX"),
]

SAMPLE_ROWS = [
    ("En", "Name", "Status", "Center", "Dist", "Last RX", "Bw/s", "Aircraft"),
    ("✓", "adsb-wi", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
    ("✓", "adsb-chi", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
    ("✓", "adsb-msp", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
    ("✗", "adsb-oh", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
    ("✗", "adsb-in", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
]

# class NetworkManager:
#     def __init__(self: NetworkManager, rns_config: str | None, id_file: str | None) -> None:
#         self.RNS = RNS.Reticulum(rns_config)
#         self.identity = None
#         self.identitypath = Path(__file__).resolve().parent.joinpath('receiver_identity')

#         if os.path.isfile(self.identitypath):
#             try:
#                 self.identity = RNS.Identity.from_file(self.identitypath)
#                 if self.identity != None:
#                     RNS.log("Loaded Primary Identity %s from %s" % (str(self.identity), self.identitypath))
#                 else:
#                     RNS.log("Could not load the Primary Identity from "+self.identitypath, RNS.LOG_ERROR)
#                     nomadnet.panic()
#             except Exception as e:
#                 RNS.log("Could not load the Primary Identity from "+self.identitypath, RNS.LOG_ERROR)
#                 RNS.log("The contained exception was: %s" % (str(e)), RNS.LOG_ERROR)
#                 nomadnet.panic()
#         else:
#             try:
#                 RNS.log("No Primary Identity file found, creating new...")
#                 self.identity = RNS.Identity()
#                 self.identity.to_file(self.identitypath)
#                 RNS.log("Created new Primary Identity %s" % (str(self.identity)))
#             except Exception as e:
#                 RNS.log("Could not create and save a new Primary Identity", RNS.LOG_ERROR)
#                 RNS.log("The contained exception was: %s" % (str(e)), RNS.LOG_ERROR)
#                 nomadnet.panic()



# Primary screen with radar grid and aircraft table
class RadarScreen(Screen):
    BINDINGS = [
        Binding("tab", "switch_mode('sources')", "Sources", show=True),
        Binding("s", "sort_by_selected_column", "Sort by Column", priority=True),

    ]

    current_sorts: set = set()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                RadarGrid(),
            ),
            AircraftTable(id='actable')
        )
        yield Footer()

    def on_mount(self) -> None:
        pass

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_sort_by_selected_column(self):
        table = self.query_one(DataTable)
        table.cursor_type = "column"
    
    def on_data_table_column_selected(self, message: DataTable.ColumnSelected):
        table = message.control

        table.sort(message.column_key, reverse=self.sort_reverse(str(message.column_key)))
        table.cursor_type = "row"

class RadarGrid(Static):

    def render(self):
        zoom = [25, 15, 10]
        w = self.size.width
        h = self.size.height - 3
        cy = h // 2
        cx = w // 2
        scale_x = zoom[0] / cx
        scale_y = zoom[0] / cy

        grid = [[' ' for _ in range(w)] for _ in range(h)]
        color = [['blue' for _ in range(w)] for _ in range(h)]

        rx = zoom[0] / scale_x
        ry = zoom[0] / scale_y

        seen = set()

        points = 360*3

        for i in range(points):
            angle = 2 * math.pi * i / points
            gx_ = int(round(cx + rx * math.cos(angle)))
            gy_ = int(round(cy - ry * math.sin(angle)))
            if (gx_, gy_) in seen:
                continue
            seen.add((gx_, gy_))
            if 0 <= gx_ < w and 0 <= gy_ < h and grid[gy_][gx_] == " ":
                grid[gy_][gx_] = "·"



        grid[cy][cx] = '@'
        color[cy][cx] = 'green'

        for x in range(1,5):
            grid[cy+x][cx] = '|'
            grid[cy-x][cx] = '|'
            grid[cy][cx+x] = '-'
            grid[cy][cx-x] = '-'

        txt = Text()
        for y in range(h):
            for x in range(w): 
                txt.append(grid[y][x], style=Style(color=color[y][x]))
            txt.append('\n')
        return txt

class AircraftTable(DataTable):
    
    BINDINGS = [
    ]

    def on_mount(self):
        self.cursor_type = "row"
        self.zebra_stripes = True
        for col in AIRCRAFT_ROWS[0]:
            self.add_column(col, key=col)
        self.add_rows(AIRCRAFT_ROWS[1:])
        self.cursor_type = "row"
        self.zebra_stripes = True

        def sort_reverse(self, sort_type: str):
            """Determine if `sort_type` is ascending or descending."""
            reverse = sort_type in self.current_sorts
            if reverse:
                self.current_sorts.remove(sort_type)
            else:
                self.current_sorts.add(sort_type)
            return reverse

        def action_sort_by_selected_column(self):
            table = self.query_one(DataTable)
            table.cursor_type = "column"

        def on_data_table_column_selected(self, message: DataTable.ColumnSelected):
            table = message.control

            table.sort(message.column_key, reverse=self.sort_reverse(str(message.column_key)))
            table.cursor_type = "row"

# Sources screen - shows connected senders, allows enable/disable, blocking, and reconnecting to a sender
class SourcesScreen(Screen):
    BINDINGS = [
                    Binding("tab", "toggle_mode", "Radar", show=True),
                ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield SourcesTable()
        yield Footer()

# Table for sources
class SourcesTable(DataTable):

    BINDINGS = [
        Binding("space", "toggle_source_enabled", "Enable / Disable Source")
    ]

    def on_mount(self):
        self.cursor_type = "row"
        self.zebra_stripes = True
        for col in SAMPLE_ROWS[0]:
            self.add_column(col, key=col)
        self.add_rows(SAMPLE_ROWS[1:])

    def action_toggle_source_enabled(self):
        (cursor_row, cursor_col) = self.cursor_coordinate
        colummn_index = self.get_column_index('En')
        cell_coordinate = Coordinate(cursor_row, colummn_index)

        if self.get_cell_at(Coordinate(cursor_row, colummn_index)) == "✓":
            self.update_cell_at(cell_coordinate, "✗")
        else:
            self.update_cell_at(cell_coordinate, "✓")

# Help Screen
class HelpScreen(Screen):
    BINDINGS = [
                    Binding("tab", "toggle_mode", "Radar", show=True),
                    Binding("h", "toggle_mode", "Exit Help", show=False),
                    Binding("escape", "toggle_mode", "Close Help", show=False),

                    
                ]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static('Help Screen')
        yield Footer()

# App class - high level settings and behavior
class TableApp(App):
    CSS_PATH = "placeholder.tcss"

    BINDINGS = [
        ("h", "switch_mode('help')", "Help"),
        ("q", "quit", "Quit"),
        Binding("tab", "toggle_mode", "Sources", show=True),
    ]

    MODES = {
        "radar": RadarScreen,
        "sources": SourcesScreen,
        "help": HelpScreen,
    }

    def on_mount(self) -> None:
        self.switch_mode("radar")

    def action_toggle_mode(self):
        if self.current_mode == "radar":
            self.switch_mode('sources')
        else:
            self.switch_mode('radar')

    # @work(exclusive=True, thread=True)
    # def refresh_loop(self):
    #     should_exit = False
    #     last_run = 0.0
    #     current_time = 0.0
    #     while not should_exit:
    #         current_time = time.time()
    #         if current_time > last_run + 5:
    #             last_run = current_time
    #             aircraft_list = []



    #         else:
    #             time.sleep(0.2)
    #             continue


# When executed
app = TableApp()
if __name__ == "__main__":
    app.run()