import pandas as pd
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import numpy as np

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

erlt_df_2014b_3 = pd.read_csv("data/running_mvs_2014b_3.csv", index_col=0)
rename_map = {
    "moves": "MOVES",
    "District": "District",
    "year_id": "Year",
    "month": "Month",
    "day": "Day",
    "hour_id": "Hour",
    "road_desc": "Road Description",
    "source_type_name": "Source Type",
    "fuel_type_desc": "Fuel Type",
    "pollutant_short_name": "Pollutant",
    "avg_bin_speed": "Average Speed (mph)",
    "avg_speed_bin_desc": "Average Speed Bin Description",
    "per_diff": "Percent Change in MOVES 3 Emissions",
    "rate_per_distance": "Running Emission Rate (grams/mile)",
}
erlt_df_2014b_3_1 = erlt_df_2014b_3.rename(columns=rename_map).filter(
    items=rename_map.values()
)

sut_label_value = [
    {"label": sut, "value": sut} for sut in erlt_df_2014b_3_1["Source Type"].unique()
]

fuel_label_value = [
    {"label": fuel_ty, "value": fuel_ty}
    for fuel_ty in erlt_df_2014b_3_1["Fuel Type"].unique()
]

pollutants_label_value = [
    {"label": pollutant, "value": pollutant}
    for pollutant in erlt_df_2014b_3_1.Pollutant.unique()
]

avgspeed_values = erlt_df_2014b_3_1["Average Speed (mph)"].unique()
avgspeed_values_marks_dict = {
    int(avg_speed) if avg_speed % 1 == 0 else avg_speed: f"{avg_speed}"
    for avg_speed in avgspeed_values
    if avg_speed % 5 == 0
}
avgspeed_values_marks_dict[2.5] = "2.5"
min_avgspeed = min(avgspeed_values)
max_avgspeed = max(avgspeed_values)

year_values = erlt_df_2014b_3_1["Year"].unique()

year_label_dict = [
    {"label": year, "value": year} for year in erlt_df_2014b_3_1.Year.unique()
]

app.layout = html.Div(
    [
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="eight columns",
                    children=[
                        html.H1(
                            "MOVES 2014b vs. MOVES 3 Running Emission "
                            "Comparison for El Paso"
                        ),
                        dcc.Dropdown(
                            id="pollutant-dropdown",
                            options=pollutants_label_value,
                            value="CO",
                            multi=False,
                        ),
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="four columns",
                                    children=[
                                        dcc.RadioItems(
                                            id="sut-radio",
                                            options=sut_label_value,
                                            value="Passenger Car",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="four columns",
                                    children=[
                                        dcc.RadioItems(
                                            id="fuel-radio",
                                            options=fuel_label_value,
                                            value="Gasoline",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        dcc.Graph(id="erlt_comp_line"),
                        html.P("Select Analysis Year"),
                        dcc.RadioItems(
                            id="year-radio",
                            options=year_label_dict,
                            value=2020,
                            labelStyle={"display": "inline-block"},
                        ),
                    ],
                )
            ],
        )
    ]
)


@app.callback(Output("fuel-radio", "options"), Input("sut-radio", "value"))
def set_fuel_options(selected_sut):
    fuel_sut_type_comb = (
        erlt_df_2014b_3_1[["Fuel Type", "Source Type"]]
        .drop_duplicates()
        .set_index("Source Type")
    )
    return [
        {"label": i, "value": i}
        for i in np.ravel(fuel_sut_type_comb.loc[selected_sut].values)
    ]


@app.callback(Output("fuel-radio", "value"), Input("fuel-radio", "options"))
def set_fuel_value(available_options):
    return available_options[0]["value"]


@app.callback(
    Output("erlt_comp_line", "figure"),
    [
        Input("sut-radio", "value"),
        Input("fuel-radio", "value"),
        Input("pollutant-dropdown", "value"),
        Input("year-radio", "value"),
    ],
)
def update_line_chart(sut_val, fuel_val, pollutant_val, year_val):
    max_em = erlt_df_2014b_3_1.loc[
        lambda df: (df.Pollutant == pollutant_val), "Running Emission Rate (grams/mile)"
    ].values.max()

    min_em = 0

    erlt_df_2014_2014b_1_fil = erlt_df_2014b_3_1.loc[
        lambda df: (
            (df["Source Type"] == sut_val)
            & (df["Fuel Type"] == fuel_val)
            & (df.Pollutant == pollutant_val)
            & (df["Year"] == year_val)
        )
    ].assign(Year=lambda df: df.Year.astype(int))
    fig = px.line(
        data_frame=erlt_df_2014_2014b_1_fil,
        x="Average Speed (mph)",
        y="Running Emission Rate (grams/mile)",
        hover_data=rename_map.values(),
        line_dash="MOVES",
        color="MOVES",
        facet_col="Road Description",
        facet_col_wrap=2,
        template="plotly",
    )

    fig.update_layout(
        font=dict(family="Time New Roman", size=18, color="black"),
        yaxis=dict(
            range=(min_em, max_em * 1.2),
            showexponent="all",
            exponentformat="e",
            title_text="",
        ),
        xaxis=dict(
            range=(0, 80), showexponent="all", exponentformat="e", title_text=""
        ),
        yaxis3=dict(showexponent="all", exponentformat="e", title_text=""),
        xaxis2=dict(showexponent="all", exponentformat="e", title_text=""),
        hoverlabel=dict(font_size=14, font_family="Rockwell"),
    )
    fig.add_annotation(
        {
            "showarrow": False,
            "text": "Average Speed (mph)",
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "y": 0,
            "yanchor": "top",
            "yref": "paper",
            "yshift": -30,
        }
    )
    fig.add_annotation(
        {
            "showarrow": False,
            "text": "Running Emission Rates (grams/mile)",
            "textangle": 270,
            "x": 0,
            "xanchor": "left",
            "xref": "paper",
            "y": 0.5,
            "yanchor": "middle",
            "yref": "paper",
            "xshift": -80,
        }
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
