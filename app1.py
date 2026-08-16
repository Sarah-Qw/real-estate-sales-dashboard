"""
Real Estate Sales Dashboard
============================
An interactive dashboard for analyzing real estate sales data, built with
Streamlit + Plotly.

Pages:
  - "Overview": key charts (cities, monthly trend, projects, agents,
    segments, channels)
  - "Insights": auto-generated text insights from the data

Run with:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Real Estate Sales Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme state (dark / light)
# ---------------------------------------------------------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# A single cohesive color language used across the WHOLE dashboard, so every
# chart reads as part of the same family instead of unrelated random colors.
#   - accent      -> single-series bars/lines (one flat color everywhere)
#   - sequential  -> continuous color scales (treemap, colored bars/scatter)
#   - qualitative -> small categorical sets (pie chart segments), all drawn
#                    from the same blue family so the palette stays cohesive
COLOR_THEMES = {
    True: {  # dark mode
        "bg": "#0E1117",
        "bg_secondary": "#161A23",
        "card_bg": "#1B2028",
        "card_bg_alt": "#20262F",
        "text": "#F1F3F7",
        "subtext": "#9AA4B2",
        "border": "#2A2F3A",
        "accent": "#5B8FD9",
        "shadow": "rgba(0, 0, 0, 0.45)",
        "sequential": "Blues",
        "qualitative": ["#5B8FD9", "#3E6BA8", "#8FB4E3", "#2A4C7A", "#B7CEEF", "#1B3358"],
        "plotly_template": "plotly_dark",
    },
    False: {  # light mode
        "bg": "#F7F9FC",
        "bg_secondary": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "card_bg_alt": "#F2F5FA",
        "text": "#1A1D23",
        "subtext": "#5B6472",
        "border": "#E3E7EF",
        "accent": "#2F5FA8",
        "shadow": "rgba(31, 63, 102, 0.12)",
        "sequential": "Blues",
        "qualitative": ["#2F5FA8", "#4F81BD", "#7FA9D9", "#1F3F66", "#9BC4F7", "#123054"],
        "plotly_template": "plotly_white",
    },
}


def inject_theme_css(dark: bool) -> None:
    t = COLOR_THEMES[dark]
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {t['bg']};
                color: {t['text']};
            }}
            section[data-testid="stSidebar"] {{
                background-color: {t['bg_secondary']};
                border-right: 1px solid {t['border']};
            }}
            h1, h2, h3, h4, h5, h6, p, span, label, div {{
                color: {t['text']};
            }}

            /* KPI cards */
            .kpi-card {{
                background: linear-gradient(160deg, {t['card_bg']} 0%, {t['card_bg_alt']} 100%);
                border: 1px solid {t['border']};
                border-top: 3px solid {t['accent']};
                border-radius: 16px;
                padding: 20px 18px;
                text-align: center;
                box-shadow: 0 6px 16px {t['shadow']};
                transition: transform .15s ease, box-shadow .15s ease;
            }}
            .kpi-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 22px {t['shadow']};
            }}
            .kpi-icon {{
                font-size: 22px;
                margin-bottom: 4px;
            }}
            .kpi-value {{
                font-size: 27px;
                font-weight: 700;
                color: {t['accent']};
                margin: 0;
            }}
            .kpi-label {{
                font-size: 13px;
                color: {t['subtext']};
                margin: 4px 0 0 0;
                letter-spacing: 0.2px;
            }}

            /* Chart cards: every chart sits inside a bordered container */
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                background: linear-gradient(160deg, {t['card_bg']} 0%, {t['card_bg_alt']} 100%);
                border: 1px solid {t['border']};
                border-radius: 18px;
                padding: 6px 10px 12px 10px;
                box-shadow: 0 6px 18px {t['shadow']};
                margin-bottom: 22px;
            }}

            /* Insight cards */
            .insight-card {{
                background-color: {t['card_bg']};
                border: 1px solid {t['border']};
                border-left: 4px solid {t['accent']};
                border-radius: 10px;
                padding: 16px 18px;
                margin-bottom: 12px;
            }}
            .insight-card p {{
                margin: 0;
                color: {t['text']};
                font-size: 15px;
                line-height: 1.6;
            }}

            div[data-testid="stMetric"] {{
                background-color: {t['card_bg']};
                border: 1px solid {t['border']};
                border-radius: 12px;
                padding: 10px;
            }}
            .block-container {{
                padding-top: 2rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme_css(st.session_state.dark_mode)
THEME = COLOR_THEMES[st.session_state.dark_mode]
TEMPLATE = THEME["plotly_template"]
ACCENT = THEME["accent"]
SEQUENTIAL = THEME["sequential"]
QUALITATIVE = THEME["qualitative"]
TEXT_COLOR = THEME["text"]


def style_fig(fig, title: str):
    """Apply one consistent, high-contrast look to every chart so titles
    stay readable in both dark and light mode, and center every title."""
    fig.update_layout(
        template=TEMPLATE,
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=17, color=TEXT_COLOR),
        ),
        margin=dict(t=64, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color=TEXT_COLOR),
        legend=dict(font=dict(color=TEXT_COLOR)),
    )
    fig.update_xaxes(title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR))
    fig.update_yaxes(title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR))
    return fig


def chart_card(fig, title: str):
    """Render a chart wrapped in its own bordered 'card' container."""
    with st.container(border=True):
        st.plotly_chart(style_fig(fig, title), use_container_width=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
REQUIRED_COLS = [
    "city", "final_price", "year", "month",
    "project_name", "agent", "segment", "channel",
]


@st.cache_data
def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file)


def get_dataframe():
    # Try loading the dataset that ships next to the app first, silently.
    # The upload box only appears as a fallback if that file isn't found,
    # so it doesn't clutter the sidebar when data is already available.
    default_path = "sales_full_dataset.csv"
    try:
        return load_data(default_path)
    except Exception:
        pass

    st.sidebar.markdown("### 📂 Data Source")
    uploaded = st.sidebar.file_uploader("Upload sales_full_dataset.csv", type=["csv"])
    if uploaded is not None:
        return load_data(uploaded)

    st.sidebar.info("⬆️ Upload a CSV file to get started.")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar: navigation, theme toggle, filters
# ---------------------------------------------------------------------------
st.sidebar.title("🏙️ Real Estate Dashboard")

page = st.sidebar.radio("Page", ["📊 Overview", "💡 Insights"], index=0)

st.sidebar.markdown("---")
dark_toggle = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
if dark_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_toggle
    st.rerun()

df = get_dataframe()

missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    st.error(f"The following required columns are missing from the file: {missing}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Filters")

years = sorted(df["year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Year", years, default=years)

cities = sorted(df["city"].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect("City", cities, default=cities)

channels = sorted(df["channel"].dropna().unique().tolist())
selected_channels = st.sidebar.multiselect("Sales Channel", channels, default=channels)

filtered_df = df[
    df["year"].isin(selected_years)
    & df["city"].isin(selected_cities)
    & df["channel"].isin(selected_channels)
].copy()

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

filtered_df["year_month"] = (
    filtered_df["year"].astype(str) + "-" + filtered_df["month"].astype(str).str.zfill(2)
)

# ---------------------------------------------------------------------------
# Aggregation helpers (shared by both pages)
# ---------------------------------------------------------------------------

def agg_city_revenue(data):
    return (
        data.groupby("city")["final_price"].sum().reset_index()
        .sort_values("final_price", ascending=False)
    )


def agg_monthly(data):
    m = data.groupby(["year", "month"])["final_price"].sum().reset_index()
    m["year_month"] = m["year"].astype(str) + "-" + m["month"].astype(str).str.zfill(2)
    return m.sort_values(["year", "month"])


def agg_projects(data):
    return (
        data.groupby("project_name")["final_price"].sum().reset_index()
        .sort_values("final_price", ascending=False)
    )


def agg_agents(data):
    return (
        data.groupby("agent")
        .agg(revenue=("final_price", "sum"), deals=("final_price", "count"))
        .reset_index()
    )


def agg_segment(data):
    return data.groupby("segment")["final_price"].sum().reset_index()


def agg_channel(data):
    return (
        data.groupby("channel")["final_price"].sum().reset_index()
        .sort_values("final_price", ascending=False)
    )


def agg_avg_city(data):
    return (
        data.groupby("city")["final_price"].mean().reset_index()
        .sort_values("final_price", ascending=False)
    )


def fmt_b(x):
    return f"{x/1e9:,.2f}B"


def fmt_m(x):
    return f"{x/1e6:,.2f}M"


# ===========================================================================
# PAGE 1: OVERVIEW
# ===========================================================================
if page == "📊 Overview":
    st.title("🏢 Real Estate Sales Performance")
    st.caption("A complete interactive view of real estate sales performance across cities, projects, agents and channels.")

    total_revenue = filtered_df["final_price"].sum()
    total_deals = len(filtered_df)
    avg_deal = filtered_df["final_price"].mean()
    top_city = agg_city_revenue(filtered_df).iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><p class="kpi-icon">💰</p>'
            f'<p class="kpi-value">{fmt_b(total_revenue)}</p>'
            f'<p class="kpi-label">Total Revenue</p></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card"><p class="kpi-icon">🤝</p>'
            f'<p class="kpi-value">{total_deals:,}</p>'
            f'<p class="kpi-label">Total Deals</p></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card"><p class="kpi-icon">📐</p>'
            f'<p class="kpi-value">{fmt_m(avg_deal)}</p>'
            f'<p class="kpi-label">Average Deal Size</p></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card"><p class="kpi-icon">🏆</p>'
            f'<p class="kpi-value">{top_city["city"]}</p>'
            f'<p class="kpi-label">Top City by Revenue</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Row 1: revenue by city + top 4 cities ---
    c1, c2 = st.columns([1.3, 1])
    with c1:
        city_sales = agg_city_revenue(filtered_df)
        city_sales["label"] = city_sales["final_price"].apply(fmt_b)
        fig = px.bar(city_sales, x="city", y="final_price", text="label")
        fig.update_traces(textposition="outside", marker_color=ACCENT)
        chart_card(fig, "Total Revenue by City")

    with c2:
        top4 = agg_city_revenue(filtered_df).head(4)
        fig_city = px.bar(
            top4, x="final_price", y="city", orientation="h",
            text_auto=".2s", color="final_price", color_continuous_scale=SEQUENTIAL,
        )
        chart_card(fig_city, "Top 4 Cities by Revenue")

    # --- Row 2: monthly trend ---
    monthly_sales = agg_monthly(filtered_df)
    fig_month = px.line(monthly_sales, x="year_month", y="final_price", markers=True)
    fig_month.update_traces(line_color=ACCENT, marker_color=ACCENT)
    chart_card(fig_month, "Monthly Sales Trend")

    # --- Row 3: projects (treemap) + agents (bubble) ---
    c3, c4 = st.columns(2)
    with c3:
        project_sales = agg_projects(filtered_df).head(10)
        fig_projects = px.treemap(
            project_sales, path=["project_name"], values="final_price",
            color="final_price", color_continuous_scale=SEQUENTIAL,
        )
        fig_projects.update_traces(
            textinfo="label+percent parent",
            texttemplate="<b>%{label}</b><br>%{percentParent:.1%}",
        )
        chart_card(fig_projects, "Revenue Contribution by Project (Top 10)")

    with c4:
        agent_perf = agg_agents(filtered_df)
        fig_agents = px.scatter(
            agent_perf, x="deals", y="revenue", size="revenue",
            hover_name="agent", color="revenue", color_continuous_scale=SEQUENTIAL,
            size_max=40,
        )
        chart_card(fig_agents, "Agent Performance: Deals vs Revenue")

    # --- Row 4: segments (pie) + channels (bar) ---
    c5, c6 = st.columns(2)
    with c5:
        segment_sales = agg_segment(filtered_df)
        fig_seg = px.pie(
            segment_sales, names="segment", values="final_price",
            color_discrete_sequence=QUALITATIVE,
        )
        fig_seg.update_traces(textinfo="label+percent")
        chart_card(fig_seg, "Revenue by Customer Segment")

    with c6:
        channel_sales = agg_channel(filtered_df)
        channel_sales["label"] = channel_sales["final_price"].apply(fmt_b)
        fig_ch = px.bar(channel_sales, x="channel", y="final_price", text="label")
        fig_ch.update_traces(textposition="outside", marker_color=ACCENT)
        chart_card(fig_ch, "Revenue by Sales Channel")

    # --- Row 5: average deal size per city ---
    avg_city_price = agg_avg_city(filtered_df)
    avg_city_price["label"] = avg_city_price["final_price"].apply(fmt_m)
    fig_avg = px.bar(
        avg_city_price, x="final_price", y="city", text="label", orientation="h",
    )
    fig_avg.update_traces(textposition="outside", marker_color=ACCENT)
    chart_card(fig_avg, "Average Deal Size per City")


# ===========================================================================
# PAGE 2: INSIGHTS
# ===========================================================================
else:
    st.title("💡 Real Estate Market Insights")
    st.caption("Insights auto-generated from the currently filtered data.")

    city_sales = agg_city_revenue(filtered_df)
    monthly_sales = agg_monthly(filtered_df)
    project_sales = agg_projects(filtered_df)
    agent_perf = agg_agents(filtered_df)
    segment_sales = agg_segment(filtered_df).sort_values("final_price", ascending=False)
    channel_sales = agg_channel(filtered_df)
    avg_city_price = agg_avg_city(filtered_df)

    total_revenue = filtered_df["final_price"].sum()

    # Growth of the last month vs. the previous one
    growth_text = None
    if len(monthly_sales) >= 2:
        last = monthly_sales.iloc[-1]
        prev = monthly_sales.iloc[-2]
        if prev["final_price"] != 0:
            growth = (last["final_price"] - prev["final_price"]) / prev["final_price"] * 100
            direction = "an increase" if growth >= 0 else "a decrease"
            growth_text = (
                f"Revenue in {last['year_month']} showed {direction} of "
                f"{abs(growth):.1f}% compared to {prev['year_month']}."
            )

    top_city = city_sales.iloc[0]
    top_city_share = top_city["final_price"] / total_revenue * 100

    top_project = project_sales.iloc[0]
    top_project_share = top_project["final_price"] / total_revenue * 100

    top_agent = agent_perf.sort_values("revenue", ascending=False).iloc[0]

    top_segment = segment_sales.iloc[0]
    top_segment_share = top_segment["final_price"] / total_revenue * 100

    top_channel = channel_sales.iloc[0]
    top_channel_share = top_channel["final_price"] / total_revenue * 100

    priciest_city = avg_city_price.iloc[0]

    insights = [
        f"🏙️ <b>{top_city['city']}</b> is the top-revenue city with total sales of "
        f"{fmt_b(top_city['final_price'])}, or {top_city_share:.1f}% of total revenue.",

        f"🏗️ Project <b>{top_project['project_name']}</b> leads all projects with "
        f"{fmt_b(top_project['final_price'])} in revenue ({top_project_share:.1f}% of total).",

        f"🧑‍💼 Agent <b>{top_agent['agent']}</b> is the top performer, generating "
        f"{fmt_b(top_agent['revenue'])} across {int(top_agent['deals'])} deals.",

        f"👥 The <b>{top_segment['segment']}</b> segment contributes the most revenue at "
        f"{top_segment_share:.1f}% ({fmt_b(top_segment['final_price'])}).",

        f"📡 The <b>{top_channel['channel']}</b> channel is the most effective, driving "
        f"{fmt_b(top_channel['final_price'])} ({top_channel_share:.1f}% of total).",

        f"💰 <b>{priciest_city['city']}</b> has the highest average deal size, at "
        f"{fmt_m(priciest_city['final_price'])} per deal.",
    ]

    if growth_text:
        insights.insert(1, "📈 " + growth_text)

    for text in insights:
        st.markdown(f'<div class="insight-card"><p>{text}</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 City Performance Summary")
    summary = city_sales.merge(
        avg_city_price.rename(columns={"final_price": "avg_price"}), on="city"
    )
    summary["share_%"] = (summary["final_price"] / total_revenue * 100).round(2)
    summary = summary.rename(
        columns={"final_price": "total_revenue", "avg_price": "avg_deal_size"}
    )
    st.dataframe(
        summary.style.format(
            {"total_revenue": "{:,.0f}", "avg_deal_size": "{:,.0f}", "share_%": "{:.2f}%"}
        ),
        use_container_width=True,
    )