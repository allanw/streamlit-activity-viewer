import base64

import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

import strava
from pandas.api.types import is_numeric_dtype

st.title = "Run With Al"

st.markdown(
    """
    # Run With Al
    """
)

strava_auth = {'access_token': '6be10feca5935c51c1550559344a9cbf4c850393'}

if strava_auth is None:
    st.markdown("Click the \"Connect with Strava\" button at the top to login with your Strava account and get started.")
    st.image(
        "https://files.gssns.io/public/streamlit-activity-viewer-demo.gif",
        caption="Streamlit Activity Viewer demo",
        use_column_width="always",
    )
    st.stop()


activity = strava.select_strava_activity(strava_auth)
data = strava.download_activity(activity, strava_auth)

query_params = st.experimental_get_query_params()

st.markdown(query_params)


csv = data.to_csv()
csv_as_base64 = base64.b64encode(csv.encode()).decode()
st.markdown(
    (
        f"<a "
        f"href=\"data:application/octet-stream;base64,{csv_as_base64}\" "
        f"download=\"{activity['id']}.csv\" "
        f"style=\"color:{strava.STRAVA_ORANGE};\""
        f">Download activity as csv file</a>"
    ),
    unsafe_allow_html=True
)


columns = []
for column in data.columns:
    if is_numeric_dtype(data[column]):
        columns.append(column)

selected_columns = st.multiselect(
    label="Select columns to plot",
    options=columns
)

data["index"] = data.index

if selected_columns:
    for column in selected_columns:
        altair_chart = alt.Chart(data).mark_line(color=strava.STRAVA_ORANGE).encode(
            x="index:T",
            y=f"{column}:Q",
        )
        st.altair_chart(altair_chart, use_container_width=True)
else:
    st.write("No column(s) selected")

map_data = data[['latitude', 'longitude']]

st.map(map_data)
