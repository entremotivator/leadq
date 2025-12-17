import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Lead Qualifier Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Generate 76 demo clients
@st.cache_data
def generate_demo_clients():
    locations = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra']
    timelines = ['1-3 months', '3-6 months', '6-12 months', '12+ months']
    property_types = ['Apartment', 'House', 'Townhouse', 'Villa', 'Studio']
    first_names = ['James', 'Emma', 'Oliver', 'Sophia', 'William', 'Ava', 'Lucas', 'Mia', 
                   'Noah', 'Isabella', 'Liam', 'Charlotte', 'Ethan', 'Amelia', 'Mason']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas']
    
    clients = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(76):
        budget_min = random.randint(200000, 1000000)
        budget_max = budget_min + random.randint(100000, 500000)
        location = random.choice(locations)
        timeline = random.choice(timelines)
        
        # Calculate score based on criteria
        score = 50
        if budget_min > 600000:
            score += 20
        if location == 'Sydney':
            score += 15
        if timeline == '1-3 months':
            score += 15
        score += random.randint(-10, 20)
        score = max(0, min(100, score))
        
        date = start_date + timedelta(days=random.randint(0, 350))
        
        clients.append({
            'ID': i + 1,
            'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'Email': f"client{i+1}@example.com",
            'Budget_Min': budget_min,
            'Budget_Max': budget_max,
            'Location': location,
            'Timeline': timeline,
            'Property_Type': random.choice(property_types),
            'Score': score,
            'Qualified': 'Yes' if score >= 70 else 'No',
            'Date': date.strftime('%Y-%m-%d'),
            'Urgency': 'High' if timeline == '1-3 months' else 'Medium' if timeline == '3-6 months' else 'Low'
        })
    
    return pd.DataFrame(clients)

# Load data
df = generate_demo_clients()

# Sidebar
st.sidebar.title("🏠 Lead Qualifier")
st.sidebar.markdown("---")

# Filters
st.sidebar.header("Filters")

search_term = st.sidebar.text_input("🔍 Search by Name or Email", "")

qualification_filter = st.sidebar.selectbox(
    "Qualification Status",
    ["All", "Qualified", "Unqualified"]
)

location_filter = st.sidebar.multiselect(
    "Location",
    options=df['Location'].unique(),
    default=df['Location'].unique()
)

timeline_filter = st.sidebar.multiselect(
    "Timeline",
    options=df['Timeline'].unique(),
    default=df['Timeline'].unique()
)

budget_range = st.sidebar.slider(
    "Minimum Budget Range",
    min_value=int(df['Budget_Min'].min()),
    max_value=int(df['Budget_Min'].max()),
    value=(int(df['Budget_Min'].min()), int(df['Budget_Min'].max())),
    step=50000,
    format="$%d"
)

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df['Name'].str.contains(search_term, case=False) | 
        filtered_df['Email'].str.contains(search_term, case=False)
    ]

if qualification_filter != "All":
    filtered_df = filtered_df[filtered_df['Qualified'] == ('Yes' if qualification_filter == "Qualified" else 'No')]

filtered_df = filtered_df[filtered_df['Location'].isin(location_filter)]
filtered_df = filtered_df[filtered_df['Timeline'].isin(timeline_filter)]
filtered_df = filtered_df[
    (filtered_df['Budget_Min'] >= budget_range[0]) & 
    (filtered_df['Budget_Min'] <= budget_range[1])
]

# Main Dashboard
st.title("🏠 Real Estate Lead Qualifier Dashboard")
st.markdown("### Intelligent Lead Scoring & Analytics")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Leads",
        len(filtered_df),
        delta=f"{len(filtered_df) - len(df)} from total"
    )

with col2:
    qualified_count = len(filtered_df[filtered_df['Qualified'] == 'Yes'])
    st.metric(
        "Qualified Leads",
        qualified_count,
        delta=f"{round(qualified_count/len(filtered_df)*100, 1)}%"
    )

