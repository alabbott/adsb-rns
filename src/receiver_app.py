from rich.text import Text

from textual.app import App, ComposeResult
from textual.events import Event, Mount
from textual.screen import Screen
from textual.widgets import *
from textual.containers import *
from textual.coordinate import Coordinate
from textual.content import Content


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

        def action_sort_by_average_time(self) -> None:
            """Sort DataTable by average of times (via a function) and
            passing of column data through positional arguments."""

            def sort_by_average_time_then_last_name(row_data):
                name, *scores = row_data
                return (sum(scores) / len(scores), name.split()[-1])

            table = self.query_one(DataTable)
            table.sort(
                "swimmer",
                "time 1",
                "time 2",
                key=sort_by_average_time_then_last_name,
                reverse=self.sort_reverse("time"),
            )

        def action_sort_by_last_name(self) -> None:
            """Sort DataTable by last name of swimmer (via a lambda)."""
            table = self.query_one(DataTable)
            table.sort(
                "swimmer",
                key=lambda swimmer: swimmer.split()[-1],
                reverse=self.sort_reverse("swimmer"),
            )

        def action_sort_by_country(self) -> None:
            """Sort DataTable by country which is a `Rich.Text` object."""
            table = self.query_one(DataTable)
            table.sort(
                "country",
                key=lambda country: country.plain,
                reverse=self.sort_reverse("country"),
            )

        def action_sort_by_columns(self) -> None:
            """Sort DataTable without a key."""
            table = self.query_one(DataTable)
            table.sort("swimmer", "lane", reverse=self.sort_reverse("columns"))

        def action_sort_by_selected_column(self):
            table = self.query_one(DataTable)
            table.cursor_type = "column"

        def on_data_table_column_selected(self, message: DataTable.ColumnSelected):
            table = message.control

            table.sort(message.column_key, reverse=self.sort_reverse(str(message.column_key)))
            table.cursor_type = "row"

class RadarGrid(Static):

    text = ''

    def compose(self):
        grid = [['.' * 20] for _ in range(20)]
        self.text = grid
        text = reactive(str(self.text))
        
        yield Static(str(text), expand=True)

    def get_size(self):
        return self.size
    
    def on_mount(self):
        grid = [['.' * 20] for _ in range(20)]
        self.text = grid


class RadarScreen(Screen):
    BINDINGS = [
        Binding("tab", "switch_mode('sources')", "Sources", show=True),
    ]

    current_sorts: set = set()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                RadarGrid('Radar Grid', id='radar'),
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