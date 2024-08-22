import dash
import os
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.io as pio
import io

load_dotenv()

# Construct database URL from environment variables
db_url = create_engine(
    f"{os.getenv('ENGINE')}://{os.getenv('DATABASE_USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"
)

# Query to fetch data
query = '''
SELECT
    pf.indicator_value,
    pf.gender_code,
    pf.state_code,
    pf.sector_code,
    pf.year,
    pf.status_code,
    x.gender_name as gender_description,
    i.indicator_name AS indicator_description,
    s.state_name AS state_description,
    st.status_name AS status_description,
    sec.sector_name AS sector_description
FROM
    plfs_fact AS pf
LEFT JOIN
    indicator AS i ON pf.indicator_code = i.indicator_code
LEFT JOIN
    "state" AS s ON pf.state_code = s.state_code
LEFT JOIN
    status_code AS st ON pf.status_code = st.status_code
LEFT JOIN
    sector AS sec ON pf.sector_code = sec.sector_code
LEFT JOIN
    gender AS x ON pf.gender_code = x.gender_code
'''

df = pd.read_sql_query(query, db_url)

# Define default dropdown values function
def get_default_dropdown_values():
    default_indicator = "Labour Force Participation Rate (LFPR)"
    default_state = 'All India'
    default_sector = 'Rural + Urban'
    default_gender = 'person'
    default_year = ["Select All"]
    default_status =  "Usual Status (ps+ss)"
    return default_indicator, default_state, default_sector, default_gender, default_year, default_status

# Get default dropdown values
default_indicator, default_state, default_sector, default_gender, default_year, default_status = get_default_dropdown_values()

