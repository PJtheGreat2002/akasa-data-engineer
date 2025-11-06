"""
System Logs - View application logs
"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import re

from config.config import Config

st.set_page_config(
    page_title="System Logs",
    page_icon="📋",
    layout="wide"
)

st.title("📋 System Logs")
st.markdown("View application logs and system activity")

# Get log file
log_file = Config.LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Log Controls")
    
    # Log level filter
    log_levels = st.multiselect(
        "Filter by Level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=["INFO", "WARNING", "ERROR"]
    )
    
    # Search
    search_term = st.text_input("🔍 Search logs", "")
    
    # Refresh button
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Log file info
    if log_file.exists():
        file_size = log_file.stat().st_size / 1024  # KB
        st.info(f"**Log File:** {log_file.name}\n\n**Size:** {file_size:.2f} KB")
    else:
        st.warning("No log file found for today")

# Main content
if log_file.exists():
    try:
        # Read log file
        with open(log_file, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        st.info(f"📄 Total log entries: {len(log_lines)}")
        
        # Filter logs
        filtered_logs = []
        for line in log_lines:
            # Filter by log level
            if any(level in line for level in log_levels):
                # Filter by search term
                if not search_term or search_term.lower() in line.lower():
                    filtered_logs.append(line)
        
        st.success(f"✅ Showing {len(filtered_logs)} entries after filtering")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 All Logs", "📊 Summary", "⚠️ Errors Only"])
        
        with tab1:
            st.markdown("### 📋 Full Log View")
            
            # Display options
            col1, col2 = st.columns([3, 1])
            with col1:
                max_lines = st.slider("Max lines to display", 10, 500, 100)
            with col2:
                reverse_order = st.checkbox("Newest first", value=True)
            
            # Display logs
            display_logs = filtered_logs[-max_lines:] if not reverse_order else filtered_logs[-max_lines:][::-1]
            
            log_text = "".join(display_logs)
            
            # Color code by log level
            def colorize_log(log_text):
                # ERROR - red
                log_text = re.sub(r'(ERROR.*)', r'🔴 \1', log_text)
                # WARNING - yellow
                log_text = re.sub(r'(WARNING.*)', r'🟡 \1', log_text)
                # INFO - green
                log_text = re.sub(r'(INFO.*)', r'🟢 \1', log_text)
                # DEBUG - blue
                log_text = re.sub(r'(DEBUG.*)', r'🔵 \1', log_text)
                # CRITICAL - purple
                log_text = re.sub(r'(CRITICAL.*)', r'🟣 \1', log_text)
                return log_text
            
            colored_logs = colorize_log(log_text)
            st.text_area("Logs", colored_logs, height=600, label_visibility="collapsed")
            
            # Download button
            st.download_button(
                label="📥 Download Full Log",
                data=log_text,
                file_name=log_file.name,
                mime="text/plain"
            )
        
        with tab2:
            st.markdown("### 📊 Log Summary")
            
            # Count by log level
            level_counts = {
                "DEBUG": sum(1 for line in log_lines if "DEBUG" in line),
                "INFO": sum(1 for line in log_lines if "INFO" in line),
                "WARNING": sum(1 for line in log_lines if "WARNING" in line),
                "ERROR": sum(1 for line in log_lines if "ERROR" in line),
                "CRITICAL": sum(1 for line in log_lines if "CRITICAL" in line)
            }
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("🔵 DEBUG", level_counts['DEBUG'])
            with col2:
                st.metric("🟢 INFO", level_counts['INFO'])
            with col3:
                st.metric("🟡 WARNING", level_counts['WARNING'])
            with col4:
                st.metric("🔴 ERROR", level_counts['ERROR'])
            with col5:
                st.metric("🟣 CRITICAL", level_counts['CRITICAL'])
            
            st.markdown("---")
            
            # Recent activity
            st.markdown("### 🕐 Recent Activity")
            
            recent_logs = log_lines[-20:][::-1]
            for log in recent_logs:
                if "ERROR" in log or "CRITICAL" in log:
                    st.error(log.strip())
                elif "WARNING" in log:
                    st.warning(log.strip())
                else:
                    st.info(log.strip())
        
        with tab3:
            st.markdown("### ⚠️ Errors and Warnings")
            
            # Filter only errors and warnings
            error_logs = [line for line in log_lines if "ERROR" in line or "WARNING" in line or "CRITICAL" in line]
            
            if error_logs:
                st.error(f"Found {len(error_logs)} errors/warnings")
                
                for log in error_logs[-50:][::-1]:  # Last 50 errors
                    if "ERROR" in log or "CRITICAL" in log:
                        st.error(log.strip())
                    else:
                        st.warning(log.strip())
            else:
                st.success("✅ No errors or warnings found!")
    
    except Exception as e:
        st.error(f"Error reading log file: {e}")
else:
    st.warning("No log file found for today. Logs will be created when the application runs.")
    
    st.markdown("### 📝 Log File Location")
    st.code(str(Config.LOG_DIR))

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")