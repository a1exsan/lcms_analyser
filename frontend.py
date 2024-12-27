from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

import frontend_map_tabs


class oligo_lcms_layout():

    def __init__(self, graph_mz, graph_mass, db_content):
        self.upload_area = html.Div(
                        dcc.Upload(
                                    id='upload-data',
                                    children=html.Div(['Drag and Drop or ', dbc.Button('Select File',
                                                                                       color="primary",
                                                                                       className="me-1")]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'},
                                    # Allow multiple files to be uploaded
                                    multiple=False),
                            )

        self.rt_interval = dbc.Toast(
                [
                            html.H6("rt min: ; rt max:", id='show-retention-time-interval'),
                            dcc.RangeSlider(0, 2000, 50, value=[100, 1500],
                                 id='retention-time-interval',
                                 marks={
                                     0: {'label': '0 sec'},
                                     500: {'label': '500 sec'},
                                     1000: {'label': '1000 sec'},
                                     1500: {'label': '1500 sec'},
                                     2000: {'label': '2000 sec'}
                                 }),
                            ],
                header="RT interval, sec",
)

        self.bkg_treshold = dbc.Toast(
                [
                            html.H6("bkg: ", id='show-background-treshold'),
                            dcc.Slider(100, 6000, 200, value=500,
                                 id='background-treshold',
                                 marks={
                                     0: {'label': '0'},
                                     500: {'label': '500'},
                                     1500: {'label': '1500'},
                                     3000: {'label': '3000'},
                                     6000: {'label': '6000'}
                                 }),
                            ],
                header="Background treshold",
)

        self.nigh_treshold = dbc.Toast(
                [
                            html.H6("selected: ", id='show-neighbor-treshold'),
                            dcc.Slider(5, 100, 5, value=50,
                                 id='neighbor-treshold',
                                 marks={
                                     10: {'label': '10%'},
                                     30: {'label': '30%'},
                                     50: {'label': '50%'},
                                     100: {'label': 'All'}
                                 }),
                            ],
                header="Neighbor treshold",
)

        self.low_intens_treshold = dbc.Toast(
                [
                            html.H6("selected: ", id='show-low-intens-treshold'),
                            dcc.Slider(0, 10000, 200, value=1000,
                                 id='low-intens-treshold',
                                 marks={
                                     1000: {'label': '10%'},
                                     3000: {'label': '30%'},
                                     5000: {'label': '50%'},
                                     10000: {'label': 'max'}
                                 }),
                            ],
                header="low intensity treshold",
)

        self.polish_repeats = dbc.Toast(
                [
                            html.H6("selected: ", id='show-bkg-polish-repeats'),
                            dcc.Slider(0, 10, 1, value=1,
                                 id='bkg-polish-repeats',
                                 marks={
                                     1: {'label': '10%'},
                                     3: {'label': '30%'},
                                     5: {'label': '50%'},
                                     10: {'label': 'max'}
                                 }),
                            ],
                header="background polish repeats",
)


        self.processing_buttons = dbc.Toast([
                                dbc.ButtonGroup(
                        [
                                    dbc.Button("mzdata polish", id='polish-button'),
                                    dbc.Button("show init", id='show-init-mzdata-button'),
                                    dbc.Button("deconv fast", id='deconv-fast-button'),
                                    dbc.Button("deconv data", id='deconvolution-button')
                                ],
                                size="me",
                                className="me-1",
                                ),
                            html.Br(),
                            html.Br(),
                            dcc.Checklist(
                                    [
                                            {'label': 'Negative mode', 'value': 'neg'}
                                            ],
                            value=['neg'],
                            id='control-deconv-mode'
                            )
        ],
                                header="data processing",
)

        self.selection_processing_buttons = dbc.Toast([
                                dbc.Input(id="selected-tag", placeholder="Tag Name", type="text"),
                                html.Br(),
                                dbc.Textarea(id="sequence-tag", className='mb-3', placeholder="Sequence",
                                style={"width": "100%", "height": "100 px"}),
                                html.Br(),
                                dbc.ButtonGroup(
                        [
                                    dbc.Button("add tag", id='add-tag-button'),
                                    dbc.Button("del points", id='del-points-button'),
                                    dbc.Button("del tag", id='del-tag-button'),
                                    dbc.Button("show tags", id='show-tags-button')
                                ],
                                size="lg",
                                className="me-1",
                                ),
                                html.Br(),
                                html.Br(),
                                dcc.Checklist(
                        [
                                    {'label': 'Hide text from graph', 'value': 'hide'}
                                ],
                                value=[],
                                id='control-text-view'
                                ),
                                html.Br(),
                                dcc.Checklist(
                        [
                                {'label': 'ellipse in red', 'value': 'red'}
                                ],
                                value=[],
                                id='control-ellipse-color'
                                )
                                ],
                                header="selection processing",
)

        self.initial_sequence_fragmentation_buttons = dbc.Toast([
                                dbc.Textarea(id="init-find-sequence", className='mb-3', placeholder="Sequence",
                                style={"width": "100%", "height": "100 px"}),
                                html.Br(),
                                dbc.ButtonGroup(
                        [
                                    dbc.Button("generate", id='generate-frag-button'),
                                    dbc.Button("find", id='find-frag-button'),
                                    dbc.Button("clear", id='clear-frag-button')
                                ],
                                size="lg",
                                className="me-1",
                                )],
                                header="find fragments",
)

        self.oligo_mass_calculation_box = dbc.Container([
            dbc.Row([
            dbc.Col(dbc.Textarea(id="oligo-sequence", className='mb-3', placeholder="Sequence",
                                 style={"width": "100%", "height": "100 px"})),
            dbc.Col(dbc.Button("Get prop", id='calculate-oligo-prop-button'), width=1)
            ]),
            dbc.Row(
                dbc.Col(html.Div('Mol Mass, Da:', id='oligo-mass'))
            ),
            dbc.Row(
                html.Br()
            ),
            dbc.Row(dbc.Col(
                dbc.Col(html.Div('Extinction:', id='oligo-extinction'))
            ))
        ])

        self.progress = dbc.Progress(label="0%", value=5, id='process-progress')

        self.params_board = dbc.Container(
    html.Div([
    dbc.Row(dbc.Col(self.progress)),
    html.Br(),
    dbc.Row([
       dbc.Col(self.rt_interval),
       dbc.Col(self.polish_repeats)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(self.bkg_treshold),
        dbc.Col(self.processing_buttons)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(self.nigh_treshold),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(self.low_intens_treshold),
    ])
])
)

        df = pd.DataFrame(
            {
                'tag name': [],
                'intensed mass': [],
                'area%': [],
                'seq': [],
            })
        self.tagging_tab = dash_table.DataTable(    df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                                id='tagging_table',
                                                style_cell={
                                                    'overflow': 'hidden',
                                                    'textOverflow': 'ellipsis',
                                                    'maxWidth': 0
                                                }
                                                )

        df = pd.DataFrame(
            {
                'name': [],
                'mass': [],
                'seq': []
            })
        self.fragments_tab = dash_table.DataTable(    df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                                id='fragment_table',
                                                style_cell={
                                                    'overflow': 'hidden',
                                                    'textOverflow': 'ellipsis',
                                                    'maxWidth': 0
                                                }
                                                )

        df = pd.DataFrame(
            {
                'tag name': [],
                'local area%': [],
                'global area%': [],
                'rect area%': [],
                'sequence': [],
            })
        self.tagging_mz_tab = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                                id='tagging_mz_table',
                                                style_cell={
                                                    'overflow': 'hidden',
                                                    'textOverflow': 'ellipsis',
                                                    'maxWidth': 0
                                                }
                                                )

        df = pd.DataFrame(
            {
                'mass': [],
                'mz': [],
                'charge': []
            })
        self.mz_tab = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                                id='mz_identify_table',
                                                style_cell={
                                                    'overflow': 'hidden',
                                                    'textOverflow': 'ellipsis',
                                                    'maxWidth': 0
                                                }
                                                )

        self.db_content_tab = dash_table.DataTable(db_content.to_dict('records'), [{"name": i, "id": i} for i in db_content.columns],
                                                id='db-content-table',
                                                style_cell={
                                                    'overflow': 'hidden',
                                                    'textOverflow': 'ellipsis',
                                                    'maxWidth': 0,
                                                    'minWidth': '100%'
                                                }
                                                )

        self.tagging_param_board = dbc.Container(
            html.Div(
                [
                    dbc.Row(dbc.Col(html.Br())),
                    dbc.Row([dbc.Col(self.selection_processing_buttons, width='auto'),
                            dbc.Col(self.oligo_mass_calculation_box, width='auto')]),
                    dbc.Row(dbc.Col(html.Br())),
                    dbc.Row(dbc.Col(self.tagging_tab))
                ]
            )
        )

        self.finding_fragments_board = dbc.Container(
            html.Div(
                [
                    dbc.Row(dbc.Col(html.Br())),
                    dbc.Row([dbc.Col(self.initial_sequence_fragmentation_buttons, width='auto'),
                             dbc.Col(
                                 dcc.Checklist(
                                     [
                                         {'label': 'Prefix', 'value': 'prefix'},
                                         {'label': 'Suffix', 'value': 'suffix'},
                                         {'label': 'Deletion', 'value': 'deletion'},
                                         {'label': 'Multimer', 'value': 'multimer'}

                                     ],
                                     value=['prefix'],
                                     id='fragment-type-list'
                                 )
                             )]),
                    dbc.Row(dbc.Col(html.Br())),
                    dbc.Row(dbc.Col(self.fragments_tab))
                ]
            )
        )

        self.database_buttons = dbc.Container(
            html.Div(
                [
                    dbc.Row(dbc.Col(html.Br())),
                    dbc.Row([dbc.Col(dbc.Button("load data", id='load-db-data-button')),
                            dbc.Col(dbc.Button("Update", id='update-db-data-button'))]),
                ]
            )
        )

        self.db_content_board = dbc.Container(
            html.Div([
                dbc.Row(dbc.Col(html.Br())),
                dbc.Row(
                    dbc.Col(self.db_content_tab)#, width='auto')
                ),
                dbc.Row(
                    dbc.Col(self.database_buttons)
                )
            ])
        )

        self.mz_interval_ident = dbc.Toast(
            [
                html.H6("width of area", id='show-mz-interval'),
                dcc.Slider(1, 10, 1, value=2,
                           id='mz-tag-window'),
                html.H6("mz window"),
                dcc.Slider(1, 10, 1, value=5,
                           id='mz-find-window'),
            ],
            header="mz window",
        style={"width": 'auto'})

        self.mz_identifying_buttons = dbc.Toast([
            html.Br(),
            dbc.Textarea(id="oligo-mz-tag-name", className='mb-3', placeholder="Tag Name",
                         style={"width": "100%", "height": "100 px"}),
            html.Br(),
            dbc.Textarea(id="oligo-seq-mz", className='mb-3', placeholder="Sequence",
                         style={"width": "100%", "height": "100 px"}),
            dbc.ButtonGroup(
                [
                    dbc.Button("mz tab", id='calculate-mz-button'),
                    dbc.Button("add tag", id='add-tag-mz-button'),
                    dbc.Button("add mz area", id='add-area-mz-button')
                ],
                size="lg",
                className="me-1",
                style={'width': '300px'}
            ),
            html.Br(),
            html.Br(),
            dbc.Col(self.mz_interval_ident, width='auto')
        ],
            header="Oligo mz Identifying",
        )

        self.mz_deconv_params = dbc.Toast(
            [
                html.H6("low intens treshold"),
                dcc.Slider(1, 10, 1, value=2,
                           id='mz-low-intens-treshold'),
            ],
            header="mz window",
            style={"width": 'auto'})

        self.mz_deconv_box = dbc.Toast([
            html.Br(),
                dbc.Label('low intensety treshold'),
            dbc.Input(id="mz-low-intens-treshhold", placeholder="10000", type='text',
                      size="md", value='10000'),
            html.Br(),
            dbc.Label(children='get', id='conc-pts'),
            #dbc.Textarea(id="oligo-seq-mz", className='mb-3', placeholder="Sequence",
            #             style={"width": "100%", "height": "100 px"}),
            dbc.ButtonGroup(
                [
                    dbc.Button("show selected", id='show-selected-pts-button'),
                    dbc.Button("show all", id='show-all-pts-button'),
                    dbc.Button("save sel", id='save-sel-pts-button'),
                    dbc.Button("get conc", id='conc-pts-button')
                ],
                size="lg",
                className="me-1",
                style={'width': '300px'}
            ),
            html.Br(),
            html.Br(),
            dbc.Col(self.mz_deconv_params, width='auto')
        ],
            header="Oligo mz deconvolution",
        )

        self.mzdata_ident_board = dbc.Container(
            html.Div([
                dbc.Row(dbc.Col(html.Br())),
                dbc.Row([
                    dbc.Col(dbc.Row([
                        self.mz_identifying_buttons,
                        self.mz_deconv_box
                                     ])),
                    dbc.Col(dbc.Row([
                        self.tagging_mz_tab,
                        html.Br(),
                        html.Br(),
                        self.mz_tab
                    ]))
                ])
                ])
        )

        self.mz_tab_content = dbc.Card(
    dbc.CardBody(
        [
            dcc.Graph(id='Scatter-mzdata', figure=graph_mz.figure),
        ]
    ),
    className="mt-3",
)

        self.mass_tab_content = dbc.Card(
    dbc.CardBody(
        [
            dcc.Graph(id='Scatter-mass-data', figure=graph_mass.figure),
            #html.H1('Test')
        ]
    ),
    className="mt-3",
)

        self.graph_tabs = dbc.Tabs(
    [
        dbc.Tab(self.mz_tab_content, label="mzdata Analysis"),
        dbc.Tab(self.mass_tab_content, label="mass Analysis")
    ]
)

        self.params_tabs = dbc.Tabs(
            [
                dbc.Tab(self.params_board, label="data perform"),
                dbc.Tab(self.tagging_param_board, label="data tagging"),
                dbc.Tab(self.finding_fragments_board, label="fragments finding"),
                dbc.Tab(self.mzdata_ident_board, label="mz identifying"),
                dbc.Tab(self.db_content_board, label="data base content"),
            ]
        )


        self.lcms_layout = html.Div([
                #dbc.Row(dbc.Col(dbc.Alert("LCMS analysis App"), width='100%')),
                dbc.Row(dbc.Col(self.upload_area)),
                dbc.Row([
                    dbc.Col(self.graph_tabs),
                    dbc.Col(self.params_tabs)
                ]),
                #dbc.Row(dbc.Textarea(id='textarea_out',
                #                     style={'width': '50%', 'height': 300}))
])

        self.map_tabs_obj = frontend_map_tabs.oligo_maps_tab()

        self.map_tabs = html.Div([
            dbc.Row([
                self.map_tabs_obj.map_tab_,
                self.map_tabs_obj.map_db_tab
            ])
        ])

        self.main_tabs = dbc.Tabs(
            [
                dbc.Tab(self.lcms_layout, label = 'LCMS analyser'),
                dbc.Tab(self.map_tabs, label = 'Maps tables')
        ]
        )

        self.layout = html.Div([
            dbc.Row(dbc.Col(dbc.Alert("LCMS analysis App"), width='100%')),
            self.main_tabs
        ])

    def add_tag_to_tab(self, tag_tab):
        tag_tab = pd.DataFrame(tag_tab)
        columns = ['tag name', 'intensed mass', 'area%', 'seq']
        if len(tag_tab) > 0:
            cols = []
            for c in columns:
                if c in list(tag_tab.keys()):
                    cols.append(c)

            df = tag_tab[cols]
        else:
            df = pd.DataFrame(
            {
                'tag name': [],
                'intensed mass': [],
                'area%': [],
                'seq': [],
                           })
        return df.to_dict('records')
