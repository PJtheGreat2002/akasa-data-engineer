"""
Overview Dashboard - Main analytics view
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from config.config import Config
from src.database.db_manager import db_manager
from src.kpis.table_based_kpis import table_kpi_engine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

st.set_page_config(
    page_title="Overview Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Overview Dashboard")
st.markdown("Real-time view of key business metrics and trends")

# Refresh button
col1, col2, col3 = st.columns([6, 1, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
with col3:
    view_mode = st.selectbox("View", ["SQL", "Pandas"], label_visibility="collapsed")

st.markdown("---")

# Load data
@st.cache_data(ttl=Config.CACHE_TTL)
def load_overview_data():
    """Load overview data from database"""
    try:
        # Total customers
        customers = db_manager.execute_query("SELECT COUNT(*) as count FROM customers")[0]['count']
        
        # Total orders
        orders = db_manager.execute_query("SELECT COUNT(*) as count FROM orders")[0]['count']
        
        # Total revenue
        revenue = db_manager.execute_query("SELECT COALESCE(SUM(total_amount), 0) as total FROM orders")[0]['total']
        
        # Average order value
        avg_order = revenue / orders if orders > 0 else 0
        
        # Recent orders (last 7 days)
        recent_orders = db_manager.execute_query("""
            SELECT COUNT(*) as count 
            FROM orders 
            WHERE order_date_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)[0]['count']
        
        # Repeat customers
        repeat_customers = db_manager.execute_query("""
            SELECT COUNT(DISTINCT c.customer_id) as count
            FROM customers c
            INNER JOIN orders o ON c.mobile_number = o.mobile_number
            GROUP BY c.customer_id
            HAVING COUNT(o.order_id) > 1
        """)
        repeat_count = len(repeat_customers)
        
        return {
            'customers': customers,
            'orders': orders,
            'revenue': float(revenue),
            'avg_order': float(avg_order),
            'recent_orders': recent_orders,
            'repeat_customers': repeat_count
        }
    except Exception as e:
        logger.error(f"Error loading overview data: {e}")
        return None

# Display metrics
data = load_overview_data()

if data:
    # Key metrics
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("👥 Customers", f"{data['customers']:,}")
    
    with col2:
        st.metric("📦 Orders", f"{data['orders']:,}")
    
    with col3:
        st.metric("💰 Revenue", f"₹{data['revenue']:,.0f}")
    
    with col4:
        st.metric("📊 Avg Order", f"₹{data['avg_order']:,.0f}")
    
    with col5:
        st.metric("🕐 Last 7 Days", f"{data['recent_orders']:,}")
    
    with col6:
        st.metric("🔁 Repeat", f"{data['repeat_customers']:,}")
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Monthly Order Trends")
        
        # Get monthly data
        monthly_result = table_kpi_engine.calculate_kpi('monthly_trends')
        if monthly_result['success']:
            monthly_df = pd.DataFrame(monthly_result['data'])
            
            if not monthly_df.empty:
                fig = go.Figure()
                
                # Orders line
                fig.add_trace(go.Scatter(
                    x=monthly_df['month_year'],
                    y=monthly_df['total_orders'],
                    mode='lines+markers',
                    name='Orders',
                    line=dict(color='#FF6B35', width=3),
                    marker=dict(size=8)
                ))
                
                # Revenue line
                fig.add_trace(go.Scatter(
                    x=monthly_df['month_year'],
                    y=monthly_df['total_revenue'],
                    mode='lines+markers',
                    name='Revenue (₹)',
                    line=dict(color='#4ECDC4', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Orders",
                    yaxis2=dict(
                        title="Revenue (₹)",
                        overlaying='y',
                        side='right'
                    ),
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No monthly data available")
        else:
            st.error("Failed to load monthly trends")
    
    with col2:
        st.markdown("### 🌍 Regional Revenue Distribution")
        
        # Get regional data
        regional_result = table_kpi_engine.calculate_kpi('regional_revenue')
        if regional_result['success']:
            regional_df = pd.DataFrame(regional_result['data'])
            
            if not regional_df.empty:
                fig = px.pie(
                    regional_df,
                    values='total_revenue',
                    names='region',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>'
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No regional data available")
        else:
            st.error("Failed to load regional revenue")
    
    st.markdown("---")
    
    # Top customers and repeat customers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top Customers (Last 30 Days)")
        
        top_customers_result = table_kpi_engine.calculate_kpi('top_customers', days=30, limit=10)
        if top_customers_result['success']:
            top_df = pd.DataFrame(top_customers_result['data'])
            
            if not top_df.empty:
                # Format the dataframe
                display_df = top_df[['customer_name', 'region', 'order_count', 'total_spend']].copy()
                display_df['total_spend'] = display_df['total_spend'].apply(lambda x: f"₹{float(x):,.2f}")
                display_df.columns = ['Customer', 'Region', 'Orders', 'Total Spend']
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            else:
                st.info("No data available for the last 30 days")
        else:
            st.error("Failed to load top customers")
    
    with col2:
        st.markdown("### 🔁 Repeat Customers")
        
        repeat_result = table_kpi_engine.calculate_kpi('repeat_customers')
        if repeat_result['success']:
            repeat_df = pd.DataFrame(repeat_result['data'])
            
            if not repeat_df.empty:
                # Show top 10 repeat customers
                display_df = repeat_df.head(10)[['customer_name', 'order_count', 'total_spent']].copy()
                display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"₹{float(x):,.2f}")
                display_df.columns = ['Customer', 'Orders', 'Total Spent']
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            else:
                st.info("No repeat customers found")
        else:
            st.error("Failed to load repeat customers")

else:
    st.error("Failed to load overview data. Please check database connection.")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")