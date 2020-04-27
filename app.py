import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.subplots as ps
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
#Looks like naming convention for universities is different in this table, may need to map for linking
employment = pd.read_csv('data/tyollistyminen_data.csv')
employment['Työllinen'] = (employment['Työllinen'] / employment['Yhteensä'])
employment['Työtön'] = (employment['Työtön'] / employment['Yhteensä'])
employment['Päätoiminen opiskelija'] = (employment['Päätoiminen opiskelija'] / employment['Yhteensä'])
employment = pd.melt(employment, id_vars=['yliopisto', 'tilastovuosi'], value_vars=['Työllinen','Päätoiminen opiskelija','Työtön','Muut','Muuttanut maasta','Yhteensä'], var_name='Tila',value_name='Keskiarvo')
employment = employment[employment.Tila.isin(['Työllinen', 'Työtön', 'Päätoiminen opiskelija'])]
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

#get list of universities for dropdown
unis = degrees.yliopisto.unique()

#create placeholder figures before they are reloaded with filtered data
fig = px.bar(degrees, x='yliopisto', y='lkm', color='Tutkintotyyppi', title='Completed degrees')
fig2 = px.line_polar(student_feedback, r='Keskiarvo', theta='metric', hover_name='yliopisto', color='yliopisto', range_r=[student_feedback.Keskiarvo.min()-0.2,student_feedback.Keskiarvo.max()+0.2], line_close=True, title='Student feedback')
fig2.update_layout(legend_orientation="h")
fig_345 = ps.make_subplots(rows=3, cols=1)
fig6 = px.bar(publications, x='yliopisto', y='lkm', color='JUFO-taso', title='Publications')
fig7 = px.line(career_feedback, x='metric', y='Keskiarvo', color='yliopisto', hover_name='yliopisto', hover_data=['metric', 'Keskiarvo'], range_y=[1,5], title='Career feedback')
fig7.update_traces(mode='lines+markers')

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
                value=['Aalto-yliopisto', 'Helsingin yliopisto', 'Lapin yliopisto'],
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
                dcc.Graph(id='completed_degrees',figure=fig)
            ],
            className="four columns"
            ),
            html.Div([
                dcc.Graph(id='student_feedback', figure=fig2)
            ],
            className="four columns"
            ),
            html.Div([
                dcc.Graph(id='employment', figure=fig_345)
            ],
            className="four columns"
            ),
        ],
        className="row"
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='publications', figure=fig6)
            ],
            className="four columns"
            ),
            html.Div([
                dcc.Graph(id = 'career_feedback',figure=fig7)
            ],
            className="eight columns"
            ),
        ],
        className="row"
        ),
        ],
)

#Year selector

@app.callback(
    [Output('completed_degrees', 'figure'),
    Output('student_feedback', 'figure'),
    Output('publications','figure'),
    Output('career_feedback','figure'),
    Output('employment', 'figure')],
    [Input('year-selection', 'value'),
    Input('university-selection', 'value')])
def update_year(years, universities):
    #fig1
    filtered_degrees = degrees[degrees['tilastovuosi'].between(years[0], years[1])]
    filtered_degrees = filtered_degrees[filtered_degrees.yliopisto.isin(universities)]
    filtered_degrees = filtered_degrees.groupby(['yliopisto', 'Tutkintotyyppi'], as_index=False).sum()
    filtered_degrees.sort_values(by=['yliopisto','Tutkintotyyppi'], inplace=True)
    fig_degrees = px.bar(filtered_degrees, x='yliopisto', y='lkm', color='Tutkintotyyppi', title='Completed degrees')
    #fig2
    filtered_sfeedback = student_feedback[student_feedback['tilastovuosi'].between(years[0], years[1])]
    filtered_sfeedback = filtered_sfeedback[filtered_sfeedback.yliopisto.isin(universities)]
    filtered_sfeedback = filtered_sfeedback.groupby(['yliopisto','metric'], as_index=False).mean()
    fig_sfeedback = px.line_polar(filtered_sfeedback, r='Keskiarvo', theta='metric', hover_name='yliopisto', color='yliopisto', range_r=[student_feedback.Keskiarvo.min()-0.2,student_feedback.Keskiarvo.max()+0.2], line_close=True, title='Student feedback')
    fig_sfeedback.update_layout(legend_orientation="h")
    fig_sfeedback.update_traces(mode='lines+markers')
    #fig3-6
    filtered_employed = employment[employment['tilastovuosi'].between(years[0], years[1])]
    filtered_employed = filtered_employed[filtered_employed.yliopisto.isin(universities)]
    filtered_employed = filtered_employed.groupby(['yliopisto', 'Tila'], as_index=False).mean()
    fig_345 = px.bar(filtered_employed, facet_row='Tila', x='yliopisto', y='Keskiarvo', height=500, title='Employment 2 years after graduation')
    fig_345.update_yaxes(tickformat = '%')
    fig_345.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    #fig6
    filtered_publications = publications[publications['tilastovuosi'].between(years[0], years[1])]
    filtered_publications = filtered_publications[filtered_publications.yliopisto.isin(universities)]
    filtered_publications = filtered_publications.groupby(['yliopisto', 'JUFO-taso'], as_index=False).sum()
    fig_publications = px.bar(filtered_publications, x='yliopisto', y='lkm', color='JUFO-taso', title='Publications')
    #fig7
    filtered_cfeedback = career_feedback[career_feedback['tilastovuosi'].between(years[0], years[1])]
    filtered_cfeedback = filtered_cfeedback[filtered_cfeedback.yliopisto.isin(universities)]
    filtered_cfeedback = filtered_cfeedback.groupby(['yliopisto', 'metric'], as_index=False).mean()
    fig_cfeedback = px.line(filtered_cfeedback, x='metric', y='Keskiarvo', color='yliopisto', hover_name='yliopisto', hover_data=['metric', 'Keskiarvo'], range_y=[1,5], title='Career feedback')
    fig_cfeedback.update_traces(mode='lines+markers')

    return  fig_degrees, fig_sfeedback, fig_publications, fig_cfeedback, fig_345


#University selector TBD

if __name__ == '__main__':
    app.run_server(debug=True)
