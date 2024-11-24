from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd
import json 

app_ui = ui.page_fluid(
    ui.panel_title("Top 10 Alerts by Type & Subtype"),
    ui.input_select(id="type_subtype", label='Choose a Type-Subtype',
                    choices=[]),
    output_widget("chicago_map")
)


def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("../top_alerts_map.csv")

    @reactive.calc
    def subsetted_data():
        df = full_data()
        return df[df['type-subtype'] == input.type_subtype()]

    @render_altair
    def chicago_map():
        df = subsetted_data()
        file_path = "../chicago-boundaries.geojson"
    
        with open(file_path) as f:
             chicago_geojson = json.load(f)
             
        geo_data = alt.Data(values=chicago_geojson["features"])

        background = alt.Chart(geo_data).mark_geoshape(
            fill='lightgrey',stroke='white'
            ).project(type='equirectangular'
                      ).properties(
                width=500, height=300)
        

        points = alt.Chart(df).mark_circle(size=15).encode(
            longitude='lon_bin:Q',
            latitude='lat_bin:Q',
            tooltip=['lon_bin:Q', 'lat_bin:Q']
            ).project(type='equirectangular').properties(
                width=500,height=300)

        layered_chart = background + points

        return layered_chart

    @reactive.effect
    def update_dropdown():
        df = full_data()
        types_list = df['type-subtype'].unique().tolist()
        types_list = sorted(types_list)
        ui.update_select("type_subtype", choices=types_list)


app = App(app_ui, server)
