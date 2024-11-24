from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import altair as alt
import pandas as pd
import json 

app_ui = ui.page_fluid(
    ui.panel_title("Top 10 Alerts of Each Type by Hour or Hour Range"),
    ui.input_select(id="type_subtype", label='Choose a Type-Subtype',
                    choices=[]),
    ui.input_switch(id="switch_button",
                    label = 'Toggle to switch to range of hours',
                    value=False),
    ui.panel_conditional(
        "!input.switch_button",
        ui.input_slider(id="hour_chooser", 
                    label = 'Choose an hour of the day',
                    min=0, max=23, value=12, step=1),
        output_widget("chicago_map_single_hour")
    ),
    ui.panel_conditional(
        "input.switch_button",
        ui.input_slider(id="range_slider", 
                    label = 'Select Hour Range',
                    min=0, max=23, value=[6,9], step=1),
        output_widget("chicago_map_hour_range")
    )
)

def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("/Users/katherinetu/Desktop/Pset6/top_alerts_map_byhour/top_alerts_map_byhour.csv")

    @reactive.calc
    def subsetted_data_type():
        df = full_data()
        return df[df['type-subtype'] == input.type_subtype()]
    
    @reactive.calc
    def subsetted_data_hour():
        df = subsetted_data_type()
        hour = f"{input.hour_chooser():02}:00"
        return df[df['hour'] == hour]

    @reactive.calc
    def top_10_by_range():
        start_hour = f"{input.range_slider()[0]:02}:00"
        end_hour = f"{input.range_slider()[1]:02}:00"

        df = subsetted_data_type()

        filtered_df = df[(df['hour']>= start_hour) 
                            & (df['hour'] < end_hour)]

        aggregated_df = filtered_df.groupby(['lon_bin','lat_bin']
                                            ).agg({'count': 'sum'}
                                                  ).reset_index()
        
        top_10 = aggregated_df.sort_values(by='count', 
                                           ascending=False).head(10)
        
        return top_10
    
    @render_altair
    def chicago_map_hour_range():
        df = top_10_by_range()
        
        file_path = "/Users/katherinetu/Desktop/Pset6/top_alerts_map/chicago-boundaries.geojson"
    
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

    @render_altair
    def chicago_map_single_hour():
        df = subsetted_data_hour()
        
        file_path = "/Users/katherinetu/Desktop/Pset6/top_alerts_map/chicago-boundaries.geojson"
    
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
