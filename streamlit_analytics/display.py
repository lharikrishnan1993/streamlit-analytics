"""
Displays the analytics results within streamlit.
"""

import streamlit as st
import altair as alt
import pandas as pd
import streamlit_metrics as st_metrics

from . import utils


def show_results(counts, unsafe_password=None):
    """Show analytics results in streamlit, asking for password if given."""

    # Show header.
    st.title("Analytics")
    st.markdown(
        """
        Psst! 👀 You found a secret section generated by 
        [streamlit-analytics](https://github.com/jrieke/streamlit-analytics). 
        If you didn't mean to go here, remove `?analytics=on` from the URL.
        """
    )

    # Ask for password if one was given.
    show = True
    if unsafe_password is not None:
        password_input = st.text_input(
            "Enter password to show results", type="password"
        )
        if password_input != unsafe_password:
            show = False
            if len(password_input) > 0:
                st.write("Nope, that's not correct ☝️")

    if show:
        # Show traffic.
        st.header("Traffic")
        st.write(f"since {counts['start_time']:%d %b %Y, %H:%M:%S}")
        st.write(
            f"""
            <sup>pageview = user (re-)loads site; 
            script run = streamlit re-runs upon changes; 
            time spent = from page load to last widget interaction (summed across users)</sup>
            """,
            unsafe_allow_html=True,
        )
        st_metrics.metric_row(
            {
                "Pageviews": counts["total_pageviews"],
                "Script runs": counts["total_script_runs"],
                "Time spent": utils.format_seconds(counts["total_time_seconds"]),
            }
        )

        # Total: {counts['total_pageviews']} pageviews, {counts['total_script_runs']} script runs
        # <br>

        # st.header("Traffic per day")
        # Plot altair chart with pageviews and script runs.
        df = pd.DataFrame(counts["per_day"])
        base = alt.Chart(df).encode(
            x=alt.X("monthdate(days):O", axis=alt.Axis(title="", grid=True))
        )
        line1 = base.mark_line(point=True, stroke="#5276A7").encode(
            alt.Y(
                "pageviews:Q",
                axis=alt.Axis(
                    titleColor="#5276A7",
                    tickColor="#5276A7",
                    labelColor="#5276A7",
                    format=".0f",
                    tickMinStep=1,
                ),
                scale=alt.Scale(domain=(0, df["pageviews"].max() + 1)),
            )
        )
        line2 = base.mark_line(point=True, stroke="#57A44C").encode(
            alt.Y(
                "script_runs:Q",
                axis=alt.Axis(
                    title="script runs",
                    titleColor="#57A44C",
                    tickColor="#57A44C",
                    labelColor="#57A44C",
                    format=".0f",
                    tickMinStep=1,
                ),
            )
        )
        layer = (
            alt.layer(line1, line2)
            .resolve_scale(y="independent")
            .configure_axis(titleFontSize=15, labelFontSize=12, titlePadding=10)
        )
        st.altair_chart(layer, use_container_width=True)

        # Show widget interactions.
        st.header("Widget interactions")
        st.markdown(
            """
            Numbers represent user interactions, e.g. how often a button was 
            clicked, how often a specific text input was given, ...
            <br>
            <sub>Note: Numbers only increase if the state of the widget
            changes, not every time streamlit runs the script.</sub>
            """,
            unsafe_allow_html=True,
        )
        st.write(counts["widgets"])

