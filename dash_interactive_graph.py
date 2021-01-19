# -*- coding: utf-8 -*-
# Импортируем библиотеки
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

#Импортируем стили
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Получаем файл с данными
df = pd.read_csv('games.csv')

#Приводим названия колонок к нижнему регистру
df.columns = df.columns.str.lower()

#Переводим колонки с числовыми данными к нужному формату, удаляя возникающие ошибки
df['user_score'] = pd.to_numeric(df['user_score'], errors='coerce')
df['critic_score'] = pd.to_numeric(df['critic_score'], errors='coerce')
df['year_of_release'] = pd.to_numeric(df['year_of_release'], errors='coerce')

#Исключаем игры, выпущенные до 2000 года
df = df[df['year_of_release'] > 1999]

#Исключаем оставшиеся строки с пропусками
df.dropna(axis=0, how='any', inplace=True)

#Создаем pivot table для второго графика
df1 = df.pivot_table(index = ['platform', 'year_of_release'], values='name', aggfunc='count').reset_index() 

app.layout = html.Div([
    html.H2(children='История игровой индустрии'),
    html.Div(children='''
        Ниже представлены графики изменения игровой индустрии в зависимости от жанра, рейтинга, года выпуска игр.  Вы увидите тренды выпуска игр на разных платформах в разные годы по выбранным жанрам и рейтингу. В самом низу вы можете выбрать интересующий вас год.
    '''),
    html.Br(),
        html.Div([
            html.Label("Всего игр выпущено в выбранном году:", style={"font-weight": "bold"}),
            html.Div(id='counter'),
            html.Div([
            dcc.Graph(
                id='stacked_area_plot'
                    ),
            dcc.Graph(
                id='scatter_plot'
                    )
            ], 
                style={'columnCount': 2, 'display': 'flex'}),
            html.Div([
            dcc.Slider(
                id='year-slider',
                min=df['year_of_release'].min(),
                max=df['year_of_release'].max(),
                value=df['year_of_release'].min(),
                marks={i: str(i) for i in range(2000, 2017)},
                step=None)],
                style={'width': '50%'}
                    ),
            html.Br()
            ])
@app.callback(
    Output('counter', 'children'),
    Output('scatter_plot', 'figure'),
    Output('stacked_area_plot', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df[df['year_of_release'] == selected_year]
    
    counter = len(filtered_df)
    
    fig1 = px.scatter(filtered_df, x="user_score", y="critic_score",  color="genre", labels={
                     "user_score": "Оценка пользователей",
                     "critic_score": "Оценка критиков",
                     "genre": "Жанр"
                     },
                     title= "Игры по жанрам")
    fig1.update_layout(transition_duration=500)

    filtered_df1 = filtered_df.pivot_table(index = 'platform', values='name', aggfunc='count').reset_index() 
    fig2 = px.area(filtered_df1, y='name', color="platform", labels={
                     "name": "Количество игр",
                     "index": "Актуальные платформы в выбранном году",
                     "platform": "Платформа",
                     },
                     title= "Игры по платформам")
    fig2.update_layout(transition_duration=500)

    return counter, fig1, fig2

#Запускаем приложение
if __name__ == '__main__':
    app.run_server(debug=True)
