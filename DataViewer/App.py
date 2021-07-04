"""
Author: Ruiheng Su

Engineering Physics, UBC

ruihengsu@alumni.ubc.ca

2021
"""

import dash
from dash import no_update
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH, ALLSMALLER

from Home import home_page
from Analysis import analysis
from SideBar import sidebar, TABS

from ManageData import DataManager


import numpy as np
from datetime import datetime

DM = DataManager("Measurement_Data")
FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"

app = dash.Dash(
    external_stylesheets=[dbc.themes.SANDSTONE, FA],
    suppress_callback_exceptions=True,)
server = app.server


content = html.Div(home_page(DM.all_runs()),
                   id="page-content", className="content")
app.layout = html.Div([dcc.Location(id="url"), sidebar(), content])

# set the content according to the current pathname


@ app.callback(
    [Output("page-content", "children"),
     Output("home-link", "active"),
     Output("connect-link", "active"),
     Output("analysis-link", "active"),
     Output("home-link", "disabled")],
    Input("url", "pathname")
)
def render_page_content(pathname):
    """
    """
    # at the home page
    if pathname == TABS[0]:
        all_runs = DM.all_runs()
        return home_page(all_runs), True, False, False, False
    # page to connect to scope
    elif pathname == TABS[1] and DM.new_run is not None:
        return html.P("This page is under development"), False, True, False, True
    # page to do analysis
    elif pathname == TABS[2] and DM.new_run is not None:
        return analysis([]), False, False, True, True
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The page {pathname} does not exist..."),
            html.P(f"Or you attempted to access this page without loading a profile"),
        ]
    ), no_update, no_update, no_update, no_update


@ app.callback(
    [Output('login-alert', 'children'),
     Output('connect-link', 'disabled'),
     Output('analysis-link', 'disabled')],
    [Input('login-button', 'n_clicks'),
     ],
    [State('select-run', 'value'), ])
def login_auth(n_clicks_login, runname):
    """
    """
    if (n_clicks_login is None or n_clicks_login == 0):
        return [no_update, True, True]

    elif (n_clicks_login >= 0):
        if runname in DM.all_runs():
            DM.new_run = runname
            return [dbc.Alert('Run loaded!', color='success', dismissable=True), False, False]

    return [dbc.Alert('Try again!', color='danger', dismissable=True), True, True]


def wrap_component(component):
    """
    Wraps components given as a list nicely
    """
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.Row(
                            component
                        ),
                    ],
                ),
            )
        ],
    )


@ app.callback(
    Output('analysis', 'children'),
    [Input('new-plot-button', 'n_clicks')],
    [State('analysis', 'children')]
)
def display_graphs(n_clicks, div_children):
    """
    """
    parsed = DM.list_parsed_data()

    new_child = html.Div(
        children=[
            html.Br(),
            wrap_component(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Label(
                                                "Data"),
                                            dcc.Dropdown(
                                                id={
                                                    'type': 'dynamic-dpn-A',
                                                    'index': n_clicks
                                                },
                                                options=[{'label': c, 'value': c}
                                                         for c in parsed["PID"]],
                                                # clearable=False
                                            ),
                                        ]
                                    ),
                                    dbc.FormGroup(
                                        [
                                            dbc.Label(
                                                "Trace"),
                                            dcc.Dropdown(
                                                id={
                                                    'type': 'dynamic-dpn-trace',
                                                    'index': n_clicks
                                                },
                                                multi=True,
                                                # clearable=False
                                            ),
                                        ],
                                    ),
                                    # dbc.FormGroup(
                                    #     [
                                    #         dbc.Label(
                                    #             "Settings"),
                                    #         dcc.Dropdown(
                                    #             id={
                                    #                 'type': 'dynamic-dpn-S',
                                    #                 'index': n_clicks
                                    #             },
                                    #             options=[{'label': s, 'value': s}
                                    #                      for s in parsed[ManageData.SETTING]],
                                    #             # clearable=False
                                    #         ),
                                    #     ],
                                    # ),
                                    dbc.FormGroup(
                                        [
                                            dbc.Textarea(
                                                id={
                                                    'type': 'dynamic-dpn-textarea',
                                                    'index': n_clicks
                                                },
                                                value=""
                                                # clearable=False
                                            ),
                                        ],
                                    ),
                                    dbc.FormGroup(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Button('Delete', id={
                                                            'type': 'dynamic-dpn-del-data',
                                                            'index': n_clicks
                                                        },
                                                            color='danger', block=True)
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button('Prev', id={
                                                            'type': 'dynamic-dpn-prev-data',
                                                            'index': n_clicks
                                                        },
                                                            color='secondary', block=True)
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button('Next', id={
                                                            'type': 'dynamic-dpn-next-data',
                                                            'index': n_clicks
                                                        },
                                                            color='success', block=True)
                                                    ),
                                                ],
                                                no_gutters=True,
                                            ),
                                        ],
                                    ),
                                ],
                                body=True,
                                style={'border': 'none'}
                            )
                        ],
                        md=4
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Spinner(
                                    dcc.Graph(
                                        id={
                                            'type': 'dynamic-graph',
                                            'index': n_clicks
                                        },
                                        figure={},
                                        style={"height": "60vh"}
                                    ),
                                    color="primary"),
                            ],
                            style={'border': 'none'}
                        ),
                        md=8,
                        style={'border': 'none'}
                    ),
                ],
            )
        ]
    )
    div_children.append(new_child)
    return div_children


