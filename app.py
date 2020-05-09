import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly
import plotly.subplots as ps
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import flask
import pandas as pd
import numpy as np

pio.templates.default = "plotly_white"
external_stylesheet = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

#Load and transform data
degrees = pd.read_csv('data/degrees_data_2.csv')
degrees = degrees.rename(columns={'Tutkintotyyppi':'Degree level'})
degrees['Degree level'] = degrees['Degree level'].replace({
    'Alempi korkeakoulututkinto':'Bachelor\'s',
    'Ylempi korkeakoulututkinto':'Master\'s',
    'Tohtorintutkinto':'PhD'
})
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
student_feedback['yliopisto'] = student_feedback['yliopisto'].replace({
    'Lappeenrannan-Lahden teknillinen yliopisto':'Lappeenrannan–Lahden teknillinen yliopisto',
    'Itä-Suomen Yliopisto':'Itä-Suomen yliopisto'
})

employment = pd.read_csv('data/tyollistyminen_data.csv')
employment['Työllinen'] = (employment['Työllinen'] / employment['Yhteensä'])
employment['Työtön'] = (employment['Työtön'] / employment['Yhteensä'])
employment['Päätoiminen opiskelija'] = (employment['Päätoiminen opiskelija'] / employment['Yhteensä'])
employment = pd.melt(employment, id_vars=['yliopisto', 'tilastovuosi'], value_vars=['Työllinen','Päätoiminen opiskelija','Työtön','Muut','Muuttanut maasta','Yhteensä'], var_name='Tila',value_name='Keskiarvo')
employment = employment[employment.Tila.isin(['Työllinen', 'Työtön', 'Päätoiminen opiskelija', ''])]
employment['yliopisto'] =employment['yliopisto'].replace({
    'Lappeenrannan tekn. yliopisto':'Lappeenrannan–Lahden teknillinen yliopisto'
})
publications = pd.read_csv('data/jufo_data.csv')
publications = publications.rename(columns={'JUFO-taso':'JUFO-class'})
publications['JUFO-class'] = publications['JUFO-class'].astype(str)
publications['yliopisto'] = publications['yliopisto'].replace({
    'Lappeenrannan-Lahden teknillinen yliopisto':'Lappeenrannan–Lahden teknillinen yliopisto'
})
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
career_feedback['yliopisto'] = career_feedback['yliopisto'].replace({
    'Lappeenrannan-Lahden teknillinen yliopisto':'Lappeenrannan–Lahden teknillinen yliopisto'
})
career_feedback = career_feedback.groupby(['yliopisto', 'tilastovuosi', 'metric'], as_index=False).mean()

#get list of universities for dropdown
unis = degrees.yliopisto.unique()

#create placeholder figures before they are reloaded with filtered data
fig = px.bar()
fig2 = ps.make_subplots(rows=1,cols=5)
fig_345 = px.bar()
fig6 = px.bar()
fig7 = ps.make_subplots(rows=1,cols=6)

server = app.server

top_markdown_text = '''
### Compare university funding metrics
'''

