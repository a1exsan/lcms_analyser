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
                'Do synth': [True],
                'Done synth': [False],
                'Do cart': [True],
                'Done cart': [False],
                'Do hplc': [True],
                'Done hplc': [False],
                'Do paag': [True],
                'Done paag': [False],
                'Do click': [True],
                'Done click': [False],
                'Do sed': [True],
                'Done sed': [False],
                'Do subl': [True],
                'Done subl': [False],
                'DONE': [False],
                'Wasted': [False],
                'Send': [False],
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
            {"field": "Do synth", 'editable': False},
            {"field": "Done synth", 'editable': True},
            {"field": "Do cart", 'editable': False},
            {"field": "Done cart", 'editable': True},
            {"field": "Do hplc", 'editable': False},
            {"field": "Done hplc", 'editable': True},
            {"field": "Do paag", 'editable': False},
            {"field": "Done paag", 'editable': True},
            {"field": "Do sed", 'editable': False},
            {"field": "Done sed", 'editable': True},
            {"field": "Do click", 'editable': False},
            {"field": "Done click", 'editable': True},
            {"field": "Do subl", 'editable': False},
            {"field": "Done subl", 'editable': True},
            {"field": "DONE", 'editable': False},
            {"field": "Wasted", 'editable': True},
            {"field": "Send", 'editable': True},

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
            dbc.Button('Show actual', id='asm2000-inprogress-maps-db-btn',
                       outline=False, color="success", className="me-1"),
            dbc.Button('Load map', id='asm2000-load-from-maps-db-btn',
                       outline=False, color="primary", className="me-1"),
            dbc.Button('Save map', id='asm2000-save-from-maps-db-btn',
                       outline=False, color="success", className="me-1"),
            #dbc.Button('Sel done', id='asm2000-seldone-from-maps-db-btn',
            #           outline=False, color="primary", className="me-1"),
            dbc.Button('Put sequence', id='asm2000-put-sequence-from-maps-db-btn',
                       outline=False, color="success", className="me-1"),
            dbc.Button('Load LCMS data', id='asm2000-load-lcms-data-from-maps-db-btn',
                       outline=False, color="primary", className="me-1"),
            dcc.Input(placeholder='Enter volume, ml', id='asm2000-set-volume-input', type="text",
                      size='25', debounce=True),
            dbc.Button('Set volume', id='asm2000-set-volume-btn',
                       outline=False, color="info", className="me-1"),
            dbc.Button('Print passport', id='asm2000-print_pass-btn',
                       outline=False, color="success", className="me-1"),
        ])

        self.flags_buttons = dbc.Col([
            dbc.Button("Done lcms", outline=True, color="warning",
                       id='set-done-lcms-btn', className="me-1", size='lg'),
            dbc.Button("Done synth", outline=True, color="warning",
                       id='set-done-synth-btn', className="me-1", size='lg'),
            dbc.Button("Done cart", outline=True, color="warning",
                       id='set-done-cart-btn', className="me-1", size='lg'),
            dbc.Button("Done hplc", outline=True, color="warning",
                       id='set-done-hplc-btn', className="me-1", size='lg'),
            dbc.Button("Done paag", outline=True, color="warning",
                       id='set-done-paag-btn', className="me-1", size='lg'),
            dbc.Button("Done sed", outline=True, color="warning",
                       id='set-done-sed-btn', className="me-1", size='lg'),
            dbc.Button("Done click", outline=True, color="warning",
                       id='set-done-click-btn', className="me-1", size='lg'),
            dbc.Button("Done subl", outline=True, color="warning",
                       id='set-done-subl-btn', className="me-1", size='lg'),
        ])

        self.layout = html.Div([
            dbc.Row([
                self.map_tab_,
                self.buttons,
                dbc.Row([
                    dbc.Col(
                        dbc.Button("update ologomap status", outline=True, color="primary",
                                   id='asm2000-update-oligomap-status-btn', className="me-1", size='lg')
                    )
                ]),
                dbc.Row(self.flags_buttons),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Wasted selection", outline=False, color="danger",
                                   id='asm2000-wasted-status-btn', className="me-1", size='sm')
                    ])
                ]),
                self.map_db_tab
            ])
        ])
