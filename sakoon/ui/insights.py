"""Insights dashboard — mood trends, streaks, activity charts."""

from __future__ import annotations

import streamlit as st

from sakoon.core.security import escape_html
from sakoon.services.insights import collect_insights, insights_ui_copy

_CHART_PRIMARY = "#0D9488"
_CHART_SECONDARY = "#38BDF8"


def render_insights_page(lang: str) -> None:
    copy = insights_ui_copy(lang)

    st.markdown(
        f'<div class="sakoon-page-hero"><h2>{escape_html(copy["title"])}</h2>'
        f'<p>{escape_html(copy["subtitle"])}</p></div>',
        unsafe_allow_html=True,
    )

    range_labels = {
        copy["range_7"]: 7,
        copy["range_30"]: 30,
        copy["range_90"]: 90,
    }
    choice = st.radio(
        "Range",
        list(range_labels.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="insights_range",
        index=1,
    )
    days = range_labels[choice]
    uid = st.session_state.get("db_user_id")
    data = collect_insights(days=days, lang=lang, user_id=uid)
    totals = data["totals"]

    st.markdown('<div class="sakoon-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(copy["stat_mood"], totals["mood_count"])
    with c2:
        avg = totals["mood_avg"]
        st.metric(copy["stat_avg"], f"{avg:.1f}/10" if avg is not None else "—")
    with c3:
        st.metric(copy["stat_journal"], totals["journal_count"])
    with c4:
        st.metric(copy["stat_sessions"], totals["session_count"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sakoon-panel">', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        ms = data["mood_streak"]
        st.metric(
            copy["streak_mood"],
            f"{ms['current']} {copy['streak_days']}",
            delta=f"{copy['streak_best']}: {ms['best']}",
        )
    with s2:
        js = data["journal_streak"]
        st.metric(
            copy["streak_journal"],
            f"{js['current']} {copy['streak_days']}",
            delta=f"{copy['streak_best']}: {js['best']}",
        )
    with s3:
        cs = data["checkin_streak"]
        st.metric(
            copy["streak_checkin"],
            f"{cs['current']} {copy['streak_days']}",
            delta=f"{copy['streak_best']}: {cs['best']}",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"### {copy['summary']}")
    st.info(data["summary"])

    mood_series = data["mood_series"]
    activity = data["activity"]

    if not mood_series and not activity:
        st.warning(copy["empty"])
        return

    st.markdown('<div class="sakoon-panel">', unsafe_allow_html=True)
    if mood_series:
        st.markdown(f"### {copy['chart_mood']}")
        try:
            import altair as alt
            import pandas as pd

            df = pd.DataFrame(mood_series)
            df["day"] = pd.to_datetime(df["day"])
            chart = (
                alt.Chart(df)
                .mark_area(line={"color": _CHART_PRIMARY}, color=_CHART_PRIMARY, opacity=0.18)
                .encode(
                    x=alt.X("day:T", title=None),
                    y=alt.Y(
                        "avg_rating:Q",
                        title=copy["mood_series"],
                        scale=alt.Scale(domain=[1, 10]),
                    ),
                    tooltip=[
                        alt.Tooltip("day:T", title="Date"),
                        alt.Tooltip("avg_rating:Q", title="Avg"),
                        alt.Tooltip("count:Q", title="Check-ins"),
                    ],
                )
                .properties(height=280)
                .configure_view(strokeWidth=0)
                .configure_axis(labelColor="#5C6B66", titleColor="#1C2422", gridColor="#E4EDEB")
            )
            points = (
                alt.Chart(df)
                .mark_circle(size=60, color=_CHART_PRIMARY)
                .encode(x="day:T", y="avg_rating:Q")
            )
            st.altair_chart(chart + points, use_container_width=True)
        except Exception:
            chart_data = {row["day"]: row["avg_rating"] for row in mood_series}
            st.line_chart(chart_data, height=280)
    else:
        st.caption(copy["empty"])

    if activity:
        st.markdown(f"### {copy['chart_activity']}")
        try:
            import altair as alt
            import pandas as pd

            rows = []
            for row in activity:
                rows.append(
                    {
                        "day": row["day"],
                        "count": row["mood_count"],
                        "type": copy["activity_mood"],
                    }
                )
                rows.append(
                    {
                        "day": row["day"],
                        "count": row["journal_count"],
                        "type": copy["activity_journal"],
                    }
                )
            adf = pd.DataFrame(rows)
            adf["day"] = pd.to_datetime(adf["day"])
            chart = (
                alt.Chart(adf)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("day:T", title=None),
                    y=alt.Y("count:Q", title=None),
                    color=alt.Color(
                        "type:N",
                        scale=alt.Scale(
                            domain=[copy["activity_mood"], copy["activity_journal"]],
                            range=[_CHART_PRIMARY, _CHART_SECONDARY],
                        ),
                        legend=alt.Legend(title=None),
                    ),
                    tooltip=["day:T", "type:N", "count:Q"],
                )
                .properties(height=260)
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            chart_data = {
                row["day"]: {
                    copy["activity_mood"]: row["mood_count"],
                    copy["activity_journal"]: row["journal_count"],
                }
                for row in activity
            }
            st.bar_chart(chart_data, height=260)
    st.markdown("</div>", unsafe_allow_html=True)
