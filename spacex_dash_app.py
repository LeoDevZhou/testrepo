# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload],
                                                marks={i: f'{i} Kg' for i in range(0, 10001, 1000)}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(success_counts, values='count', names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        
        success_counts['class'] = success_counts['class'].replace({1: 'Success', 0:  'Failure'})
        color_map = {'Success': 'green', 'Failure': 'red'}
        category_order = ['Success', 'Failure']
        
        fig = px.pie(success_counts, values='count', names='class', 
                    title=f'Success vs. Failed Launches for {selected_site}',
                    category_orders={'class': category_order},
                    color='class',
                    color_discrete_map=color_map)
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    min_payload, max_payload = payload_range
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & (spacex_df['Payload Mass (kg)'] <= max_payload)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version',
                         title='Payload vs. Outcome for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= min_payload) &
                                (spacex_df['Payload Mass (kg)'] <= max_payload)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version',
                         title=f'Payload vs. Outcome for {selected_site}',
                         labels={'class': 'Launch Outcome'})
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
