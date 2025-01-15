from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

class passport_tab_view_layout():

    def __init__(self):
        N = 200
        df = pd.DataFrame({'#': [i + 1 for i in range(N)],
                           'Name': ['' for i in range(N)],
                           'Sequence': ['' for i in range(N)],
                           'Amount,_oe': [0 for i in range(N)],
                           'Amount,_nmol': [0 for i in range(N)],
                           'Desolving': [1 for i in range(N)],
                           'Purification': ['' for i in range(N)],
                           'order_ID': ['' for i in range(N)],
                           'Mass,_Da': [0 for i in range(N)],
                           'Extinction': [0 for i in range(N)],
                           })

        self.tab = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                        editable=True, id='passport-view-tab')

        self.layout = html.Div([
            dbc.Container(
                dbc.Row([
            #dbc.Input(id="invoce-name-text", placeholder="", type="text"),
            self.tab
                ])
            )
        ])