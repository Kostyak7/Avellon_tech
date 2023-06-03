import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Загружаем данные из csv-файла
wind_data = pd.read_csv('wind_data.csv')

# Создаем приложение Dash
app = dash.Dash(__name__)

# Добавляем ползунок
app.layout = html.Div([
    html.H3("Выберите индекс:"),
    dcc.Slider(
        id='index-slider',
        min=0,
        max=len(wind_data)-1,
        step=1,
        value=len(wind_data)-1,
        marks={i: str(i) for i in range(len(wind_data))},
    ),
    dcc.Graph(
        id='wind-rose',
    )
])

# Обновляем график в зависимости от значения ползунка
@app.callback(
    dash.dependencies.Output('wind-rose', 'figure'),
    [dash.dependencies.Input('index-slider', 'value')])
def update_figure(selected_index):
    # Выбираем значения скоростей ветра для данного индекса
    A = wind_data.iloc[selected_index]["A"]
    B = wind_data.iloc[selected_index]["B"]
    C = wind_data.iloc[selected_index]["C"]
    D = wind_data.iloc[selected_index]["D"]

    # Создаем розы ветров для каждого направления
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=[A]*5,
        theta=[0, 72, 144, 216, 288],
        name='Датчик A',
        marker_color='rgb(106,81,163)',
        marker_line_color='rgb(106,81,163)',
        opacity=0.7
    ))
    fig.add_trace(go.Barpolar(
        r=[B]*5,
        theta=[18, 90, 162, 234, 306],
        name='Датчик B',
        marker_color='rgb(202,178,214)',
        marker_line_color='rgb(202,178,214)',
        opacity=0.7
    ))
    fig.add_trace(go.Barpolar(
        r=[C]*5,
        theta=[36, 108, 180, 252, 324],
        name='Датчик C',
        marker_color='rgb(251,128,114)',
        marker_line_color='rgb(251,128,114)',
        opacity=0.7
    ))
    fig.add_trace(go.Barpolar(
        r=[D]*5,
        theta=[54, 126, 198, 270, 342],
        name='Датчик D',
        marker_color='rgb(255,237,111)',
        marker_line_color='rgb(255,237,111)',
        opacity=0.7
    ))

    # Устанавливаем параметры легенды и макета
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([A,B,C,D])+2]
            ),
        ),
        showlegend=True,
        legend=dict(
            x=0.1,
            y=1.1,
            orientation='h'
        )
    )
    fig.update_traces(
        hoverinfo="all",
        hovertemplate="Значение максимума амплитуды: %{r}<br>Направление: %{theta}°<extra></extra>",
    )
    fig.update_polars(bgcolor='rgb(223, 223, 223)')

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)