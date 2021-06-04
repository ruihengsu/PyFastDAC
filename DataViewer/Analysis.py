"""
Author: Ruiheng Su

Engineering Physics, UBC

ruihengsu@alumni.ubc.ca

2020
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


def newgraph():
    return

def addColumn(dashObj):
    return dbc.Col(dashObj)


def analysis(graphlist):
    """
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Row(
                                    [
                                        addColumn(
                                            dbc.Button('Add new plot',
                                                       id='new-plot-button',
                                                       block=True,
                                                       color="primary",
                                                       n_clicks=0)
                                        ),
                                    ]
                                ),
                            ]
                        )
                    )
                ]
            )
        ],
        id="analysis"
    )
    # dbc.Card(
    #     dbc.CardBody(
    #         [
    #             dbc.Card(
    #                 [
    #                     dbc.Row(
    #                         [
    #                             dbc.Col(
    #                                 [
    #                                     dbc.Card(
    #                                         [
    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Trigger instance [uS]"),
    #                                                     dbc.Input(
    #                                                         id='trigger-instance-input',
    #                                                         placeholder="Input...",
    #                                                         value="0",
    #                                                         type="text"),
    #                                                     # dbc.FormText(
    #                                                     #     "Type something in the box above"),
    #                                                 ]
    #                                             ),

    #                                             dbc.Row(
    #                                                 [
    #                                                     dbc.Col(
    #                                                         dbc.FormGroup(
    #                                                             [
    #                                                                 dbc.Label(
    #                                                                     "Summary"),
    #                                                                 dcc.Dropdown(
    #                                                                     id='summary-dropdown',
    #                                                                     options=s_options,
    #                                                                 ),
    #                                                             ]
    #                                                         ),
    #                                                     ),
    #                                                     dbc.Col(
    #                                                         dbc.FormGroup(
    #                                                             [
    #                                                                 dbc.Label(
    #                                                                     "Tune boxes"),
    #                                                                 dcc.Dropdown(
    #                                                                     id='tbox-dropdown',
    #                                                                     # options=t_options,
    #                                                                     multi=True,
    #                                                                 ),
    #                                                             ]
    #                                                         ),
    #                                                     )
    #                                                 ]
    #                                             ),

    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Voltage"),
    #                                                     dcc.Dropdown(
    #                                                         id='v-dropdown',
    #                                                         # options=t_options,
    #                                                         multi=True,
    #                                                         # value="MTL"
    #                                                     ),
    #                                                 ]
    #                                             ),
    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Current"),
    #                                                     dcc.Dropdown(
    #                                                         id='c-dropdown',
    #                                                         # options=t_options,
    #                                                         multi=True,
    #                                                         # value="MTL"
    #                                                     ),
    #                                                 ]
    #                                             ),
    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Data points"),
    #                                                     dcc.Slider(
    #                                                         id='plot-percent-slider',
    #                                                         min=5,
    #                                                         max=100,
    #                                                         step=5,
    #                                                         value=20,
    #                                                         marks={i: '{}%'.format(
    #                                                             i) for i in range(10, 105, 20)},
    #                                                     )
    #                                                 ]
    #                                             ),
    #                                         ],
    #                                         body=True,
    #                                         style={'border': 'none'}
    #                                     )
    #                                 ],
    #                                 md=4
    #                             ),
    #                             dbc.Col(
    #                                 dbc.Card(
    #                                     [
    #                                         dbc.Spinner(
    #                                             dcc.Graph(id='graph1'),
    #                                             color="primary"),
    #                                     ],
    #                                     style={'border': 'none'}
    #                                 ),
    #                                 md=8,
    #                                 style={'border': 'none'}
    #                             )
    #                         ],
    #                         align="center",
    #                         no_gutters=True,
    #                     ),
    #                 ]
    #             ),
    #             html.Br(),
    #             dbc.Card(
    #                 [
    #                     dbc.Row(
    #                         [
    #                             dbc.Col(
    #                                 [
    #                                     dbc.Card(
    #                                         [
    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Peak number"),
    #                                                     dcc.Dropdown(
    #                                                         id='peak_num-dropdown',
    #                                                         # options=t_options,
    #                                                         # multi=True,
    #                                                         # value="MTL"
    #                                                     ),
    #                                                 ]
    #                                             ),
    #                                             dbc.FormGroup(
    #                                                 [
    #                                                     dbc.Label(
    #                                                         "Save tune box data"),
    #                                                     dbc.Row(
    #                                                         dbc.Col(
    #                                                             dbc.Input(
    #                                                                 id="filename-input",
    #                                                                 placeholder="Save as...",
    #                                                                 type="text",
    #                                                                 value=''
    #                                                             ),
    #                                                         ),
    #                                                     ),
    #                                                     html.Br(),
    #                                                     dbc.Row(
    #                                                         [
    #                                                             dbc.Col(
    #                                                                 dcc.Dropdown(
    #                                                                     id='tbox-download-dropdown',
    #                                                                     multi=False,
    #                                                                 ),
    #                                                             ),
    #                                                             dbc.Col(
    #                                                                 dbc.Button(
    #                                                                     html.A(
    #                                                                         'Download Data',
    #                                                                         id='download-link',
    #                                                                         download="rawdata.csv",
    #                                                                         href="",
    #                                                                         target="_blank",
    #                                                                     ),
    #                                                                     id='download-button',
    #                                                                     outline=True,
    #                                                                     color="dark",
    #                                                                     block=True,
    #                                                                     disabled=True),
    #                                                             )]
    #                                                     ),
    #                                                 ]
    #                                             ),
    #                                         ],
    #                                         body=True,
    #                                         style={'border': 'none'}
    #                                     )
    #                                 ],
    #                                 md=4
    #                             ),
    #                             dbc.Col(
    #                                 dbc.Card(
    #                                     [
    #                                         dbc.Spinner(
    #                                             dcc.Graph(id='graph2'),
    #                                             color="primary"),
    #                                     ],
    #                                     style={'border': 'none'}
    #                                 ),
    #                                 md=8,
    #                                 style={'border': 'none'}
    #                             )
    #                         ],
    #                         align="center",
    #                         no_gutters=True,
    #                     ),
    #                 ]
    #             ),
    #             html.Br(),

    #             # html.Br(),
    #             # dbc.Card
    #             # (
    #             #     [
    #             #         dcc.Upload(
    #             #             [
    #             #                 html.H5(
    #             #                     "Drag and drop / Select new data files"),
    #             #             ],
    #             #             id='upload-data',
    #             #             style={
    #             #                 'textAlign': 'center',
    #             #             },
    #             #             # Allow multiple files to be uploaded
    #             #             multiple=True
    #             #         ),
    #             #     ],
    #             #     body=True
    #             # ),
    #         ]
    #     ),
    #     className="analysis",
    # )
