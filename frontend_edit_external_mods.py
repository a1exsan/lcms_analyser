from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

import dash_ag_grid as dag


class modif_editor_layout():
    def __init__(self):
        self.mods_filename = 'external_mods.csv'
        main_tab = pd.read_csv(self.mods_filename, sep='\t')

        columnDefs = [
            {"field": "code", 'editable': True},
            {"field": "mass", 'editable': True},
            {"field": "ext_cf", 'editable': True},
            {"field": "formula+", 'editable': True},
            {"field": "formula-", 'editable': True},
            {"field": "in_base", 'editable': True}
        ]

        self.tab = dag.AgGrid(
            id="external_mods_table",
            columnDefs=columnDefs,
            rowData=main_tab.to_dict("records"),
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
                dbc.Button("New modification", outline=False,
                           id='adjust-new-modif-btn', color="info", className="me-1"),
                dbc.Button("Save table", outline=False,
                           id='save-modif-btn', color="success", className="me-1")
            ]),
            self.tab
        ])

