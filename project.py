import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash_auth
import json
import plotly.graph_objs as go
from io import BytesIO
from wordcloud import WordCloud
import base64
import pandas as pd


encode_service = ['Bloc Commun', 'Brules', 'CCV', 'CMCA','Chir Pediatrique',
                    'Chir Tho', 'Gynecologie', 'NeuroChirurgie', 'NeuroRadiologie',
                    'ORL', 'Obstetrique','Ophtalmologie', 'Specialites Salengro',
                    'Traumatologie', 'Urgences']
intervention = pd.read_csv('intervention.csv',sep=',' ,encoding='ISO-8859-1')
annual_df = pd.read_csv('annual_data.csv', sep=',',encoding='ISO-8859-1' )
df_deces = pd.read_csv('deces.csv', sep=',', encoding='ISO-8859-1')
urgence = pd.read_csv('urgence.csv', sep=',', encoding='latin-1')
entUrgence = pd.read_csv('entree_urgences.csv', sep=',', encoding='latin-1')
lib_chap_df = pd.read_csv('lib_chap_text.csv', sep=',', encoding='ISO-8859-1')
lib_chap_df['SERVICE'] = encode_service
df_taille = pd.read_csv('df_taille_poid.csv', sep=',',encoding='ISO-8859-1')
var = ['Deces', 'Entree_urgences', 'Intervention']
mots = ""
for mot in lib_chap_df['LIB_CHAPITRE_TEXT'].dropna():
    mots = mots + mot
mots = ''.join(mots)

trace1 = go.Bar(
    x=entUrgence['SERVICE'],  # NOC stands for National Olympic Committee
    y=entUrgence['N_ENTREE_URGENCES'],
    name = 'ENTREE URGENCES',
    marker=dict(color='#FFD700'), # set the marker color to gold
    hoverinfo='y'
)
trace2 = go.Bar(
    x=intervention ['SERVICE'],
    y=intervention ['INTERVENTION_COUNT'],
    name='INTERVENTION',
    marker=dict(color='#9EA0A1'), # set the marker color to silver
    hoverinfo='y'
)

data = [trace1, trace2]
layout = go.Layout(
    title='Interventions passees par urgences',
    barmode='group'
)


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div(
    [
        dcc.Tabs(id="tabs-example",
                value='tab-1-example',
                children=[
                dcc.Tab(label='Hover Data',
                        value='tab-1-example',
                        children =[
                            dbc.Row(
                                [dbc.Col(
                                    html.Div([
                                        html.H5(children ='Hover on the bars to see the lib chapters', style=dict(marginLeft=20)),
                                        dcc.Graph(
                                            id='interv-per-serv',
                                            figure={
                                                'data': [
                                                    go.Bar(
                                                        x = intervention['SERVICE'],
                                                        y = intervention['INTERVENTION_COUNT']
                                                    )],
                                                'layout': go.Layout(
                                                    title = 'Intervention per service',
                                                    #xaxis = {'title': 'Service'},
                                                    yaxis = {'title': 'Number of Intervention'},
                                                    hovermode='closest'
                                                )})])
                                ),
                                dbc.Col(
                                    html.Div([
                                        dcc.Graph(
                                            id='Stack Bar',
                                            figure={
                                                'data': data,
                                                'layout': layout
                                            })]))]),
                            dbc.Row(dbc.Col(
                                    html.Div([
                                        html.H4('LIB CHAPTER OF SERVICE', style={'marginLeft':30}),
                                        dcc.Markdown(id='hover-data', style={'marginLeft':30} )
                                    ]), width=5))]
            ),
            dcc.Tab(label='Compare Services by variables',
                    value='tab-2-example',
                    children=[
                        # dbc.Row(
                        #     [dbc.Col(
                        #         html.Div([
                        #             html.P(),
                        #             html.H4('Choose a service'),
                        #             dcc.Dropdown(
                        #                 id='service',
                        #                 options=[{'label': i, 'value': i} for i in encode_service],
                        #                 value='CCV'
                        #             )
                        #         ]), width=3),
                        # ]),
                        html.P(),
                        html.P(),
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    html.P(),
                                    html.H4('Select a variable to visualize', style=dict(marginLeft=60)),
                                    dcc.RadioItems(
                                        id='variable',
                                        options=[{'label': i, 'value': i} for i in var],
                                        value='Deces',
                                        style=dict(display='inline-block',
                                                    marginLeft=60
                                                    )
                                    ),
                                    html.Div([
                                        dcc.Graph(id='bar-plot')
                                    ])
                                ]), width=3),
                        ])
                    ]),
            dcc.Tab(label='Scatterplot and Bubble chart',
                    value='tab-3-example',
                    children=[
                        dbc.Row([dbc.Col(
                                html.Div([
                                    html.H5('Select data to download', style=dict(marginLeft=20,marginTop=20)),
                                    dcc.Graph(
                                        id='hgt-wgt-plot',
                                        style = dict(width='80%'),
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x = df_taille['TAILLE'],
                                                    y = df_taille['POIDS'],
                                                    dy = 1,
                                                    mode = 'markers',
                                                    marker = {
                                                        'size': 12,
                                                        'color': 'rgb(51,204,153)'
                                                        })],
                                            'layout': go.Layout(
                                                title = 'Height vs Weight Scatterplot',
                                                xaxis = {'title': 'Height'},
                                                yaxis = {'title': 'Weight','nticks':3},
                                                hovermode='closest'
                                            )}),
                                    html.Button(
                                        id='submit-button',
                                        n_clicks=0,
                                        children='Download Selected data',
                                        style={'fontSize':15, 'marginLeft':30}
                                        ),
                                    html.Pre(id='density', style={'paddingTop':25})
                                ])),
                                dbc.Col(
                                    html.Div([
                                        dcc.Graph(
                                            id='bubble-plot',
                                            #style=dict(width='80%', margineTop = 50),
                                            figure = dict(
                                                data = [go.Scatter(
                                                            x=annual_df['N_URGENCES'],
                                                            y=annual_df['REA_POST_OP'],
                                                            dx = 1,
                                                            text=annual_df['SERVICE'],  # use the new column for the hover text
                                                            mode='markers',
                                                            marker=dict(size=1.2*annual_df['N_LIB_CHAP'])
                                            )],
                                                layout = go.Layout(
                                                            title='Number of N_URGENCES vs REA_POST_OP per service',
                                                            hovermode='closest',
                                                            xaxis=dict(title='N_URGENCES'),
                                                            yaxis=dict(title='REA_POST_OP')
                                                )
                                        )
                                        )])
                                )
                        ])
                    ]),
            dcc.Tab(label='Lib Chapter Word Cloud',
                    value='tab-4-example',
                    children=[
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    html.H4('Select Service', style={'marginLeft':10}),
                                    dcc.Dropdown(
                                        id='service_word',
                                        options=[{'label': i, 'value': i} for i in encode_service],
                                        value='CCV',
                                        style={'marginLeft':5, 'width':'70%'}
                                    ),
                                    html.H5('Word Cloud of Service',style={'margin':10, 'display':'right'} ),
                                    html.Img(id='image_wc', style={'margin':10, 'display':'inline-block','width':'50%' })
                                ]), width=5),
                            ])
                    ]),
            dcc.Tab(label='Data Table',
                    value='tab-5-example',
                    children=[
                        html.Div([
                            dash_table.DataTable(
                                id='data-table',
                                columns=[{"name": i, "id": i} for i in annual_df.columns],
                                data=annual_df.to_dict('records'),
                        )])
                    ]
            )
        ]),

        html.Div(id='tabs-content-example')
    ]
)



