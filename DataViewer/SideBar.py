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

UBC_LOGO = "assets/ubc.png"
MY_LOGO = "assets/sp.png"
TABS = ['/', '/connect', '/analysis']


def sidebar():
    sidebar = html.Div(
        [
            html.Div(
                [
                    # width: 3rem ensures the logo is the exact width of the
                    # collapsed sidebar (accounting for padding)
                    html.Img(src=MY_LOGO, style={"width": "3rem"}),
                    html.H2("Welcome"),
                ],
                className="sidebar-header",
            ),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-home mr-2"),
                            # html.Span("Home")
                        ],
                        href=TABS[0],
                        active=True,
                        disabled=False,
                        id="home-link",
                    ),
                    html.Br(),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-plug"),
                            # html.Span("Connect"),
                        ],
                        href=TABS[1],
                        # active="exact",
                        disabled=True,
                        active=False,
                        id="connect-link",
                    ),
                    html.Br(),
                    dbc.NavLink(
                        [
                            html.I(className="fas fa-chart-bar"),
                            # html.Span("  Analysis"),
                        ],
                        href=TABS[2],
                        active="False",
                        disabled=True,
                        id="analysis-link",
                    ),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar",
    )
    return sidebar
