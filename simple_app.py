import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Network Data Explorer",
    page_icon="Network Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for creative styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .stButton>button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #764ba2, #667eea);
        transform: translateY(-2px);
    }
    .data-preview {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .highlight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Data cleaning functions
def clean_data(df):
    """Clean the network dataset"""
    # Make a copy to avoid modifying original
    cleaned_df = df.copy()
    
    # Clean column names
    cleaned_df.columns = cleaned_df.columns.str.strip().str.replace(' ', '_').str.replace('/', '_')
    
    # Replace infinite values with NaN
    cleaned_df = cleaned_df.replace([np.inf, -np.inf], np.nan)
    
    # Handle missing values for numeric columns
    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
    
    # Handle missing values for categorical columns
    categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        cleaned_df[col] = cleaned_df[col].fillna('Unknown')
    
    return cleaned_df

def get_data_summary(df):
    """Get comprehensive data summary"""
    summary = {}
    
    # Basic info
    summary['total_rows'] = len(df)
    summary['total_columns'] = len(df.columns)
    summary['memory_usage'] = df.memory_usage(deep=True).sum() / 1024**2  # MB
    summary['missing_values'] = df.isnull().sum().sum()
    
    # Data types
    summary['numeric_columns'] = len(df.select_dtypes(include=[np.number]).columns)
    summary['text_columns'] = len(df.select_dtypes(include=['object']).columns)
    
    # Traffic analysis (if Label column exists)
    if 'Label' in df.columns:
        label_counts = df['Label'].value_counts()
        summary['benign_count'] = label_counts.get('BENIGN', 0)
        summary['attack_count'] = len(df) - summary['benign_count']
        summary['attack_percentage'] = (summary['attack_count'] / len(df)) * 100
    
    return summary

def create_visualizations(df):
    """Create creative visualizations"""
    figures = {}
    
    # 1. Traffic Distribution (if Label exists)
    if 'Label' in df.columns:
        label_counts = df['Label'].value_counts()
        fig1 = px.pie(
            values=label_counts.values,
            names=label_counts.index,
            title="Network Traffic Distribution",
            color_discrete_map={'BENIGN': '#2E8B57', 'DDoS': '#DC143C', 'Portscan': '#FF8C00'}
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        figures['traffic_dist'] = fig1
    
    # 2. Protocol Distribution
    if 'Protocol' in df.columns:
        protocol_counts = df['Protocol'].value_counts()
        protocol_names = {0: 'HOPOPT', 1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        protocol_counts.index = protocol_counts.index.map(lambda x: protocol_names.get(x, f'Protocol_{x}'))
        
        fig2 = px.bar(
            x=protocol_counts.index,
            y=protocol_counts.values,
            title="Network Protocol Distribution",
            color=protocol_counts.values,
            color_continuous_scale='viridis'
        )
        fig2.update_xaxes(title="Protocol")
        fig2.update_yaxes(title="Count")
        figures['protocol_dist'] = fig2
    
    # 3. Flow Duration Analysis
    if 'Flow_Duration' in df.columns:
        # Create bins for better visualization
        df['duration_bin'] = pd.cut(df['Flow_Duration'], 
                                   bins=[0, 1000, 10000, 100000, 1000000, np.inf],
                                   labels=['<1s', '1-10s', '10-100s', '100-1000s', '>1000s'])
        
        duration_counts = df['duration_bin'].value_counts().sort_index()
        
        fig3 = px.bar(
            x=duration_counts.index,
            y=duration_counts.values,
            title="Flow Duration Distribution",
            color=duration_counts.values,
            color_continuous_scale='plasma'
        )
        fig3.update_xaxes(title="Duration Range")
        fig3.update_yaxes(title="Number of Connections")
        figures['duration_dist'] = fig3
    
    # 4. Packet Analysis
    packet_cols = ['Total_Fwd_Packet', 'Total_Bwd_packets']
    available_packet_cols = [col for col in packet_cols if col in df.columns]
    
    if len(available_packet_cols) >= 2:
        fig4 = go.Figure()
        fig4.add_trace(go.Histogram(
            x=df[available_packet_cols[0]],
            name='Forward Packets',
            opacity=0.7,
            nbinsx=50
        ))
        fig4.add_trace(go.Histogram(
            x=df[available_packet_cols[1]],
            name='Backward Packets',
            opacity=0.7,
            nbinsx=50
        ))
        fig4.update_layout(
            title="Packet Distribution Analysis",
            barmode='overlay',
            xaxis_title="Number of Packets",
            yaxis_title="Frequency"
        )
        figures['packet_analysis'] = fig4
    
    # 5. Heatmap of correlations (for numeric columns)
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:10]  # Limit to first 10 for performance
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        fig5 = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Feature Correlation Heatmap",
            color_continuous_scale='RdBu_r'
        )
        figures['correlation_heatmap'] = fig5
    
    return figures

def main():
    # Header
    st.markdown('<h1 class="main-header">Network Data Explorer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Data Control Panel")
        
        # File selection
        data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
        selected_file = st.selectbox("Select Dataset", data_files)
        
        # Data loading options
        st.subheader("Loading Options")
        sample_size = st.slider("Sample Size (rows)", 100, 10000, 1000)
        show_raw = st.checkbox("Show Raw Data", value=False)
        
        # Data cleaning options
        st.subheader("Data Cleaning")
        clean_missing = st.checkbox("Handle Missing Values", value=True)
        clean_infinite = st.checkbox("Handle Infinite Values", value=True)
        clean_columns = st.checkbox("Clean Column Names", value=True)
        
        # Load data button
        if st.button("Load and Process Data", type="primary"):
            with st.spinner("Loading and processing data..."):
                try:
                    # Load data
                    file_path = os.path.join('data', selected_file)
                    df = pd.read_csv(file_path, nrows=sample_size)
                    
                    # Store in session state
                    st.session_state.raw_data = df
                    st.session_state.file_name = selected_file
                    
                    # Clean data if options selected
                    if clean_missing or clean_infinite or clean_columns:
                        st.session_state.cleaned_data = clean_data(df)
                    else:
                        st.session_state.cleaned_data = df
                    
                    st.success(f"Successfully loaded {len(df)} rows from {selected_file}")
                    
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
    
    # Main content
    if 'cleaned_data' in st.session_state:
        df = st.session_state.cleaned_data
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Data Overview", 
            "Data Cleaning", 
            "Visualizations", 
            "Data Explorer",
            "Export"
        ])
        
        with tab1:
            st.header("Data Overview")
            
            # Summary metrics
            summary = get_data_summary(df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary['total_rows']:,}</h3>
                    <p>Total Rows</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary['total_columns']}</h3>
                    <p>Total Columns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary['memory_usage']:.1f} MB</h3>
                    <p>Memory Usage</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if 'attack_count' in summary:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{summary['attack_count']:,}</h3>
                        <p>Attack Connections</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Data information
            st.subheader("Dataset Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Statistics:**")
                st.write(f"- Numeric Columns: {summary['numeric_columns']}")
                st.write(f"- Text Columns: {summary['text_columns']}")
                st.write(f"- Missing Values: {summary['missing_values']}")
                st.write(f"- Dataset: {st.session_state.file_name}")
            
            with col2:
                if 'attack_percentage' in summary:
                    st.write("**Traffic Analysis:**")
                    st.write(f"- Benign Connections: {summary['benign_count']:,}")
                    st.write(f"- Attack Connections: {summary['attack_count']:,}")
                    st.write(f"- Attack Percentage: {summary['attack_percentage']:.2f}%")
            
            # Data preview
            st.subheader("Data Preview")
            
            if show_raw and 'raw_data' in st.session_state:
                st.write("**Raw Data:**")
                st.dataframe(st.session_state.raw_data.head(10))
            
            st.write("**Cleaned Data:**")
            st.dataframe(df.head(10))
        
        with tab2:
            st.header("Data Cleaning Report")
            
            # Compare raw vs cleaned
            if 'raw_data' in st.session_state:
                raw_df = st.session_state.raw_data
                
                st.subheader("Cleaning Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Before Cleaning:**")
                    st.write(f"- Rows: {len(raw_df):,}")
                    st.write(f"- Missing Values: {raw_df.isnull().sum().sum():,}")
                    st.write(f"- Infinite Values: {(raw_df == np.inf).sum().sum() + (raw_df == -np.inf).sum().sum():,}")
                
                with col2:
                    st.write("**After Cleaning:**")
                    st.write(f"- Rows: {len(df):,}")
                    st.write(f"- Missing Values: {df.isnull().sum().sum():,}")
                    st.write(f"- Infinite Values: {(df == np.inf).sum().sum() + (df == -np.inf).sum().sum():,}")
                
                # Column name changes
                raw_cols = set(raw_df.columns)
                clean_cols = set(df.columns)
                
                if raw_cols != clean_cols:
                    st.subheader("Column Name Changes")
                    changes = {}
                    for old_col in raw_cols:
                        new_col = old_col.strip().replace(' ', '_').replace('/', '_')
                        if old_col != new_col and new_col in clean_cols:
                            changes[old_col] = new_col
                    
                    if changes:
                        changes_df = pd.DataFrame(list(changes.items()), columns=['Original', 'Cleaned'])
                        st.dataframe(changes_df)
        
        with tab3:
            st.header("Data Visualizations")
            
            # Create visualizations
            figures = create_visualizations(df)
            
            if figures:
                # Display visualizations in a grid
                viz_cols = st.columns(2)
                
                for i, (name, fig) in enumerate(figures.items()):
                    with viz_cols[i % 2]:
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(f"Figure: {name.replace('_', ' ').title()}")
            else:
                st.info("No visualizations available for the current dataset.")
        
        with tab4:
            st.header("Interactive Data Explorer")
            
            # Column selection
            st.subheader("Column Explorer")
            
            all_columns = df.columns.tolist()
            selected_columns = st.multiselect(
                "Select columns to explore:",
                all_columns,
                default=all_columns[:5]
            )
            
            if selected_columns:
                # Data filtering
                st.subheader("Data Filtering")
                
                # Numeric filters
                numeric_cols = df[selected_columns].select_dtypes(include=[np.number]).columns
                
                if len(numeric_cols) > 0:
                    filter_col = st.selectbox("Select column to filter", numeric_cols)
                    
                    if filter_col:
                        min_val = df[filter_col].min()
                        max_val = df[filter_col].max()
                        
                        filter_range = st.slider(
                            f"Filter {filter_col}",
                            float(min_val),
                            float(max_val),
                            (float(min_val), float(max_val))
                        )
                        
                        filtered_df = df[
                            (df[filter_col] >= filter_range[0]) & 
                            (df[filter_col] <= filter_range[1])
                        ]
                        
                        st.write(f"Filtered data: {len(filtered_df)} rows ({len(filtered_df)/len(df)*100:.1f}%)")
                        st.dataframe(filtered_df[selected_columns].head(100))
                else:
                    st.dataframe(df[selected_columns].head(100))
            
            # Statistics
            st.subheader("Column Statistics")
            
            if selected_columns:
                stats_df = df[selected_columns].describe()
                st.dataframe(stats_df)
        
        with tab5:
            st.header("Export Data")
            
            st.subheader("Export Options")
            
            # Export format selection
            export_format = st.radio("Select export format:", ["CSV", "JSON", "Excel"])
            
            # Export options
            include_stats = st.checkbox("Include summary statistics", value=True)
            include_visualizations = st.checkbox("Include visualization data", value=False)
            
            if st.button("Export Data", type="primary"):
                try:
                    # Prepare export data
                    export_data = df
                    
                    if export_format == "CSV":
                        csv_data = export_data.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"network_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    elif export_format == "JSON":
                        json_data = export_data.to_json(orient='records', indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"network_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    elif export_format == "Excel":
                        excel_data = export_data.to_excel(index=False)
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=f"network_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    st.success("Data prepared for export!")
                    
                except Exception as e:
                    st.error(f"Export error: {str(e)}")
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to Network Data Explorer! 
        
        This creative tool helps you explore and clean network traffic data with beautiful visualizations.
        
        ### Features:
        - **Data Loading**: Load network traffic datasets with flexible options
        - **Data Cleaning**: Handle missing values, infinite values, and clean column names
        - **Visualizations**: Create beautiful charts and graphs
        - **Interactive Explorer**: Filter and analyze data interactively
        - **Export Options**: Download cleaned data in multiple formats
        
        ### Getting Started:
        1. Select a dataset from the sidebar
        2. Choose your data loading and cleaning options
        3. Click "Load and Process Data"
        4. Explore the different tabs to analyze your data
        
        ---
        **Ready to explore your network data? Start by selecting a dataset from the sidebar!**
        """)

if __name__ == "__main__":
    main()
