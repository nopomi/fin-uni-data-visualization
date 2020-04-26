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

#Load and transform data
degrees = pd.read_csv('data/degrees_data_2.csv')
student_feedback = pd.read_csv('data/opiskelijapalaute_data.csv')
student_feedback = student_feedback[['väittämä', 'yliopisto', 'tilastovuosi', 'Keskiarvo (rahoitusmalli)']]
student_feedback = student_feedback.rename(columns={'Keskiarvo (rahoitusmalli)':'Keskiarvo', 'väittämä':'metric'})
student_feedback['metric'] = student_feedback['metric'].map({
    'Voin hyvin yliopistossani.':'Well-being & Satisfaction',
    'Olen tyytyväinen omaan opiskeluuni.':'Well-being & Satisfaction',
    'Minun on ollut helppoa löytää opintoihini liittyvää tietoa ja tukea.':'Study guidance',
    'Ongelmatilanteissa olen tarvittaessa löytänyt henkilön, jolta olen voinut pyytää neuvoa.':'Study guidance',
    'Tarjolla on ollut riittävästi ohjausta opintojen suunnitteluun.':'Study guidance',
    'Olen ollut  tyytyväinen käytettyihin opetusmenetelmiin.':'Teaching',
    'Opetus on ollut  mielestäni pääosin laadukasta.':'Teaching',
    'Olen ollut tyytyväinen vuorovaikutukseeni opetushenkilökunnan kanssa.':'Teacher interaction',
    'Opettajilta saamani palaute on auttanut minua opinnoissani.':'Teacher interaction',
    'Olen ollut tyytyväinen opinto-ohjelmani tarjoamiin vaikutus- ja osallistumismahdollisuuksiin (esim. opetussuunnitteluun osallistuminen ja palautteen antamisen mahdollisuudet).':'Teacher interaction',
    'Koulutukseni on vastannut  sille asetettuja tavoitteita.':'Degree satisfaction',
    'Koulutuksen myötä kehittynyt osaamiseni vastaa odotuksiani.':'Degree satisfaction',
    'Tarjolla on ollut riittävästi ohjausta kandidaatin tutkielman laatimiseen/opinnäytteen tekemiseen.':'Thesis guidance'
})
student_feedback = student_feedback.groupby(['yliopisto','metric','tilastovuosi'], as_index=False).mean()
employment = pd.read_csv('data/tyollistyminen_data.csv')
publications = pd.read_csv('data/jufo_data.csv')
publications['JUFO-taso'] = publications['JUFO-taso'].astype(str)
career_feedback = pd.read_csv('data/uraseuranta_data.csv')
career_feedback = career_feedback[['väittämä','yliopisto', 'tilastovuosi', 'Keskiarvo (maisterit)']]
career_feedback = career_feedback.rename(columns={'väittämä':'metric', 'Keskiarvo (maisterit)':'Keskiarvo'})
career_feedback['metric'] = career_feedback['metric'].map({
    '19.  Arvioi vuonna 2012 suorittamaasi tutkintoa ja nykyistä työtäsi. Valitse sopivin vaihtoehto seuraaviin väitteisiin:  a) Pystyn hyödyntämään yliopistossa oppimiani tietoja ja taitoja nykyisessä työssäni hyvin.':'Career benefit',
    'a) Pystyn hyödyntämään yliopistossa oppimiani tietoja ja taitoja nykyisessä työssäni hyvin.':'Career benefit',
    'd)  Koulutus antoi riittävät valmiudet työelämään.':'Career benefit',
    '3.4 Koulutus antoi riittävät valmiudet työelämään.':'Career benefit',
    '4.  Miten tyytyväinen olet kokonaisuudessaan vuonna 2012 suorittamaasi tutkintoon työurasi kannalta?':'Career benefit',
    '4. Miten tyytyväinen olet kokonaisuudessaan vuonna 2013 suorittamaasi tutkintoon työurasi kannalta?':'Career benefit',
    '3)  analyyttiset, systemaattisen ajattelun taidot':'Learning & thinking skills',
    '3) analyyttiset, systemaattisen ajattelun taidot':'Learning & thinking skills',
    '21)  kyky oppia ja omaksua uutta':'Learning & thinking skills',
    '21) kyky oppia ja omaksua uutta':'Learning & thinking skills',
    '4)  tiedonhankintataidot':'Learning & thinking skills',
    '4) tiedonhankintataidot':'Learning & thinking skills',
    'b) Työni vastaa vaativuustasoltaan hyvin yliopistollista koulutustani.':'Job challenge',
    '23)  tieteiden- tai taiteidenvälisyys/moniammatillisissa ryhmissä toimiminen':'Interdisciplinary capability',
    '23) tieteiden- tai taiteidenvälisyys/moniammatillisissa ryhmissä toimiminen':'Interdisciplinary capability',
    '26)  itseohjautuvuus/oma-aloitteisuus':'Self-directedness',
    '26) itseohjautuvuus/oma-aloitteisuus':'Self-directedness',
    '27)  yrittäjyystaidot':'Entrepreneurship',
    '27) yrittäjyystaidot':'Entrepreneurship'
})
career_feedback = career_feedback.groupby(['yliopisto', 'tilastovuosi', 'metric'], as_index=False).mean()
career_feedback['yliopisto-tilastovuosi'] = career_feedback['yliopisto'] + '.' + career_feedback['tilastovuosi'].astype(str)
career_feedback = career_feedback.pivot(index='yliopisto-tilastovuosi', columns='metric', values='Keskiarvo')
career_feedback.reset_index(inplace=True)
career_feedback['yliopisto'] = career_feedback['yliopisto-tilastovuosi'].str.split('.', expand=True)[0]
career_feedback['tilastovuosi'] = career_feedback['yliopisto-tilastovuosi'].str.split('.', expand=True)[1]
career_feedback.drop(['yliopisto-tilastovuosi'], axis=1, inplace=True)

unis = degrees.yliopisto.unique()

#temporary data restrictions and dummy data
student_feedback = student_feedback[student_feedback['tilastovuosi']==2019]
employment = employment[employment['tilastovuosi'] == 2015]
employment = employment[['yliopisto', 'Työllinen', 'Päätoiminen opiskelija', 'Työtön']]
#END OF DUMMY DATA

fig = px.bar(degrees, x='yliopisto', y='lkm', color='Tutkintotyyppi')
fig2 = px.line_polar(student_feedback, r='Keskiarvo', theta='metric', hover_name='yliopisto', color='yliopisto', range_r=[student_feedback.Keskiarvo.min()-0.2,student_feedback.Keskiarvo.max()+0.2], line_close=True)
fig2.update_layout(legend_orientation="h")
fig3 = px.bar(employment[['yliopisto', 'Työllinen']], x='yliopisto', y='Työllinen')
fig4 = px.bar(employment[['yliopisto', 'Päätoiminen opiskelija']], x='yliopisto', y='Päätoiminen opiskelija')
fig5 = px.bar(employment[['yliopisto', 'Työtön']], x='yliopisto', y='Työtön')
fig6 = px.bar(publications, x='yliopisto', y='lkm', color='JUFO-taso')
fig7 = px.parallel_coordinates(career_feedback, dimensions=['Entrepreneurship','Interdisciplinary capability', 'Job challenge', 'Learning & thinking skills', 'Self-directedness'])

server = app.server

top_markdown_text = '''
### Compare university funding metrics
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
                options=[{'label':x, 'value':x} for x in unis],
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
