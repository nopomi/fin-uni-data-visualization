import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objects as go
import plotly.express as px
import flask
import pandas as pd
import numpy as np

external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

degrees = pd.read_csv('data/degrees_data.csv')
student_feedback = pd.read_csv('data/opiskelijapalaute_data.csv')
employment = pd.read_csv('data/tyollistyminen_data.csv')
publications = pd.read_csv('data/jufo_data.csv')
career_feedback = pd.read_csv('data/uraseuranta_data.csv')

#temporary filters and dummy data for prototyping
demo_unis = ['Aalto-yliopisto', 'Helsingin yliopisto', 'Itä-Suomen yliopisto']
degrees = degrees[degrees.yliopisto.isin(demo_unis)]
publications = publications[publications.yliopisto.isin(demo_unis)]
publications = publications[publications['tilastovuosi']==2015]
publications = publications[['yliopisto', 'JUFO-taso', 'lkm']]
student_feedback = pd.DataFrame(dict(
    r=[3.5, 4, 4.2, 4.0, 4.1],
    theta=['Feedback','Teaching','Guidance',
           'Communication', 'Wellbeing']))
employment = employment[employment['tilastovuosi'] == 2015]
employment = employment[['yliopisto', 'Työllinen', 'Päätoiminen opiskelija', 'Työtön']]
employment = employment[employment.yliopisto.isin(demo_unis)]
df = pd.read_csv("https://raw.githubusercontent.com/bcdunbar/datasets/master/iris.csv")
df = df[:3]
fig7 = go.Figure(data=
    go.Parcoords(
        line = dict(color = df['species_id'],
                   colorscale = [[0,'purple'],[0.5,'lightseagreen'],[1,'gold']]),
        dimensions = list([
            dict(range = [0,8],
                constraintrange = [4,8],
                label = 'Career satisfaction', values = df['sepal_length']),
            dict(range = [0,8],
                label = 'Learned skills', values = df['sepal_width']),
            dict(range = [0,8],
                label = 'Entrepreneurship', values = df['petal_length']),
            dict(range = [0,8],
                label = 'Applicability', values = df['petal_width'])
        ])
    )
)
#END OF DUMMY DATA

fig = px.bar(degrees[['yliopisto', 'Alempi korkeakoulututkinto', 'Ylempi korkeakoulututkinto', 'Tohtorintutkinto']], x='yliopisto', y='Alempi korkeakoulututkinto')
fig2 = px.line_polar(student_feedback, r='r', theta='theta')
fig3 = px.bar(employment[['yliopisto', 'Työllinen']], x='yliopisto', y='Työllinen')
fig4 = px.bar(employment[['yliopisto', 'Päätoiminen opiskelija']], x='yliopisto', y='Päätoiminen opiskelija')
fig5 = px.bar(employment[['yliopisto', 'Työtön']], x='yliopisto', y='Työtön')
fig6 = px.bar(publications, x='yliopisto', y='lkm', color='JUFO-taso')

server = app.server

top_markdown_text = '''
### Compare universities!
'''

app.layout = html.Div([
    html.Div([
    dcc.Markdown(children=top_markdown_text),
    ],
    className='six columns'
    ),
    html.Div([
        html.Div([
            html.P(
                'Filter univerities:',
                className="control_label"
            ),
            dcc.Dropdown(
                id='university-selection',
                options=[
                    {'label':'Helsingin Yliopisto', 'value':'Helsingin Yliopisto'},
                    {'label': 'Itä-Suomen Yliopisto', 'value':'Itä-Suomen Yliopisto'},
                    {'label':'Aalto-Yliopisto', 'value':'Aalto-Yliopisto'}
                ],
                multi=True
            ),
        ],
        className='two columns'
        ),
        html.Div([
            html.P(
                'Filter years:',
                className="control_label"
            ),
            dcc.RangeSlider(
                id='year-selection',
                min=2015,
                max=2019,
                step=1.0,
                value=[2015, 2019],
                marks={
                    2015: '2015',
                    2016: '2016',
                    2017: '2017',
                    2018: '2018',
                    2019: '2019'
                }
            ),
        ],
        className='two columns',
        style={'margin-left': '40px'}
        ),
        ],
        className="row"
        ),
        html.Div([
            html.Div([
                dcc.Graph(figure=fig)
            ],
            className="four columns"
            ),
            html.Div([
                dcc.Graph(figure=fig2)
            ],
            className="four columns"
            ),
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig5, style={'height':200})
                ],
                className="row"
                ),
                html.Div([
                    dcc.Graph(figure=fig4, style={'height':200})
                ],
                className="row"
                ),
                html.Div([
                    dcc.Graph(figure=fig3, style={'height':200})
                ],
                className="row"
                ),
            ],
            className="four columns"
            ),
        ],
        className="row"
        ),
        html.Div([
            html.Div([
                dcc.Graph(figure=fig6)
            ],
            className="four columns"
            ),
            html.Div([
                dcc.Graph(figure=fig7)
            ],
            className="eight columns"
            ),
        ],
        className="row"
        ),
        ],
)

#Year selector
"""
@app.callback(
    Output('year-test-output', 'children'),
    [Input('year-selection', 'value')])
def update_year(value):
    return f"First selector: {value[0]} and second selector: {value[1]}"
"""

#University selector TBD

if __name__ == '__main__':
    app.run_server(debug=True)
