from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

import dash_ag_grid as dag

class oligo_stock_database_layout():

    def __init__(self):

        main_tab = pd.DataFrame(
            {
                '#': [0],
                'Name': [''],
                "units": [''],
                'Unicode': [''],
                "Description": [''],
                'low limit': [0],
                'Exist on stock': [0],
                'E-L': [0],
                'SUB': [0],
                'last rate': [0],
                'Exist/rate': [1]
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name", 'editable': True},
            {"field": "units", 'editable': True},
            {"field": "Unicode", 'editable': True},
            {"field": "Description", 'editable': True},
            {"field": "low limit", 'editable': True},
            {"field": "Exist on stock"},
            {"field": "E-L"},
            {"field": "SUB", 'editable': True},
            {"field": "last rate", 'editable': False},
            {"field": "Exist/rate", 'editable': False},
        ]

        self.tab = dag.AgGrid(
            id="main-stock-tab-database",
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

        input_tab_df = pd.DataFrame(
            {
                '#': [0],
                'Name': [''],
                "Amount": [''],
                'Unicode': [''],
                "Date": [''],
                "Time": [''],
                'User': ['']
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name"},
            {"field": "Amount"},
            {"field": "Unicode"},
            {"field": "Date"},
            {"field": "Time"},
            {"field": "User"}
        ]

        self.input_tab = dag.AgGrid(
            id="input-stock-tab-database",
            columnDefs=columnDefs,
            rowData=input_tab_df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 300, "width": '100%'},
        )

        output_tab_df = pd.DataFrame(
            {
                '#': [0],
                'Name': [''],
                "Amount": [''],
                'Unicode': [''],
                "Date": [''],
                "Time": [''],
                'User': ['']
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name"},
            {"field": "Amount"},
            {"field": "Unicode"},
            {"field": "Date"},
            {"field": "Time"},
            {"field": "User"}
        ]

        self.output_tab = dag.AgGrid(
            id="output-stock-tab-database",
            columnDefs=columnDefs,
            rowData=output_tab_df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 300, "width": '100%'},
        )

        users_tab_df = pd.DataFrame(
            {
                '#': [0],
                'Name': [''],
                "Telegram id": [''],
                'Status': ['']
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name"},
            {"field": "Telegram id"},
            {"field": "Status"},
        ]

        self.users_tab = dag.AgGrid(
            id="user-stock-tab-database",
            columnDefs=columnDefs,
            rowData=users_tab_df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 300, "width": '100%'},
        )

        self.layout = html.Div([
            dbc.Col([
            dbc.Button("show data", outline=True, color="secondary",
                       id='show-stock-data-btn'),
            dbc.Button("update data", outline=True, color="secondary",
                           id='update-stock-data-btn'),
            dbc.Button("add row", outline=True, color="secondary",
                           id='add-row-stock-data-btn'),
            dbc.Button("delete row", outline=True, color="secondary",
                           id='delete-row-stock-data-btn'),
            dbc.Button("sub from stock", outline=True, color="secondary",
                           id='substruct_from-stock-data-btn'),
            dbc.Button("add to stock", outline=True, color="secondary",
                           id='add-to-stock-data-btn')
            ]),
            dbc.Row(self.tab),
            dbc.Row([
                dbc.Col([
                    html.H6("INPUT", id='input-tab-input'),
                    self.input_tab
                ]),
                dbc.Col([
                    html.H6("OUTPUT", id='output-tab-input'),
                    self.output_tab]
                        ),
                #dbc.Col([
                #    self.users_tab,
                #    dbc.Col([
                #        dbc.Button("Send link", outline=True, color="secondary",
                #                   id='send-link-to-user-btn'),
                #    ])
                #]),

            ]
            )
        ])