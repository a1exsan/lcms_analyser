import dash_ag_grid as dag
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc

class oligo_lcms_adducts_tab():

    def __init__(self):

        adducts_tab = pd.DataFrame(
            {
                #'#': [],
                'adduct name': [],
                'mz rect': [],
                'mz': [],
                'area': [],
                'charge': [],
                'mass': [],
                'delta': [],
                'area%':[],
                'area total mz %': [],
                'norm area %': []
            }
        )

        columnDefs = [
            #{"field": "#"},
            {"field": "adduct name", 'editable': True},
            {"field": "mz rect", 'editable': False},
            {"field": "mz", 'editable': False},
            {"field": "area", 'editable': False},
            {"field": "charge", 'editable': True},
            {"field": "mass", 'editable': False},
            {"field": "delta", 'editable': False},
            {"field": "area%", 'editable': False},
            {"field": "area total mz %", 'editable': False},
            {"field": "norm area %", 'editable': False}
        ]

        self.adducts_tab = dag.AgGrid(
            id="lcms-adducts-tab",
            columnDefs=columnDefs,
            rowData=adducts_tab.to_dict("records"),
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
            dbc.Col([
                dbc.Button('Add tag', id='add-adduct-area-btn',
                           outline=False, color="primary", className="me-1"),
                dbc.Button('Del tag', id='del-adduct-area-btn',
                           outline=False, color="danger", className="me-1"),
                dbc.Button('Update mass', id='update-mass-tab-btn',
                           outline=False, color="info", className="me-1"),
                dbc.Input(id="normal-purity-input", placeholder="100", type="text", size=100),
                dbc.Button('Normalization', id='normalization-tab-btn',
                           outline=False, color="info", className="me-1"),
                dbc.Button('Save to csv', id='save-to-csv-tab-btn',
                           outline=False, color="success", className="me-1")
            ]),
            self.adducts_tab,
            html.H6("Purity%:", id='total-adduct-mz-area-text'),
            html.H6("0", id='total-adduct-mz-area')
        ])