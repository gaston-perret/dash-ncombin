import plotly.graph_objects as go
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import pandas as pd

import pyodbc
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq

external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# CONNECT TO DB
""" connection = pyodbc.connect('DRIVER={SQL Server};SERVER={18.230.114.111};DATABASE={EnfasisPreRegistro_Prod};UID={enfasis};PWD={enfasisLive2020!};')
connection = pyodbc.connect('Driver={SQL Server};'
                      'Server=18.230.114.111;'
                      'PORT=1433;'
                      'Database=EnfasisPreRegistro_Prod;'
                      'UID=enfasis;'
                      'PWD={enfasisLive2020!}')"""

connection = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                      "Server=18.230.114.111;"
                      "Database=EnfasisPreRegistro_Prod;"
                      "UID=enfasis;"
                      "PWD=EnfasisLive2020!")


cursor = connection.cursor()


# DATAFRAMES
df = pd.read_sql_query("Select * from dbo.tbl_PreRegistro", connection)
df2 = pd.read_sql_query("Select * from dbo.tbl_PreRegistroPortal", connection)
del_col = ['PaginaWeb', 'IdCargo', 'IdArea', 'IdSector', 'IdGiro', 'Custom1', 'PaginaWeb', 
'PaginaWeb', 'Custom2','Custom3','Custom4','Custom5','IdCiudad','IdColonia',
'CodigoPostal','CalleNombre','CalleNumero','PreCargado','ZohoSync','WelcomeMail','Categoria']
df_merged = pd.merge(df, df2, left_on='Id', right_on='IdUsuario')
df_merged = df_merged.loc[df_merged['IdPortal'] == 2]
df_merged.drop(del_col, inplace=True, axis=1)
df_merged.drop_duplicates('Id_x', inplace = True)
""" df_table = pd.merge(df, df2, left_on='Id', right_on='IdUsuario')
df_table =df_table.loc[df_table['IdPortal'] == 2]
df_table.drop(del_col, inplace=True, axis=1) """
#df_table = df_table.loc[df_table['IdPortal'] == 2]


# LAYOUT FOR WEBSITE - HTML
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Encumex Events Analytics"), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(html.H6(children='Visualizando datos relacionados a los eventos virtuales de Encumex'), className="mb-4")
        ]),

        dbc.Row([
            dbc.Col(dbc.Card(html.H3(children='Refrescar la página para obtener datos en tiempo real',
                                     className="text-center text-light bg-dark"), body=True, color="dark")
                    , className="mb-4")
        ]),
        
        #,

    dcc.Dropdown(
        id='event_selector',
        options=[
            {'label': 'Learn & Connect', 'value': '1'},
            #{'label': 'Learn & Connect', 'value': '2'}
        ],
        value='1',
        style={'width': '48%', 'margin-left':'5px'}
        ),

    dbc.Row([
        dbc.Col(html.H5(children='Registrados ahora', className="text-center"),
            className="mt-4")
    ]),


    daq.LEDDisplay(
        id='my-LED-display',
        label=" ",
        style={'width': '100%'},
        value=0,
        size = 60,
        color="#FF5E5E"
    ),

    dbc.Row([
        dbc.Col(html.H5(children='Registrados diarios al evento', className="text-center"),
                className="mt-4")
    ]),

    dcc.Graph(id='graph_by_period',
              hoverData={}),

    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_merged.columns],
        data=df_merged.to_dict('records'),
        export_format="csv",
        style_table={'overflowX': 'scroll'},
        style_cell = {
                'font_color': 'blue',
                'font_size': '14px',
                'text_align': 'left'
            },
        style_cell_conditional=
            [{'if': {'column_id': 'Id'},
            'width': '160px', 'text_align': 'center'}]
    )

    ])

])


@app.callback(Output('graph_by_period', 'figure'),
              [Input('event_selector', 'value')])

def update_graph(event_name):
    # not sure why this doesn't work, Daily Confirmed is an invalid key
    #col = ['Daily Imported', 'Daily Local transmission']

    print(event_name)
    df_lc = df_merged
    #df_lc = df_lc.loc[df_lc['IdPortal'] == 2]

    #print (df2)
    print (df_lc)
    container = "Datos sobre el evento: {}".format(event_name)
    df_lc2 = df_lc.copy()
    df_lc2 = (pd.to_datetime(df_lc2['FechaCreacion'])
    .dt.floor('d')
    .value_counts()
    .rename_axis('date')
    .reset_index(name='count'))
    #df_lc2 = df_lc2[df_lc2['idEvento'] == event_name]

    #print (df_lc2)
    fig = px.bar(df_lc2, x=df_lc2['date'], y=df_lc2['count'])
    """ data = [go.Scatter(x=dff['date'], y=dff['count'],
                    mode='lines+markers',name='Daily confirmed')] """
    layout = go.Layout(
        yaxis={'title': "Registros"},
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        template = "seaborn",
        margin=dict(t=20)
    )
    return fig
    #return {'data': fig, 'layout': layout}


@app.callback(
dash.dependencies.Output('my-LED-display', 'value'),
[dash.dependencies.Input('event_selector', 'value')])


def update_output(value):
    df_sum = df_merged
    df_sum = df_sum.loc[df_sum['IdPortal'] == 2]
    return str(len(df_sum.index))


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', debug=True)