app.layout = html.Div([
    html.Div([
    dcc.Markdown(children=top_markdown_text),
    ],
    className='five columns'
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
        className='four columns'
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
                dcc.Graph(id='publications', figure=fig6)
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
                dcc.Graph(id = 'student_feedback',figure=fig2)
            ],
            ),
        ],
        className="row"
        ),
        html.Div([
            html.Div([
                dcc.Graph(id = 'career_feedback',figure=fig7)
            ],
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
    filtered_degrees = filtered_degrees.groupby(['yliopisto', 'Degree level'], as_index=False).sum()
    filtered_degrees.sort_values(by=['yliopisto','Degree level'], inplace=True)
    fig_degrees = px.bar(filtered_degrees, x='yliopisto', y='lkm', color='Degree level', title='Completed degrees')
    fig_degrees.update_xaxes(title='')
    fig_degrees.update_yaxes(title='')
    #fig2
    filtered_sfeedback = student_feedback[student_feedback['tilastovuosi'].between(years[0], years[1])]
    filtered_sfeedback = filtered_sfeedback[filtered_sfeedback.yliopisto.isin(universities)]
    filtered_sfeedback = filtered_sfeedback.groupby(['yliopisto','metric'], as_index=False).mean()
    filtered_sfeedback = filtered_sfeedback.sort_values(by=['yliopisto'], ascending=False)
    fig_sfeedback = ps.make_subplots(rows=1, cols=5, shared_xaxes=True, shared_yaxes=True, subplot_titles=("Degree satisfaction","Study guidance","Teaching","Teacher interaction","Well-being & satisfaction"))
    sfeed_dimensions = ["Degree satisfaction","Study guidance","Teaching","Teacher interaction","Well-being & Satisfaction"]
    for i, dim in enumerate(sfeed_dimensions, start=1):
        fig_sfeedback.add_trace(
            go.Bar(
                x = filtered_sfeedback[filtered_sfeedback['metric'] == dim].Keskiarvo,
                y = filtered_sfeedback[filtered_sfeedback['metric'] == dim].yliopisto,
                orientation='h',
                textposition='inside',
                texttemplate='%{x:.2f}'
            ),
            row=1,
            col=i
        )
    fig_sfeedback.update_layout(title_text='Student feedback (after bachelor\'s degree)', showlegend=False, height = 120 + (50 * len(universities)))
    for i in fig_sfeedback['layout']['annotations']:
        i['font'] = dict(size=14, color='#000000')
    filtered_employed = employment[employment['tilastovuosi'].between(years[0], years[1])]
    filtered_employed = filtered_employed[filtered_employed.yliopisto.isin(universities)]
    filtered_employed = filtered_employed.groupby(['yliopisto', 'Tila'], as_index=False).mean()
    fig_employment = ps.make_subplots(rows=2, cols=1, shared_xaxes=True, shared_yaxes=False)
    fig_employment.append_trace(
        go.Bar(
        x=filtered_employed[filtered_employed.Tila == 'Työllinen'].yliopisto,
        y=filtered_employed[filtered_employed.Tila == 'Työllinen'].Keskiarvo,
        name='Employed',
        text = filtered_employed[filtered_employed['Tila'] == 'Työllinen'].Keskiarvo,
        textposition='inside',
        texttemplate='%{y:.1%}'
        ), row=1, col=1
    )
    fig_employment.append_trace(
        go.Bar(
        x=filtered_employed[filtered_employed.Tila == 'Työtön'].yliopisto,
        y=filtered_employed[filtered_employed.Tila == 'Työtön'].Keskiarvo,
        name = 'Unemployed',
        text = filtered_employed[filtered_employed['Tila'] == 'Työllinen'].Keskiarvo,
        textposition='inside',
        texttemplate='%{y:.1%}'
        ), row=2, col=1
    )
    fig_employment.update_yaxes(tickformat='%')
    fig_employment.update_yaxes(autorange='reversed', row=2,col=1)
    fig_employment.update_layout(title_text="Employment status (2 years after graduating)")

    #fig6
    filtered_publications = publications[publications['tilastovuosi'].between(years[0], years[1])]
    filtered_publications = filtered_publications[filtered_publications.yliopisto.isin(universities)]
    filtered_publications = filtered_publications.groupby(['yliopisto', 'JUFO-class'], as_index=False).sum()
    fig_publications = px.bar(filtered_publications, x='yliopisto', y='lkm', color='JUFO-class', title='Publications')
    fig_publications.update_xaxes(title='')
    fig_publications.update_yaxes(title='')
    #fig7
    filtered_cfeedback = career_feedback[career_feedback['tilastovuosi'].between(years[0], years[1])]
    filtered_cfeedback = filtered_cfeedback[filtered_cfeedback.yliopisto.isin(universities)]
    filtered_cfeedback = filtered_cfeedback.groupby(['yliopisto', 'metric'], as_index=False).mean()
    filtered_cfeedback = filtered_cfeedback.sort_values(by=['yliopisto'], ascending=False)
    fig_cfeedback = ps.make_subplots(rows=1, cols=6, shared_xaxes=True, shared_yaxes=True, subplot_titles=("Career benefit of degree","Entrepreneurship","Interdisciplinary capability","Job challenge","Learning & thinking skills","Self-directedness"))
    cfeed_dimensions = ["Career benefit","Entrepreneurship","Interdisciplinary capability","Job challenge","Learning & thinking skills","Self-directedness"]
    for i, dim in enumerate(cfeed_dimensions, start=1):
        fig_cfeedback.add_trace(
            go.Bar(
                x = filtered_cfeedback[filtered_cfeedback['metric'] == dim].Keskiarvo,
                y = filtered_cfeedback[filtered_cfeedback['metric'] == dim].yliopisto,
                orientation='h',
                text = filtered_cfeedback[filtered_cfeedback['metric'] == dim].Keskiarvo,
                textposition='inside',
                texttemplate='%{x:.2f}'
            ),
            row=1,
            col=i
        )
    fig_cfeedback.update_layout(title_text='Career feedback (2 years after graduating)', showlegend=False, height = 120 + (50 * len(universities)))
    for i in fig_cfeedback['layout']['annotations']:
        i['font'] = dict(size=12, color='#000000')
    return  fig_degrees, fig_sfeedback, fig_publications, fig_cfeedback, fig_employment


if __name__ == '__main__':
    app.run_server(debug=True)
