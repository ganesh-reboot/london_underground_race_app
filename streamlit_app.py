import pandas as pd
import plotly.express as px
import streamlit as st

# --- Page setup ---
st.set_page_config(page_title="London Race Chart", page_icon="🏁", layout="wide")
st.title("Race Between Train, Walking, and Cycling")
st.caption("Compare how long it takes to travel between London stations via different modes of transport.")

# --- Load data ---
@st.cache_data
def load_data():
    train_routes = pd.read_csv("train_routes.csv")
    df_reversed = train_routes.copy()
    df_reversed["origin"], df_reversed["destination"] = train_routes["destination"], train_routes["origin"]

    df_full = pd.concat([train_routes, df_reversed], ignore_index=True)
    df_full.drop_duplicates(subset=["origin", "destination"], inplace=True)
    df_full.reset_index(drop=True, inplace=True)
    return df_full

df = load_data()

# --- Sidebar inputs ---
st.sidebar.header("Select route")
source = st.sidebar.selectbox("Origin", sorted(df["origin"].unique()))
valid_dests = df.loc[df["origin"] == source, "destination"].unique()
destination = st.sidebar.selectbox("Destination", sorted(valid_dests))

# --- Filter for selected route ---
row = df[(df["origin"] == source) & (df["destination"] == destination)]

if row.empty:
    st.warning("No data available for this route.")
    st.stop()

row = row.iloc[0]

# --- Prepare data ---
modes = ["Train", "Walking", "Cycling"]
times = [row.total_time_in_train, row.total_walking_time, row.total_cycling_time]
calories = [0, row.calories_burnt_walking, row.calories_burnt_cycling]

# --- Animation-like data ---
animation_data = []
for t in range(0, int(max(times)) + 1):
    for mode, total_time in zip(modes, times):
        progress = min(t / total_time * 100, 100)
        animation_data.append({
            "Mode": mode,
            "Progress (%)": progress,
            "Time (min)": t
        })
anim_df = pd.DataFrame(animation_data)

# --- Race chart ---
fig = px.bar(
    anim_df,
    x="Progress (%)",
    y="Mode",
    color="Mode",
    animation_frame="Time (min)",
    range_x=[0, 100],
    title=f"From {source} → {destination}",
    orientation='h'
)

fig.update_layout(
    xaxis_title="Progress toward destination (%)",
    yaxis_title="Travel Mode",
    showlegend=False,
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# --- Additional stats ---
st.markdown("### Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Train time (min)", round(row.total_time_in_train, 1))
col2.metric("Walking time (min)", round(row.total_walking_time, 1))
col3.metric("Cycling time (min)", round(row.total_cycling_time, 1))

st.markdown("### Calories Burnt")
col4, col5 = st.columns(2)
col4.metric("Walking", f"{round(row.calories_burnt_walking)} kcal")
col5.metric("Cycling", f"{round(row.calories_burnt_cycling)} kcal")
