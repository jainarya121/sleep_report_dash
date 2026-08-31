import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
    
    if 'Sleep Disorder' in df.columns:
        df['Sleep Disorder'] = df['Sleep Disorder'].fillna("None")
        
    return df

df = load_and_clean_data()

def assign_tier(row):
    if row['Sleep Duration'] < 6.0 or (row['Sleep Duration'] < 6.5 and row['Quality of Sleep'] <= 5):
        return 'Tier 1'
    elif row['Sleep Duration'] < 7.0 and row['Stress Level'] >= 6:
        return 'Tier 2'
    else:
        return 'Tier 3'

df['Sleep_Health_Tier'] = df.apply(assign_tier, axis=1)

st.set_page_config(page_title="Sleep Health Dashboard", layout="wide")
st.title("Sleep Health Analytics Dashboard")

st.subheader("Overview KPIs")
col1, col2, col3, col4, col5 = st.columns(5)

total_records = len(df)
tier_percentages = df['Sleep_Health_Tier'].value_counts(normalize=True) * 100

tier1_df = df[df['Sleep_Health_Tier'] == 'Tier 1']
avg_hr_tier1 = tier1_df['Heart Rate'].mean() if not tier1_df.empty else 0

col1.metric("Total Records", total_records)
col2.metric("Tier 1 (Severely Deprived)", f"{tier_percentages.get('Tier 1', 0):.1f}%")
col3.metric("Tier 2 (Strained)", f"{tier_percentages.get('Tier 2', 0):.1f}%")
col4.metric("Tier 3 (Healthy)", f"{tier_percentages.get('Tier 3', 0):.1f}%")
col5.metric("Avg Heart Rate (Tier 1)", f"{avg_hr_tier1:.1f} bpm")

st.divider()

st.subheader("Visual Insights")

fig_prof = px.histogram(
    df, x="Occupation", color="Sleep_Health_Tier", 
    barmode="group", 
    title="Sleep Tiers Breakdown by Profession",
    category_orders={"Sleep_Health_Tier": ["Tier 1", "Tier 2", "Tier 3"]}
)
st.plotly_chart(fig_prof, width="stretch")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_scatter = px.scatter(
        df, x="Daily Steps", y="Sleep Duration", 
        color="Sleep_Health_Tier", 
        title="Daily Steps vs. Sleep Duration",
        category_orders={"Sleep_Health_Tier": ["Tier 1", "Tier 2", "Tier 3"]}
    )
    st.plotly_chart(fig_scatter, width="stretch")

with col_chart2:
    avg_metrics = df.groupby('Sleep_Health_Tier')[['Stress Level', 'Heart Rate']].mean().reset_index()
    fig_comp = px.bar(
        avg_metrics, x='Sleep_Health_Tier', y=['Stress Level', 'Heart Rate'], 
        barmode='group', 
        title="Average Stress Level and Heart Rate by Tier"
    )
    st.plotly_chart(fig_comp, width="stretch")

st.divider()

st.subheader("Executive Summary")

if not tier1_df.empty:
    vulnerable_counts = tier1_df['Occupation'].value_counts()
    top_vulnerable_profs = ", ".join(vulnerable_counts.head(3).index.tolist())
else:
    top_vulnerable_profs = "None identified"

st.info(f"""
**Vulnerable Occupations:** According to our analysis of the data jobs like **{top_vulnerable_profs}** have the cases of severe sleep deprivation (Tier 1). 

**Actionable Lifestyle Takeaways:** 
* **Stress Management:** People who work in stressful jobs need to reduce their screen usage and avoid work related messages in the evening to help improve their sleep quality.
* **Activity Balance:** Given data shows us that moderate number of steps a day, results in improved quality of sleep, while keeping the heart rate stable during leisure time. 
* **Targeted Recovery:** Employees who are in tier 1 and tier 2 should keep an eye on their heart health because higher stress and less sleep lead to a higher heart rate during leisure time.
""")