with col3:
    avg_score = filtered_df['Score'].mean()
    st.metric(
        "Average Score",
        f"{avg_score:.1f}",
        delta=f"{avg_score - df['Score'].mean():.1f}"
    )

with col4:
    avg_budget = filtered_df['Budget_Min'].mean()
    st.metric(
        "Avg Budget",
        f"${avg_budget:,.0f}",
        delta=f"${avg_budget - df['Budget_Min'].mean():,.0f}"
    )

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Lead Qualification Distribution")
    qual_counts = filtered_df['Qualified'].value_counts()
    fig_pie = px.pie(
        values=qual_counts.values,
        names=qual_counts.index,
        color=qual_counts.index,
        color_discrete_map={'Yes': '#10b981', 'No': '#ef4444'},
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📍 Leads by Location")
    location_counts = filtered_df['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Count']
    fig_bar = px.bar(
        location_counts,
        x='Location',
        y='Count',
        color='Count',
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏰ Timeline Distribution")
    timeline_counts = filtered_df['Timeline'].value_counts().reset_index()
    timeline_counts.columns = ['Timeline', 'Count']
    fig_timeline = px.bar(
        timeline_counts,
        x='Timeline',
        y='Count',
        color='Count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    st.subheader("💰 Budget Distribution")
    fig_budget = px.histogram(
        filtered_df,
        x='Budget_Min',
        nbins=20,
        color_discrete_sequence=['#8b5cf6']
    )
    fig_budget.update_layout(
        xaxis_title="Budget Range",
        yaxis_title="Number of Leads",
        showlegend=False
    )
    st.plotly_chart(fig_budget, use_container_width=True)

# Score Distribution
st.subheader("🎯 Lead Score Distribution")
fig_score = px.histogram(
    filtered_df,
    x='Score',
    nbins=20,
    color='Qualified',
    color_discrete_map={'Yes': '#10b981', 'No': '#ef4444'},
    marginal='box'
)
fig_score.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="Qualification Threshold (70)")
st.plotly_chart(fig_score, use_container_width=True)

# Leads over time
st.subheader("📈 Leads Over Time")
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
daily_leads = filtered_df.groupby('Date').size().reset_index(name='Count')
fig_timeline = px.line(
    daily_leads,
    x='Date',
    y='Count',
    markers=True
)
fig_timeline.update_traces(line_color='#667eea', line_width=3)
st.plotly_chart(fig_timeline, use_container_width=True)

# Detailed Lead Table
st.markdown("---")
st.subheader("📋 Detailed Lead Information")

# Sort options
sort_col = st.selectbox(
    "Sort by:",
    ["Score", "Budget_Min", "Name", "Date"],
    index=0
)
sort_order = st.radio("Order:", ["Descending", "Ascending"], horizontal=True)

sorted_df = filtered_df.sort_values(
    by=sort_col,
    ascending=(sort_order == "Ascending")
)

# Display table with formatting
display_df = sorted_df.copy()
display_df['Budget_Min'] = display_df['Budget_Min'].apply(lambda x: f"${x:,.0f}")
display_df['Budget_Max'] = display_df['Budget_Max'].apply(lambda x: f"${x:,.0f}")
display_df['Budget Range'] = display_df['Budget_Min'] + ' - ' + display_df['Budget_Max']

# Select columns to display
columns_to_display = ['Name', 'Email', 'Location', 'Budget Range', 'Timeline', 
                     'Property_Type', 'Score', 'Qualified', 'Urgency', 'Date']

st.dataframe(
    display_df[columns_to_display],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score": st.column_config.ProgressColumn(
            "Score",
            min_value=0,
            max_value=100,
            format="%d",
        ),
        "Qualified": st.column_config.TextColumn(
            "Qualified",
        )
    }
)

# Download button
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"leads_export_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🏠 Real Estate Lead Qualifier Dashboard | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
