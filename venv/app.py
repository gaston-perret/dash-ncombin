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

#df = pd.read_csv('covid19 updated.csv')
connection = pyodbc.connect("Driver={SQL Server};"
                            "Server=18.230.114.111;"
                            "Database=EnfasisPreRegistro_Prod;"
                            "Uid=enfasis;"
                            "Pwd={enfasisLive2020!};"
                            "autocommit = True")


cursor = connection.cursor()
#rows = cursor.execute("Select * from dbo.tbl_PreRegistro").fetchall()

df = pd.read_sql_query("Select * from dbo.tbl_PreRegistro", connection)
df2 = pd.read_sql_query("Select * from dbo.tbl_PreRegistroPortal", connection)
del_col = ['PaginaWeb', 'IdCargo', 'IdArea', 'IdSector', 'IdGiro', 'Custom1', 'PaginaWeb', 
'PaginaWeb', 'Custom2','Custom3','Custom4','Custom5','IdCiudad','IdColonia',
'CodigoPostal','CalleNombre','CalleNumero','PreCargado','ZohoSync','WelcomeMail','Categoria']
df_table = df.copy()
df_table.drop(del_col, inplace=True, axis=1)
df_table = df_table.loc[df_table['IdEvento'] == 2]

#df2.rename(columns={'IdUsuario': 'Id'}, inplace = True)


# rename columns
""" df.rename(columns={'Intensive Care Unit (ICU)': 'Intensive Care Unit',
                   'General Wards MOH report': 'General wards',
                   'In Isolation MOH report': 'In Isolation',
                   'Total Completed Isolation MOH report': 'Total completed isolation',
                   'Total Hospital Discharged MOH report': 'Total discharged from hospital',
                   'Local cases residing in dorms MOH report': 'Local cases residing in dorms',
                   'Local cases not residing in doms MOH report': 'Local cases not residing in dorms'},inplace=True) """

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
        id='covid_period',
        options=[
            {'label': 'Learn & Connects', 'value': '1'},
            {'label': 'Learn & Connect', 'value': '2'},
            {'label': 'Learn & Connect', 'value': '3'}
        ],
        value='2',
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
        columns=[{"name": i, "id": i} for i in df_table.loc[df_table['IdEvento'] == 2].columns],
        data=df_table.to_dict('records'),
        style_table={'overflowX': 'scroll'},
        style_cell = {
                'font_color': 'blue',
                'font_size': '14px',
                'text_align': 'left'
            },
        style_cell_conditional=
            [{'if': {'column_id': 'Id'},
            'width': '130px', 'text_align': 'center'}]
    )

    ])

])


# allow for easy sieving of data to see how the situation has changed
# can observe whether government measures are effective in reducing the number of cases
@app.callback(Output('graph_by_period', 'figure'),
              [Input('covid_period', 'value')])

def update_graph(covid_period_name):
    # not sure why this doesn't work, Daily Confirmed is an invalid key
    #col = ['Daily Imported', 'Daily Local transmission']

    print(covid_period_name)
    df_lc = pd.merge(df, df2, left_on='Id', right_on='IdUsuario')
    df_lc = df_lc.loc[df_lc['IdEvento'] == 2]

    #print (df2)
    print (df_lc)
    container = "Datos sobre el evento: {}".format(covid_period_name)
    df_lc2 = df_lc.copy()
    df_lc2 = (pd.to_datetime(df_lc2['FechaCreacion'])
    .dt.floor('d')
    .value_counts()
    .rename_axis('date')
    .reset_index(name='count'))
    #df_lc2 = df_lc2[df_lc2['idEvento'] == covid_period_name]

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
[dash.dependencies.Input('covid_period', 'value')])


def update_output(value):
    df_sum = pd.merge(df, df2, left_on='Id', right_on='IdUsuario')
    df_sum = df_sum.loc[df_sum['IdEvento'] == 2]
    return str(len(df_sum.index))


if __name__ == '__main__':
    app.run_server(debug=True)