external_stylesheets = [
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "PLFS"

app.layout = html.Div(
    className="content-wrapper",
    children=[
        # Sidebar
        html.Div(
            style={'flex': '0 1 320px', 'padding': "10px", "boxSizing": "border-box"},
            children=[
                html.H1(
                    "Select parameters to get charts",
                    className="parameter-data",
                    style={'fontSize': "15px", 'fontWeight': 'normal', 'marginBottom': '25px', "marginTop": "20px"}
                ),
                html.Div(
                    children=[
                        html.Div(children="Indicator", className="menu-title"),
                        dcc.Dropdown(
                            id="indicator-dropdown",
                            options=[{'label': i, 'value': i} for i in df['indicator_description'].unique()],
                            placeholder="Indicator",
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_indicator,
                            style={"fontSize": "10px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state-dropdown",
                            options=[{'label': i, 'value': i} for i in df['state_description'].unique()],
                            value=default_state,
                            clearable=False,
                            placeholder="State",
                            searchable=False,
                            className="dropdown",
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Sector", className="menu-title"),
                        dcc.Dropdown(
                            id="sector-dropdown",
                            options=[{'label': i, 'value': i} for i in df['sector_description'].unique()],
                            value=default_sector,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="Sector"
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Gender", className="menu-title"),
                        dcc.Dropdown(
                            id="gender-dropdown",
                            options=[{'label': i, 'value': i} for i in df['gender_description'].unique()],
                            value=default_gender,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="Gender"
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="year-container",
                    children=[
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{'label': 'Select All', 'value': 'Select All'}] + [{'label': str(year), 'value': year} for year in df['year'].unique()],
                            multi=True,
                            value=default_year,  # Multi-select default value
                            className="dropdown",
                            clearable=False,
                            searchable=False,
                            placeholder="Select Year"
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="status-container",
                    children=[
                        html.Div(children="Status", className="menu-title"),
                        dcc.Dropdown(
                            id="status-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['status_description'].unique()],
                            value=default_status,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="Status"
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Button(
                    'Apply', id='plot-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '15px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginTop': '30px',
                        'marginBottom': '0px'
                    }
                ),
                html.Button(
                    'Download', id='download-svg-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '20px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginBottom': '0px'
                    }
                ),
            ]
        ),
        # Graph area
        html.Div(
            style={'flex': '1', 'padding': '20px', 'position': 'relative', 'text-align': 'center', 'height': 'calc(100% - 50px)'},
            children=[
                dcc.Loading(
                    id="loading-graph",
                    type="circle", color='#83b944',
                    children=[
                        html.Div(
                            id='graph-container',
                            style={'width': '100%', 'height': '650px'},
                            children=[
                                html.Div(
                                    className="loader",
                                    id="loading-circle",
                                    style={"position": "absolute", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
                                ),
                                dcc.Graph(
                                    id="plot-output",
                                    config={"displayModeBar": False},
                                    style={'width': '100%', 'height': 'calc(100% - 50px)'}
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        ),
        dcc.Download(id="download"),
        # Interval component to trigger default plot
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # Interval in milliseconds
            n_intervals=0,
            max_intervals=1  # Ensure it runs only once
        )
    ]
)

# Update state dropdown based on indicator selection
@app.callback(
    Output("state-dropdown", "options"),
    [Input("indicator-dropdown", "value")]
)
def update_state_dropdown(indicator):
    filtered_df = df[df['indicator_description'] == indicator]
    states = filtered_df["state_description"].unique()
    return [{"label": state, "value": state} for state in states]

# Update sector dropdown based on indicator selection
@app.callback(
    Output("sector-dropdown", "options"),
    [Input("indicator-dropdown", "value")]
)
def update_sector_dropdown(indicator):
    filtered_df = df[df["indicator_description"] == indicator]
    sectors = filtered_df["sector_description"].unique()
    return [{"label": sector, "value": sector} for sector in sectors]

@app.callback(
    Output("gender-dropdown", "options"),
    [Input("indicator-dropdown", "value")]
)
def update_gender_dropdown(indicator):
    filtered_df = df[df['indicator_description'] == indicator]
    genders = filtered_df["gender_description"].unique()
    return [{"label": gender, "value": gender} for gender in genders]

# Update year dropdown based on indicator selection
@app.callback(
    Output("year-dropdown", "options"),
    [Input("indicator-dropdown", "value")]
)
def update_year_dropdown(indicator):
    filtered_df = df[df['indicator_description'] == indicator]
    years = filtered_df["year"].unique()
    return [{"label": 'Select All', "value": 'Select All'}] + [{'label': str(year), 'value': year} for year in years]

# Update status dropdown based on indicator selection
@app.callback(
    Output("status-dropdown", "options"),
    [Input("indicator-dropdown", "value")]
)
def update_status_dropdown(indicator):
    filtered_df = df[df['indicator_description'] == indicator]
    statuses = filtered_df["status_description"].unique()
    return [{"label": status, "value": status} for status in statuses]

# Update the plot based on selected parameters
@app.callback(
    Output("plot-output", "figure"),
    [Input('plot-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State("indicator-dropdown", "value"),
     State("state-dropdown", "value"),
     State("sector-dropdown", "value"),
     State("gender-dropdown", "value"),
     State("year-dropdown", "value"),
     State("status-dropdown", "value")]
)
def update_plot(n_clicks, n_intervals, selected_indicator, state, sector, gender, year, status):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    print(f"Triggered by: {button_id}")
    print(f"n_clicks: {n_clicks}")
    print(f"n_intervals: {n_intervals}")
    print(f"selected_indicator: {selected_indicator}")
    print(f"state: {state}")
    print(f"sector: {sector}")
    print(f"gender: {gender}")
    print(f"year: {year}")
    print(f"status: {status}")

    filtered_df = df[(df['indicator_description'] == selected_indicator) & 
                     (df["state_description"] == state) & 
                     (df['gender_description'] == gender) & 
                     (df["sector_description"] == sector) & 
                     (df['status_description'] == status)]

    # Handle "Select All" in year dropdown
    if 'Select All' in year:
        years = df["year"].unique()
    else:
        years = year

    filtered_df = filtered_df[filtered_df["year"].isin(years)]

    fig = go.Figure()

    if n_clicks > 0 or n_intervals == 1:
        fig.add_trace(go.Scatter(
            x=filtered_df["year"],
            y=filtered_df["indicator_value"],
            mode="lines+markers",
            marker=dict(size=15)
        ))
        fig.update_layout(
            xaxis={"title": "Year"},
            yaxis={"title":"Periodic Labour Force Survey"},
            hovermode="closest"
        )

    return fig

# Handle SVG download
@app.callback(
    Output("download", "data"),
    Input("download-svg-button", "n_clicks"),
    State("plot-output", "figure"),
    prevent_initial_call=True
)
def download_svg(n_clicks, figure):
    if n_clicks > 0:
        fig = go.Figure(figure)
        svg_str = pio.to_image(fig, format="svg")

        buffer = io.BytesIO()
        buffer.write(svg_str)
        buffer.seek(0)

        return dcc.send_bytes(buffer.getvalue(), "plot.svg")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False, port=4574)
