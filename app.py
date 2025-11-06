"""
Akasa Air Analytics Dashboard
Main Streamlit Application
"""
import streamlit as st
from datetime import datetime

from config.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    st.markdown(f'<h1 class="main-header">{Config.PAGE_ICON} {Config.PAGE_TITLE}</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✈️ Akasa Air")
        st.markdown("---")
        
        st.markdown("### 📊 Navigation")
        st.info("Use the pages in the sidebar to navigate through different sections.")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # Refresh settings
        if Config.ENABLE_AUTO_REFRESH:
            auto_refresh = st.checkbox("Auto-refresh", value=False)
            if auto_refresh:
                refresh_interval = st.slider(
                    "Refresh interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=Config.AUTO_REFRESH_INTERVAL,
                    step=10
                )
                st.info(f"Dashboard will refresh every {refresh_interval} seconds")
        
        st.markdown("---")
        st.markdown("### 📈 About")
        st.caption(f"""
        **Version:** 1.0  
        **Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
        **Data Source:** MySQL Database
        """)
    
    # Main content
    st.markdown("## 👋 Welcome to Akasa Air Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📊 **Overview Dashboard**\n\nView key metrics and visualizations at a glance")
    
    with col2:
        st.success("📈 **KPI Analytics**\n\nDetailed analysis of business KPIs")
    
    with col3:
        st.warning("⚙️ **Data Management**\n\nUpload and process new data files")
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("## 📊 Quick Stats")
    
    from src.database.db_manager import db_manager
    
    try:
        # Get total customers
        customer_count_query = "SELECT COUNT(*) as count FROM customers"
        customer_result = db_manager.execute_query(customer_count_query)
        total_customers = customer_result[0]['count'] if customer_result else 0
        
        # Get total orders
        order_count_query = "SELECT COUNT(*) as count FROM orders"
        order_result = db_manager.execute_query(order_count_query)
        total_orders = order_result[0]['count'] if order_result else 0
        
        # Get total revenue
        revenue_query = "SELECT SUM(total_amount) as total FROM orders"
        revenue_result = db_manager.execute_query(revenue_query)
        total_revenue = revenue_result[0]['total'] if revenue_result and revenue_result[0]['total'] else 0
        
        # Get average order value
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Customers", f"{total_customers:,}")
        
        with col2:
            st.metric("📦 Total Orders", f"{total_orders:,}")
        
        with col3:
            st.metric("💰 Total Revenue", f"₹{total_revenue:,.2f}")
        
        with col4:
            st.metric("📊 Avg Order Value", f"₹{avg_order:,.2f}")
        
    except Exception as e:
        st.error(f"Error loading quick stats: {e}")
        logger.error(f"Error in main page quick stats: {e}")
    
    st.markdown("---")
    
    # Getting started guide
    with st.expander("🚀 Getting Started Guide", expanded=False):
        st.markdown("""
        ### How to use this dashboard:
        
        1. **📊 Overview Dashboard** - Start here to see the overall business performance
           - View key metrics and trends
           - Interactive charts and visualizations
           - Real-time data updates
        
        2. **📈 KPI Analytics** - Deep dive into specific KPIs
           - Repeat Customers analysis
           - Monthly order trends
           - Regional revenue breakdown
           - Top customers tracking
        
        3. **⚙️ Data Management** - Manage your data
           - Upload new CSV/XML files
           - Process data manually
           - View processing logs
           - Monitor data quality
        
        4. **📋 System Logs** - Monitor system activity
           - View application logs
           - Track data processing
           - Monitor errors
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using Streamlit | © 2025 Akasa Air Analytics"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()