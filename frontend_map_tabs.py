import dash_ag_grid as dag
import pandas as pd

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

class oligo_maps_tab():
    def __init__(self):
        map_db_tab = pd.DataFrame(
            {
                '#': [0],
                'Map name': [''],
                'Synth number': [''],
                'Date': ['']
            }
        )

        columnDefs = [
            {"field": "#"},
            {"field": "Map name"},
            {"field": "Synth number"},
            {"field": "Date"}
        ]

        self.map_db_tab = dag.AgGrid(
            id="asm2000-map-db-tab",
            columnDefs=columnDefs,
            rowData=map_db_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        map_tab = pd.DataFrame(
            {
                '#': [0],
                'Order id': [0],
                'Position': [''],
                'Name': [''],
                'Sequence': [''],
                'Purif type': [''],
                'Date': [''],
                'Synt number': [''],
                'Scale, OE': [''],
                'CPG, MG': [''],
                'asm Sequence': [''],
                'Status': ['in queue'],
                'Dens, oe/ml': [0.],
                'Vol, ml': [0.3],
                'Purity, %': [50.]
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Order id"},
            {"field": "Position", 'editable': True},
            {"field": "Name"},
            {"field": "Sequence", 'editable': True},
            {"field": "Purif type", 'editable': True},
            {"field": "Date"},
            {"field": "Synt number", 'editable': True},
            {"field": "Scale, OE", 'editable': True},
            {"field": "CPG, mg", 'editable': True},
            {"field": "asm Sequence", 'editable': True},
            {"field": "Status", 'editable': True},
            {"field": "Dens, oe/ml", 'editable': True},
            {"field": "Vol, ml", 'editable': True},
            {"field": "Purity, %", 'editable': True}
        ]

        self.map_tab_ = dag.AgGrid(
            id="asm2000-map-tab",
            columnDefs=columnDefs,
            rowData=map_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        self.layout = html.Div([
            dbc.Row([
                self.map_tab_,
                self.map_db_tab
            ])
        ])
