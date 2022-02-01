# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 15:30:57 2022

@author: Farley
"""

# importando bibliotecas
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
# import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context  # pip install dash (version 2.0.0 or higher)
from urllib.request import urlopen
import json

app = Dash(__name__)
server = app.server

# carregando banco de dados
df = pd.read_csv('RAISVINCULOSMG20102020nome.csv')
print(df.head())
print(df.describe())
with urlopen('https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-31-mun.json') as response:
    counties = json.load(response)

selections = list()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Mercado de trabalho formal - Minas Gerais (2010 - 2020)",
            style={'text-align': 'center'}),

    dcc.Slider(
        id='slct_year',
        min=df['ano'].min(),
        max=df['ano'].max(),
        value=df['ano'].max(),
        marks={str(ano): str(ano) for ano in df['ano'].unique()},
        step=None
    ),

    html.Div([
        html.Div(id='output_container', children=[]),
        html.Br(),

        dcc.Graph(id='rais_map', figure={}),
    ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'middle'}),

    html.Div([

        html.Div([
            html.Button(id='resetar', n_clicks=0, children="resetar"),
        ], style={'horizontal-align': 'right'}),

        dcc.Graph(id="line-chart")
    ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'middle'}),

])


# -----------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='rais_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')])
#    [Output("line-chart", "figure")],
#    [Input("checklist", "value")])

def update_graph(option_slctd):
    total_trab = df['vinculos'].loc[df['ano'] == option_slctd].sum()
    container = "O total de trabalhadores formais em Minas Gerais ao final de {}, foi de {} trabalhadores".format(
        option_slctd, total_trab)

    dfmap = df.copy()
    dfmap = dfmap[dfmap['ano'] == option_slctd]

    fig = px.choropleth_mapbox(dfmap,
                               geojson=counties,
                               locations='municipio',
                               featureidkey="properties.id",
                               color='vinculos',
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               center={"lat": -18.8416, "lon": -45.3865}, zoom=5,
                               range_color=(0, 10000),
                               hover_data=['nome'],
                               labels={'vinculos': 'Trabalhadores'},
                               opacity=0.7
                               )

    fig.update_traces(marker_line_width=0.5)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return container, fig


@app.callback(
    Output("line-chart", "figure"),
    [Input("rais_map", "clickData"),
     Input('resetar', 'n_clicks')])
def update_line_chart(clickData, n_clicks):
    # ------------------------------------------------------------------------------
    location = df['municipio'].min()

    if clickData is not None:
        location = clickData['points'][0]['location']
        if location not in selections:
            selections.append(location)
        else:
            selections.remove(location)
    # ------------------------------------------------------------------------------
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'resetar' in changed_id:
        selections.clear()
    # ------------------------------------------------------------------------------
    dff = df[df['municipio'].isin(selections)]
    dff = dff.sort_values(by="ano")
    fig = px.line(dff,
                  x="ano", y="vinculos", color='nome', markers=True,
                  labels={'nome': 'Município', 'vinculos': 'Total de Trabalhadores', 'ano': 'Ano'})
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(2010, 2021)),
        ))
    return fig


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)