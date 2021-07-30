import base64
import os

import arrow
import httpx
import streamlit as st
import sweat
from bokeh.models.widgets import Div


APP_URL = "streamlit-activity-viewer.localhost"
STRAVA_CLIENT_ID = '7786'
STRAVA_CLIENT_SECRET = "76f530eae935449fdb9a57dcc01fb4866e88c732"
STRAVA_AUTHORIZATION_URL = "https://www.strava.com/oauth/authorize"
STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
DEFAULT_ACTIVITY_LABEL = "NO_ACTIVITY_SELECTED"
STRAVA_ORANGE = "#fc4c02"



def authorization_url():
    request = httpx.Request(
        method="GET",
        url=STRAVA_AUTHORIZATION_URL,
        params={
            "client_id": "7786",
            "redirect_uri": APP_URL,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": "activity:read_all"
        }
    )

    return request.url



def logged_in_title(strava_auth, header=None):
    if header is None:
        base = st
    else:
        col, _, _, _ = header
        base = col

    first_name = strava_auth["athlete"]["firstname"]
    last_name = strava_auth["athlete"]["lastname"]
    col.markdown(f"*Welcome, {first_name} {last_name}!*")





def get_activities(auth, page=1):
    access_token = auth["access_token"]
    response = httpx.get(
        url=f"{STRAVA_API_BASE_URL}/athlete/activities",
        params={
            "page": page,
        },
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.json()


def activity_label(activity):
    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        return ""

    start_date = activity.get("start_date_local")
    if start_date:
        start_date = arrow.get(start_date)
        human_readable_date = start_date.humanize(granularity=["day"])
        date_string = start_date.format("YYYY-MM-DD")
    else:
        date_string = 'none'
        human_readable_date = 'none'

    if not activity.get("name"):
        activity_name = "test"
    else:
        activity_name = activity.get("name")

    return f"{activity_name} - {date_string} ({human_readable_date})"


def select_strava_activity(auth):
    col1, col2 = st.beta_columns([1, 3])
    with col1:
        page = st.number_input(
            label="Activities page",
            min_value=1,
            help="The Strava API returns your activities in chunks of 30. Increment this field to go to the next page.",
        )

    with col2:
        activities = get_activities(auth=auth, page=page)
        if not activities:
            st.info("This Strava account has no activities or you ran out of pages.")
            st.stop()
        default_activity = {"name": DEFAULT_ACTIVITY_LABEL, "start_date_local": ""}

        activity = st.selectbox(
            label="Select an activity",
            options=[default_activity] + activities,
            format_func=activity_label,
        )

    if activity["name"] == DEFAULT_ACTIVITY_LABEL:
        st.write("No activity selected")
        st.stop()
        return

    activity_url = f"https://www.strava.com/activities/{activity['id']}"
        
    st.markdown(
        f"<a href=\"{activity_url}\" style=\"color:{STRAVA_ORANGE};\">View on Strava</a>",
        unsafe_allow_html=True
    )


    return activity


@st.cache(show_spinner=False, max_entries=30, allow_output_mutation=True)
def download_activity(activity, strava_auth):
    with st.spinner(f"Downloading activity \"{activity['name']}\"..."):
        return sweat.read_strava(activity["id"], strava_auth["access_token"])