def plot_worldcloud(data):
    wc = WordCloud(background_color='black', width=300, height=300).generate(data)
    return wc.to_image()

@app.callback(Output('image_wc', 'src'),
             [Input('service_word', 'value')])
def make_image(service):
    mots = lib_chap_df[lib_chap_df['SERVICE']=='CCV']['LIB_CHAPITRE_TEXT']
    mots = ''.join(mots)
    img = BytesIO()
    plot_worldcloud(data=mots).save(img,format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(
    Output(component_id='bar-plot', component_property='figure'),
    [Input(component_id='variable',component_property='value')]
)
def plot_bar(variable):
    if variable == 'Deces':
        fig={
            'data': [
                go.Bar(
                    x = intervention['SERVICE'],
                    y = df_deces['N_DECES']
                )],
            'layout': go.Layout(
                title = 'Death per service',
                #xaxis = {'title': 'Service'},
                yaxis = {'title': 'Number of death'},
                hovermode='closest'
            )}
    elif variable == 'Intervention':
        fig={
            'data': [
                go.Bar(
                    x = intervention['SERVICE'],
                    y = intervention['INTERVENTION_COUNT']
                )],
            'layout': go.Layout(
                title = 'Intervention per service',
                #xaxis = {'title': 'Service'},
                yaxis = {'title': 'Number of Intervention'},
                hovermode='closest'
            )}
    elif variable == 'Entree_urgences':
        fig={
            'data': [
                go.Bar(
                    x = intervention['SERVICE'],
                    y=entUrgence['N_ENTREE_URGENCES'],
                    name = 'ENTREE URGENCES',
                    marker=dict(color='#FFD700'), # set the marker color to gold
                    hoverinfo='y'
                )],
            'layout': go.Layout(
                title = 'Entrees par les urgence per service',
                #xaxis = {'title': 'Service'},
                yaxis = {'title': 'Nombre entree par les urgences'},
                hovermode='closest'
            )}



    return fig
def download_status():
    return 'Download Complete'

@app.callback(
    Output('density', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('hgt-wgt-plot', 'selectedData')]
)
def return_json(n_clicks, selectedData):
    try:
        if (n_clicks >0 ):
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(selectedData, f, ensure_ascii=False, indent=2)
            #return json.dumps(selectedData, indent=2)
            return download_status()
    except Exception as e:
        return 'Error {} occured'.format(e)

@app.callback(
    Output(component_id='hover-data', component_property='children'),
    [Input(component_id='interv-per-serv', component_property='hoverData')])
def load_lib_chapter(hoverData):
    try:
        service = hoverData['points'][0]['x']
        lib_text = lib_chap_df[lib_chap_df['SERVICE']==service]['LIB_CHAPITRE_TEXT']
        return lib_text
    except Exception as e:
        return "No data to display"



if __name__ == "__main__":
    app.run_server(debug=True)