@ app.callback(
    [Output({'type': 'dynamic-dpn-trace', 'index': MATCH}, 'options'),
     Output({'type': 'dynamic-dpn-trace', 'index': MATCH}, 'value'), ],
    [Input(component_id={'type': 'dynamic-dpn-A',
                         'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'dynamic-dpn-del-data',
                         'index': MATCH}, component_property='n_clicks')]
)
def update_select_trace(a_value, del_clicks):
    """
    """
    if (del_clicks is None or del_clicks == 0):
        pass
    elif (del_clicks > 0) and a_value is not None:
        return [[], None]

    if a_value is not None:
        print(a_value)
        # return [{'label': "Tr {}".format(i), 'value': i}
        # for i in range(0, numcols)]
        return [[{'label': "Set Point", 'value': 0},
                 {'label': "Process Variable", 'value': 1},
                 {'label': "Controller Output", 'value': 2}], [0, 1, 2]]

    else:
        return [[], []]


@ app.callback(
    Output({'type': 'dynamic-dpn-textarea', 'index': MATCH}, 'value'),
    [Input(component_id={'type': 'dynamic-dpn-A',
                         'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'dynamic-dpn-del-data',
                         'index': MATCH}, component_property='n_clicks')]
)
def update_show_setting(a_value, del_clicks):
    """
    Assumes that there exists a settings file for that data folder.
    """
    if (del_clicks is None or del_clicks == 0):
        pass
    elif (del_clicks > 0) and a_value is not None:
        return ""

    if a_value is not None:
        setting = DM.load_summary(a_value+"_settings")
        return str(setting)
    else:
        return ""


@ app.callback(
    [Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
     Output(component_id={'type': 'dynamic-dpn-A',
                          'index': MATCH}, component_property='options'),
     Output(component_id={'type': 'dynamic-dpn-A',
                          'index': MATCH}, component_property='value'), ],
    [Input(component_id={'type': 'dynamic-dpn-trace',
                         'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'dynamic-dpn-del-data',
                         'index': MATCH}, component_property='n_clicks'),
     Input(component_id={'type': 'dynamic-dpn-next-data',
                         'index': MATCH}, component_property='n_clicks'),
     Input(component_id={'type': 'dynamic-dpn-prev-data',
                         'index': MATCH}, component_property='n_clicks'),],
    [State(component_id={'type': 'dynamic-dpn-A',
                         'index': MATCH}, component_property='value'), ]
)
def update_graph(trace_value, del_clicks, next_clicks, prev_clicks, a_val):
    ctx = dash.callback_context

    if not ctx.triggered:
        return [no_update, no_update, no_update, ]
    else: 
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    a_value = a_val
    fig = go.Figure()
    fig.layout.template = "simple_white"

    if "dynamic-dpn-del-data" in button_id:
        DM.del_data(a_value)
        return [fig, [{'label': c, 'value': c} for c in DM.list_parsed_data()["PID"]], None, ]

    parsed = DM.list_parsed_data()["PID"]

    if a_value is not None: 
        a_value_index = parsed.index(a_value)
       
        if "dynamic-dpn-next-data" in button_id:
            if a_value_index < len(parsed) - 1:
                a_value_index += 1
            else: 
                a_value_index = 0
            a_value = parsed[a_value_index]

        if "dynamic-dpn-prev-data" in button_id:
            if a_value_index > 0:
                a_value_index = a_value_index - 1
            else: 
                a_value_index = -1
            a_value = parsed[a_value_index]

    if a_value is None or trace_value is [] or trace_value is None:
        return [fig, no_update, no_update, ]

    if not isinstance(trace_value, list):
        trace_value = [trace_value, ]

    for i in trace_value:
        fig, num_peaks = DM.plot_curve(a_value,
                                       fig,
                                       i,)

    return [fig, no_update, a_value, ]


if __name__ == "__main__":
    app.run_server(debug=False)
