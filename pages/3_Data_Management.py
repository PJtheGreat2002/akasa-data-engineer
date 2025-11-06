"""
Data Management - Upload and process data files
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

from config.config import Config
from src.ingestion.csv_loader import csv_loader
from src.ingestion.xml_loader import xml_loader
from src.database.db_manager import db_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

st.set_page_config(
    page_title="Data Management",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Data Management")
st.markdown("Upload and process customer and order data files")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Files", "🔄 Process Data", "📊 Data Status", "🗑️ Clear Data"])

# TAB 1: Upload Files
with tab1:
    st.markdown("## 📤 Upload Data Files")
    st.markdown("Upload CSV files for customers and XML files for orders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Customer Data (CSV)")
        
        # File uploader for CSV
        csv_file = st.file_uploader(
            "Upload customers.csv",
            type=['csv'],
            help="CSV file containing customer information"
        )
        
        if csv_file is not None:
            try:
                # Preview the file
                df = pd.read_csv(csv_file)
                st.success(f"✅ File loaded: {len(df)} rows")
                
                with st.expander("📋 Preview Data", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                
                # Save button
                if st.button("💾 Save Customer Data", key="save_csv", use_container_width=True):
                    # Save to raw data directory
                    save_path = Config.RAW_DATA_DIR / "customers.csv"
                    df.to_csv(save_path, index=False)
                    st.success(f"✅ File saved to {save_path}")
                    logger.info(f"Customer CSV uploaded: {save_path}")
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {e}")
                logger.error(f"Error reading CSV upload: {e}")
    
    with col2:
        st.markdown("### 📦 Order Data (XML)")
        
        # File uploader for XML
        xml_file = st.file_uploader(
            "Upload orders.xml",
            type=['xml'],
            help="XML file containing order information"
        )
        
        if xml_file is not None:
            try:
                # Preview the file
                content = xml_file.read().decode('utf-8')
                st.success(f"✅ File loaded: {len(content)} characters")
                
                with st.expander("📋 Preview Data", expanded=True):
                    st.code(content[:1000] + "..." if len(content) > 1000 else content, language="xml")
                
                # Save button
                if st.button("💾 Save Order Data", key="save_xml", use_container_width=True):
                    # Save to raw data directory
                    save_path = Config.RAW_DATA_DIR / "orders.xml"
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    st.success(f"✅ File saved to {save_path}")
                    logger.info(f"Order XML uploaded: {save_path}")
                    
            except Exception as e:
                st.error(f"❌ Error reading XML file: {e}")
                logger.error(f"Error reading XML upload: {e}")
    
    st.markdown("---")
    st.info("💡 **Tip:** After uploading files, go to the 'Process Data' tab to load them into the database.")

# TAB 2: Process Data
with tab2:
    st.markdown("## 🔄 Process Data Files")
    st.markdown("Load uploaded files into the database")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Process Customer Data")
        
        # Check if file exists
        csv_path = Config.RAW_DATA_DIR / "customers.csv"
        if csv_path.exists():
            st.success(f"✅ File found: {csv_path.name}")
            
            # Show file info
            df = pd.read_csv(csv_path)
            st.info(f"📊 Records in file: {len(df)}")
            
            # Processing mode
            csv_mode = st.radio(
                "Processing Mode",
                ["replace", "append"],
                help="Replace: Clear existing data | Append: Add to existing data",
                key="csv_mode"
            )
            
            # Process button
            if st.button("▶️ Process Customer Data", key="process_csv", use_container_width=True, type="primary"):
                with st.spinner("Processing customer data..."):
                    result = csv_loader.process_csv(csv_path, mode=csv_mode)
                
                if result['success']:
                    st.success(f"✅ Successfully processed {result['records_loaded']} customer records")
                    st.info(f"⏱️ Duration: {result['duration']:.2f} seconds")
                    logger.info(f"Customer data processed: {result['records_loaded']} records")
                else:
                    st.error("❌ Processing failed")
                    for error in result['errors']:
                        st.error(f"• {error}")
                    logger.error(f"Customer data processing failed: {result['errors']}")
        else:
            st.warning(f"⚠️ File not found: {csv_path.name}")
            st.info("Please upload a customer CSV file first")
    
    with col2:
        st.markdown("### 📦 Process Order Data")
        
        # Check if file exists
        xml_path = Config.RAW_DATA_DIR / "orders.xml"
        if xml_path.exists():
            st.success(f"✅ File found: {xml_path.name}")
            
            # Show file info
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_path)
            root = tree.getroot()
            order_count = len(root.findall('order'))
            st.info(f"📊 Records in file: {order_count}")
            
            # Processing mode
            xml_mode = st.radio(
                "Processing Mode",
                ["replace", "append"],
                help="Replace: Clear existing data | Append: Add to existing data",
                key="xml_mode"
            )
            
            # Process button
            if st.button("▶️ Process Order Data", key="process_xml", use_container_width=True, type="primary"):
                with st.spinner("Processing order data..."):
                    result = xml_loader.process_xml(xml_path, mode=xml_mode)
                
                if result['success']:
                    st.success(f"✅ Successfully processed {result['records_loaded']} order records")
                    st.info(f"⏱️ Duration: {result['duration']:.2f} seconds")
                    logger.info(f"Order data processed: {result['records_loaded']} records")
                else:
                    st.error("❌ Processing failed")
                    for error in result['errors']:
                        st.error(f"• {error}")
                    logger.error(f"Order data processing failed: {result['errors']}")
        else:
            st.warning(f"⚠️ File not found: {xml_path.name}")
            st.info("Please upload an order XML file first")
    
    st.markdown("---")
    
    # Process both at once
    st.markdown("### ⚡ Quick Process")
    st.markdown("Process both customer and order data files at once")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        both_mode = st.radio(
            "Processing Mode for Both",
            ["replace", "append"],
            help="Apply to both files",
            key="both_mode",
            horizontal=True
        )
    
    with col2:
        if st.button("▶️ Process Both", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process CSV
            status_text.text("Processing customers...")
            csv_result = csv_loader.process_csv(mode=both_mode)
            progress_bar.progress(50)
            
            # Process XML
            status_text.text("Processing orders...")
            xml_result = xml_loader.process_xml(mode=both_mode)
            progress_bar.progress(100)
            
            status_text.empty()
            progress_bar.empty()
            
            # Show results
            if csv_result['success'] and xml_result['success']:
                st.success(f"✅ All data processed successfully!")
                st.info(f"Customers: {csv_result['records_loaded']} | Orders: {xml_result['records_loaded']}")
            else:
                st.error("❌ Some processing failed")
                if not csv_result['success']:
                    st.error(f"Customer errors: {csv_result['errors']}")
                if not xml_result['success']:
                    st.error(f"Order errors: {xml_result['errors']}")

# TAB 3: Data Status
with tab3:
    st.markdown("## 📊 Database Status")
    
    try:
        # Customer stats
        customer_query = """
            SELECT 
                COUNT(*) as total_customers,
                COUNT(DISTINCT region) as total_regions,
                MIN(created_at) as first_created,
                MAX(created_at) as last_created
            FROM customers
        """
        customer_stats = db_manager.execute_query(customer_query)[0]
        
        # Order stats
        order_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                MIN(order_date_time) as earliest_order,
                MAX(order_date_time) as latest_order,
                COUNT(DISTINCT sku_id) as unique_skus
            FROM orders
        """
        order_stats = db_manager.execute_query(order_query)[0]
        
        # Display stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Customer Data")
            st.metric("Total Customers", f"{customer_stats['total_customers']:,}")
            st.metric("Regions", f"{customer_stats['total_regions']:,}")
            if customer_stats['first_created']:
                st.caption(f"First record: {customer_stats['first_created']}")
            if customer_stats['last_created']:
                st.caption(f"Last record: {customer_stats['last_created']}")
        
        with col2:
            st.markdown("### 📦 Order Data")
            st.metric("Total Orders", f"{order_stats['total_orders']:,}")
            st.metric("Total Revenue", f"₹{float(order_stats['total_revenue'] or 0):,.2f}")
            st.metric("Avg Order Value", f"₹{float(order_stats['avg_order_value'] or 0):,.2f}")
            st.metric("Unique SKUs", f"{order_stats['unique_skus']:,}")
            if order_stats['earliest_order']:
                st.caption(f"Earliest: {order_stats['earliest_order']}")
            if order_stats['latest_order']:
                st.caption(f"Latest: {order_stats['latest_order']}")
        
        st.markdown("---")
        
        # Recent activity
        st.markdown("### 🕐 Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Recent Customers**")
            recent_customers = db_manager.execute_query(
                "SELECT customer_id, customer_name, region, created_at FROM customers ORDER BY created_at DESC LIMIT 5"
            )
            if recent_customers:
                df = pd.DataFrame(recent_customers)
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Recent Orders**")
            recent_orders = db_manager.execute_query(
                "SELECT order_id, mobile_number, total_amount, order_date_time FROM orders ORDER BY order_date_time DESC LIMIT 5"
            )
            if recent_orders:
                df = pd.DataFrame(recent_orders)
                st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error loading database status: {e}")
        logger.error(f"Error in data status tab: {e}")

