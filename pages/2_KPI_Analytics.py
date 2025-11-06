"""
KPI Analytics - Detailed KPI views
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from config.config import Config
from src.kpis.table_based_kpis import table_kpi_engine
from src.kpis.memory_based_kpis import memory_kpi_engine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

st.set_page_config(
    page_title="KPI Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("📈 KPI Analytics")
st.markdown("Detailed analysis of key performance indicators")

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ KPI Settings")
    
    # Processing method
    processing_method = st.radio(
        "Processing Method",
        ["SQL (Table-based)", "Pandas (Memory-based)"],
        help="Choose between SQL queries or Pandas in-memory processing"
    )
    
    st.markdown("---")
    
    # KPI selection
    st.markdown("### 📊 Select KPI")
    selected_kpi = st.selectbox(
        "KPI",
        [
            "All KPIs",
            "Repeat Customers",
            "Monthly Order Trends",
            "Regional Revenue",
            "Top Customers (Last 30 Days)"
        ]
    )
    
    # Additional parameters
    if selected_kpi == "Top Customers (Last 30 Days)":
        st.markdown("---")
        st.markdown("### 🎛️ Parameters")
        days = st.slider("Time Period (days)", 7, 90, 30)
        limit = st.slider("Number of customers", 5, 20, 10)
    else:
        days = 30
        limit = 10
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main content
st.markdown("---")

# Determine which engine to use
use_memory = "Pandas" in processing_method

@st.cache_data(ttl=Config.CACHE_TTL)
def calculate_kpis(use_memory_engine, days_param, limit_param):
    """Calculate KPIs based on selected method"""
    if use_memory_engine:
        memory_kpi_engine.load_data()
        return memory_kpi_engine.calculate_all_kpis(days=days_param, limit=limit_param)
    else:
        return table_kpi_engine.calculate_all_kpis(days=days_param, limit=limit_param)

# Calculate KPIs
with st.spinner(f"Calculating KPIs using {processing_method}..."):
    kpi_results = calculate_kpis(use_memory, days, limit)

# Display KPIs based on selection
if selected_kpi == "All KPIs":
    # Display all KPIs
    
    # KPI 1: Repeat Customers
    st.markdown("## 🔁 Repeat Customers")
    result = kpi_results.get('repeat_customers', {})
    
    if result.get('success'):
        data = result.get('data', [])
        metadata = result.get('metadata', result)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Repeat Customers", metadata.get('total_repeat_customers', 0))
        with col2:
            st.metric("Total Orders", metadata.get('total_orders', 0))
        with col3:
            st.metric("Total Revenue", f"₹{metadata.get('total_revenue', 0):,.2f}")
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error(f"Error: {result.get('error')}")
    
    st.markdown("---")
    
    # KPI 2: Monthly Trends
    st.markdown("## 📅 Monthly Order Trends")
    result = kpi_results.get('monthly_trends', {})
    
    if result.get('success'):
        data = result.get('data', [])
        metadata = result.get('metadata', result)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Months", metadata.get('total_months', 0))
        with col2:
            st.metric("Total Orders", metadata.get('total_orders', 0))
        with col3:
            st.metric("Avg Monthly Orders", f"{metadata.get('avg_monthly_orders', 0):.1f}")
        
        if data:
            df = pd.DataFrame(data)
            
            # Line chart
            fig = px.line(
                df,
                x='month_year',
                y='total_orders',
                title='Orders Over Time',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error(f"Error: {result.get('error')}")
    
    st.markdown("---")
    
    # KPI 3: Regional Revenue
    st.markdown("## 🌍 Regional Revenue")
    result = kpi_results.get('regional_revenue', {})
    
    if result.get('success'):
        data = result.get('data', [])
        metadata = result.get('metadata', result)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Regions", metadata.get('total_regions', 0))
        with col2:
            st.metric("Total Revenue", f"₹{metadata.get('total_revenue', 0):,.2f}")
        with col3:
            st.metric("Top Region", metadata.get('highest_revenue_region', 'N/A'))
        
        if data:
            df = pd.DataFrame(data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                fig = px.bar(
                    df,
                    x='region',
                    y='total_revenue',
                    title='Revenue by Region',
                    color='total_revenue',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie chart
                fig = px.pie(
                    df,
                    values='total_revenue',
                    names='region',
                    title='Revenue Distribution',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error(f"Error: {result.get('error')}")
    
    st.markdown("---")
    
    # KPI 4: Top Customers
    st.markdown(f"## 🏆 Top Customers (Last {days} Days)")
    result = kpi_results.get('top_customers', {})
    
    if result.get('success'):
        data = result.get('data', [])
        metadata = result.get('metadata', result)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Top Customers", metadata.get('top_customer_count', 0))
        with col2:
            st.metric("Total Revenue", f"₹{metadata.get('total_revenue_top_customers', 0):,.2f}")
        with col3:
            st.metric("Avg Spend", f"₹{metadata.get('avg_spend_top_customers', 0):,.2f}")
        
        if data:
            df = pd.DataFrame(data)
            
            # Bar chart
            if 'customer_name' in df.columns and 'total_spend' in df.columns:
                fig = px.bar(
                    df,
                    x='customer_name',
                    y='total_spend',
                    title='Top Customers by Spend',
                    color='total_spend',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error(f"Error: {result.get('error')}")

else:
    # Display individual KPI
    st.markdown(f"## {selected_kpi}")
    
    kpi_key_map = {
        "Repeat Customers": "repeat_customers",
        "Monthly Order Trends": "monthly_trends",
        "Regional Revenue": "regional_revenue",
        "Top Customers (Last 30 Days)": "top_customers"
    }
    
    kpi_key = kpi_key_map.get(selected_kpi)
    result = kpi_results.get(kpi_key, {})
    
    if result.get('success'):
        data = result.get('data', [])
        metadata = result.get('metadata', result)
        
        # Display metadata
        st.markdown("### 📊 Summary")
        cols = st.columns(len([k for k in metadata.keys() if k not in ['data', 'kpi_name', 'description', 'calculated_at', 'success', 'method']]))
        for i, (key, value) in enumerate([item for item in metadata.items() if item[0] not in ['data', 'kpi_name', 'description', 'calculated_at', 'success', 'method']]):
            with cols[i]:
                st.metric(key.replace('_', ' ').title(), f"{value:,.2f}" if isinstance(value, float) else value)
        
        st.markdown("---")
        
        # Display data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{kpi_key}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.error(f"Error: {result.get('error')}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Method: {processing_method}")