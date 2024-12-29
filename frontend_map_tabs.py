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
            id="asm2000-map-list-tab",
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
                #'CPG, MG': [''],
                #'asm Sequence': [''],
                #'Status': ['in queue'],
                'Dens, oe/ml': [0.],
                'Vol, ml': [0.3],
                'Purity, %': [50.],
                'Do LCMS': [True],
                'Done LCMS': [False],
                'DONE': [False],
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Order id", 'editable': False},
            {"field": "Position", 'editable': False},
            {"field": "Name", 'editable': False},
            {"field": "Sequence", 'editable': False},
            {"field": "Purif type", 'editable': False},
            {"field": "Date"},
            {"field": "Synt number", 'editable': False},
            {"field": "Scale, OE", 'editable': False},
            #{"field": "CPG, mg", 'editable': False},
            #{"field": "asm Sequence", 'editable': False},
            #{"field": "Status", 'editable': False},
            {"field": "Dens, oe/ml", 'editable': True},
            {"field": "Vol, ml", 'editable': True},
            {"field": "Purity, %", 'editable': True},

            {"field": "Do LCMS", 'editable': False},
            {"field": "Done LCMS", 'editable': True},
            {"field": "DONE", 'editable': True}
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

        self.buttons = dbc.Col([
            dbc.Button('Show content', id='asm2000-show-maps-db-btn',
                       outline=False, color="primary", className="me-1"),
            dbc.Button('Show in PROGRESS', id='asm2000-inprogress-maps-db-btn',
                       outline=False, color="success", className="me-1"),
            dbc.Button('Load map', id='asm2000-load-from-maps-db-btn',
                       outline=False, color="primary", className="me-1"),
            dbc.Button('Save map', id='asm2000-save-from-maps-db-btn',
                       outline=False, color="success", className="me-1"),
            dbc.Button('Sel done', id='asm2000-seldone-from-maps-db-btn',
                       outline=False, color="primary", className="me-1"),
        ])

        self.layout = html.Div([
            dbc.Row([
                self.map_tab_,
                self.buttons,
                self.map_db_tab
            ])
        ])
