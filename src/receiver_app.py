from rich.text import Text

from textual.app import App, ComposeResult
from textual.events import Event, Mount
from textual.screen import Screen
from textual.widgets import *
from textual.containers import *
from textual.coordinate import Coordinate
from textual.content import Content
from textual.reactive import reactive
import math
from rich.style import Style


AIRCRAFT_ROWS = [
    ("lane", "swimmer", "country", "time 1", "time 2"),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 50.39, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 50.39, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 50.39, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 50.39, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 50.39, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),   
]

SAMPLE_ROWS = [
        ("En", "Name", "Status", "Center", "Dist", "Last RX", "Bw/s", "Aircraft"),
        ("✓", "adsb-wi", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
        ("✓", "adsb-chi", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
        ("✓", "adsb-msp", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
        ("✗", "adsb-oh", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
        ("✗", "adsb-in", "connected", "43.67, -87.90", "3nm", "2s", "43b/s", "21"),
        
    ]


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

        
class SourcesScreen(Screen):
    BINDINGS = [
                    Binding("tab", "toggle_mode", "Radar", show=True),
                ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield SourcesTable()
        yield Footer()





class HelpScreen(Screen):
    BINDINGS = [
                    Binding("tab", "toggle_mode", "Radar", show=True),
                    Binding("escape", "toggle_mode", "Close Help", show=False),
                    
                ]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static('Help Screen')
        yield Footer()






class AircraftTable(DataTable):
    BINDINGS = [
        ("s", "sort_by_selected_column", "Sort by Column"),
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

class RadarGrid(Static):

    def render(self):
        zoom = [25, 15, 10]
        w = self.size.width
        h = self.size.height - 1
        cy = h // 2
        cx = w // 2
        scale_x = zoom[0] / cx
        scale_y = zoom[0] / cy

        grid = [[' ' for _ in range(w)] for _ in range(h)]
        color = [['blue' for _ in range(w)] for _ in range(h)]

        rx = zoom[0] / scale_x
        ry = zoom[0] / scale_y

        seen = set()

        points = 360

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


class RadarScreen(Screen):
    BINDINGS = [
        Binding("tab", "switch_mode('sources')", "Sources", show=True),
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

app = TableApp()
if __name__ == "__main__":
    app.run()