# TAB 4: Clear Data
with tab4:
    st.markdown("## 🗑️ Clear Database")
    st.warning("⚠️ **Warning:** This action will delete data from the database. This cannot be undone!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👥 Clear Customers")
        if st.button("🗑️ Clear Customer Data", key="clear_customers", use_container_width=True):
            confirm = st.checkbox("I understand this will delete all customer data", key="confirm_customers")
            if confirm:
                try:
                    db_manager.execute_query("DELETE FROM customers", fetch=False)
                    st.success("✅ Customer data cleared")
                    logger.info("Customer data cleared from database")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    logger.error(f"Error clearing customers: {e}")
    
    with col2:
        st.markdown("### 📦 Clear Orders")
        if st.button("🗑️ Clear Order Data", key="clear_orders", use_container_width=True):
            confirm = st.checkbox("I understand this will delete all order data", key="confirm_orders")
            if confirm:
                try:
                    db_manager.execute_query("DELETE FROM orders", fetch=False)
                    st.success("✅ Order data cleared")
                    logger.info("Order data cleared from database")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    logger.error(f"Error clearing orders: {e}")
    
    with col3:
        st.markdown("### 🗑️ Clear All Data")
        if st.button("🗑️ Clear All Data", key="clear_all", use_container_width=True, type="primary"):
            confirm = st.checkbox("I understand this will delete ALL data", key="confirm_all")
            if confirm:
                try:
                    db_manager.execute_query("DELETE FROM orders", fetch=False)
                    db_manager.execute_query("DELETE FROM customers", fetch=False)
                    st.success("✅ All data cleared")
                    logger.info("All data cleared from database")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    logger.error(f"Error clearing all data: {e}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")