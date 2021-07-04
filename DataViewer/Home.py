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


def home_page(all_runs):

    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("Existing entry",
                                    className='card-title'),
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Dropdown(
                                        options=[{"label": i, "value": i} for i in all_runs], id='select-run')),
                                    dbc.Col(
                                        dbc.Button('Confirm', id='login-button',
                                                   color='success', block=True)
                                    ),
                                ]
                            ),
                            html.Br(),
                            # html.H6(
                            #     'New entry', className='card-title'),
                            # dbc.Row(
                            #     [
                            #         dbc.Col(dbc.Input(id='new-run-runname',
                            #                           placeholder="New profile")),
                            #         dbc.Col(dbc.Button(
                            #             'Submit', id='new-run-button', color='success', block=True)),
                            #     ]
                            # ),
                            # html.Br(),
                            dbc.Spinner(html.Div(id='login-alert'))
                        ],
                        body=True,
                        # color="light",
                    ),
                ),
                justify='center'
            )

        ]
    )
