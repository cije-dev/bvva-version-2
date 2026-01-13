"""
Data Analyzer Pro - Web Version
A professional-grade data analysis web application built with Streamlit
Author: Development Team
Date: 2026
"""

import streamlit as st
import pandas as pd
import io
import sys
import os
import hashlib
import time
from pathlib import Path

# Try to import keyboard automation libraries
try:
    import pyautogui
    import pyperclip
    from PIL import Image
    try:
        import pytesseract
        OCR_AVAILABLE = True
    except ImportError:
        OCR_AVAILABLE = False
        pytesseract = None  # type: ignore
    KEYBOARD_AUTOMATION_AVAILABLE = True
except ImportError:
    KEYBOARD_AUTOMATION_AVAILABLE = False
    OCR_AVAILABLE = False
    pyautogui = None  # type: ignore
    pyperclip = None  # type: ignore
    Image = None  # type: ignore
    pytesseract = None  # type: ignore

# Get password from command line arguments or environment variable
def get_password():
    """Get password from command line args or environment variable"""
    # Check command line arguments (e.g., --password=secret)
    for arg in sys.argv:
        if arg.startswith('--password='):
            return arg.split('=', 1)[1]
    
    # Check environment variable
    return os.getenv('DATA_ANALYZER_PASSWORD', None)

# Get the password set at launch
APP_PASSWORD = get_password()

# Page configuration
st.set_page_config(
    page_title="Data Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #14b8a6;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #0f172a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid;
    }
    </style>
""", unsafe_allow_html=True)


def extract_base_name(base_value):
    """Extract base name from format like '20221-US-LY' -> 'LY' (part after 'US-')"""
    if not base_value or base_value == 'NAN' or base_value == 'NONE':
        return None
    
    base_str = str(base_value).strip().upper()
    
    # Look for pattern: anything-US-XXX
    if '-US-' in base_str:
        parts = base_str.split('-US-')
        if len(parts) > 1:
            base_name = parts[-1].strip()
            return base_name if base_name else None
    
    # If pattern doesn't match, return the original value
    return base_str if base_str else None


def calculate_statistics(data, checker_col):
    """Calculate statistics for approval status"""
    if data is None or len(data) == 0:
        return {'approved': 0, 'not_approved': 0, 'not_in_time': 0, 'total': 0}
    
    if checker_col not in data.columns:
        return {'approved': 0, 'not_approved': 0, 'not_in_time': 0, 'total': 0}
    
    checker_series = data[checker_col].astype(str).str.lower()
    
    approved = len(data[checker_series.str.contains('approved', na=False) & 
                           ~checker_series.str.contains('not approved', na=False)])
    not_approved = len(data[checker_series.str.contains('not approved', na=False)])
    not_in_time = len(data[checker_series.str.contains('not in time', na=False)])
    total = len(data)
    
    return {
        'approved': approved,
        'not_approved': not_approved,
        'not_in_time': not_in_time,
        'total': total
    }


def calculate_base_statistics(data, base_name, base_name_mapping, base_col, checker_col):
    """Calculate statistics for a specific base (extracted base name)"""
    if data is None or len(data) == 0:
        return {'total': 0, 'approved': 0, 'not_approved': 0, 'not_in_time': 0}
    
    if base_col is None or checker_col not in data.columns:
        return {'total': 0, 'approved': 0, 'not_approved': 0, 'not_in_time': 0}
    
    # Get all original base values that belong to this extracted base name
    original_values = base_name_mapping.get(base_name, [])
    if not original_values:
        return {'total': 0, 'approved': 0, 'not_approved': 0, 'not_in_time': 0}
    
    # Filter by all original values that belong to this base name
    base_series = data[base_col].astype(str).str.strip().str.upper()
    mask = base_series.isin(original_values)
    base_data = data[mask]
    
    if len(base_data) == 0:
        return {'total': 0, 'approved': 0, 'not_approved': 0, 'not_in_time': 0}
    
    checker_series = base_data[checker_col].astype(str).str.lower()
    
    approved = len(base_data[checker_series.str.contains('approved', na=False) & 
                                  ~checker_series.str.contains('not approved', na=False)])
    not_approved = len(base_data[checker_series.str.contains('not approved', na=False)])
    not_in_time = len(base_data[checker_series.str.contains('not in time', na=False)])
    total = len(base_data)
    
    return {
        'total': total,
        'approved': approved,
        'not_approved': not_approved,
        'not_in_time': not_in_time
    }


# Password authentication
def check_password(password_input):
    """Check if entered password matches the app password"""
    if APP_PASSWORD is None:
        # If no password is set, allow access (for development)
        return True
    
    # Simple password comparison (you could hash it for more security)
    return password_input == APP_PASSWORD

# Show password entry if not authenticated
if not st.session_state.authenticated:
    if APP_PASSWORD is None:
        st.warning("⚠️ No password set. Run with --password=YOUR_PASSWORD or set DATA_ANALYZER_PASSWORD environment variable.")
        st.session_state.authenticated = True  # Allow access if no password set
    else:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 80vh;">
            <div style="text-align: center;">
                <h1 style="font-size: 3rem; margin-bottom: 2rem;">🔒 Data Analyzer Pro</h1>
                <p style="font-size: 1.2rem; color: #666;">Please enter the password to access the application</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            password_input = st.text_input(
                "Password:",
                type="password",
                key="password_input",
                help="Enter the password set when launching the server"
            )
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("🔓 Login", type="primary", use_container_width=True):
                    if check_password(password_input):
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password. Please try again.")
            
            with col_b:
                if st.button("🔄 Clear", use_container_width=True):
                    st.session_state.password_input = ""
                    st.rerun()
        
        st.stop()  # Stop execution here if not authenticated

# Initialize session state (only reached if authenticated)
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'base_name_mapping' not in st.session_state:
    st.session_state.base_name_mapping = {}
if 'selected_bases' not in st.session_state:
    st.session_state.selected_bases = []


# Sidebar
with st.sidebar:
    st.markdown('<h1 style="font-size: 1.5rem; font-weight: bold;">📊 Analyzer</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### FILE OPERATIONS")
    
    # Check for existing files in data directory
    data_dir = Path("data")
    existing_files = []
    if data_dir.exists():
        existing_files = [f for f in data_dir.iterdir() 
                         if f.is_file() and f.suffix.lower() in ['.xlsx', '.xls', '.csv']]
        existing_files = sorted(existing_files, key=lambda x: x.name)
    
    # File source selection
    file_source = st.radio(
        "File Source:",
        ["📤 Upload File", "📁 Load from Data Folder"],
        key="file_source"
    )
    
    uploaded_file = None
    
    if file_source == "📤 Upload File":
        uploaded_file = st.file_uploader(
            "📁 Upload Excel/CSV",
            type=['xlsx', 'xls', 'csv'],
            help="Upload an Excel or CSV file to analyze"
        )
    else:
        # Load from data directory
        if existing_files:
            file_options = ["-- Select a file --"] + [f.name for f in existing_files]
            selected_file_name = st.selectbox(
                "📁 Select file from data folder:",
                file_options,
                key="data_file_selector"
            )
            
            if selected_file_name != "-- Select a file --":
                selected_file_path = data_dir / selected_file_name
                # Read file into BytesIO to simulate file upload
                with open(selected_file_path, 'rb') as f:
                    file_bytes = f.read()
                    # Create a file-like object
                    uploaded_file = io.BytesIO(file_bytes)
                    uploaded_file.name = selected_file_name
        else:
            st.info("No files found in the 'data' folder. Please upload a file or add files to the data folder.")
            # Also show upload option as fallback
            uploaded_file = st.file_uploader(
                "📁 Or upload a file:",
                type=['xlsx', 'xls', 'csv'],
                help="Upload an Excel or CSV file to analyze",
                key="fallback_uploader"
            )
    
    if uploaded_file is not None:
        try:
            file_ext = Path(uploaded_file.name).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.original_df = df.copy()
                st.success(f"✓ CSV file loaded successfully! ({len(df)} rows)")
            else:
                # Read Excel file
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                
                if len(sheet_names) > 1:
                    selected_sheets = st.multiselect(
                        "Select sheets to load:",
                        sheet_names,
                        default=sheet_names,
                        key="sheet_selector"
                    )
                    
                    if selected_sheets:
                        dfs_list = []
                        for sheet_name in selected_sheets:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                            dfs_list.append(df)
                        
                        if dfs_list:
                            combined_df = pd.concat(dfs_list, ignore_index=True)
                            st.session_state.df = combined_df
                            st.session_state.original_df = combined_df.copy()
                            st.success(f"✓ {len(selected_sheets)} sheet(s) loaded successfully! ({len(combined_df)} rows)")
                else:
                    df = pd.read_excel(uploaded_file)
                    st.session_state.df = df
                    st.session_state.original_df = df.copy()
                    st.success(f"✓ Excel file loaded successfully! ({len(df)} rows)")
                
                # Update base mapping
                if st.session_state.df is not None:
                    base_col = None
                    for col in st.session_state.df.columns:
                        if col.lower() in ['base', 'bases', 'base name', 'basename']:
                            base_col = col
                            break
                    
                    if base_col:
                        base_values = st.session_state.df[base_col].astype(str).str.strip().str.upper()
                        unique_base_values = [b for b in base_values.unique() if b and b != 'NAN' and b != 'NONE']
                        
                        base_name_mapping = {}
                        for base_value in unique_base_values:
                            extracted_name = extract_base_name(base_value)
                            if extracted_name:
                                if extracted_name not in base_name_mapping:
                                    base_name_mapping[extracted_name] = []
                                base_name_mapping[extracted_name].append(base_value)
                        
                        st.session_state.base_name_mapping = base_name_mapping
                        st.session_state.selected_bases = list(base_name_mapping.keys())
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    st.markdown("---")
    st.markdown("### FILTER BY STATUS")
    
    status_filter = st.radio(
        "Filter by status:",
        ["Show All", "Approved", "Not Approved", "Not in Time"],
        key="status_filter"
    )
    
    st.markdown("---")
    st.markdown("### NAVIGATION")
    
    page = st.radio(
        "Navigate to:",
        ["📋 Data View", "📈 Analytics", "🔍 Search", "🔗 Combine", "📍 Bases", "💳 Test Card"],
        key="page_nav"
    )


# Main content
st.markdown('<div class="main-header">Data Analyzer Pro</div>', unsafe_allow_html=True)

if st.session_state.df is None:
    st.info("👈 Please upload an Excel or CSV file from the sidebar to get started.")
    st.markdown("""
    ### Features:
    - 📊 Load and analyze Excel/CSV files
    - 📈 View analytics and statistics
    - 🔍 Search through data
    - 🔗 Combine base names for analysis
    - 📍 Filter by base names with statistics
    """)
else:
    if st.session_state.df is None or st.session_state.original_df is None:
        st.info("👈 Please upload an Excel or CSV file from the sidebar to get started.")
        st.stop()
    
    df = st.session_state.df.copy()
    original_df = st.session_state.original_df.copy()
    
    # Find columns
    base_col = None
    checker_col = None
    
    for col in df.columns:
        if col.lower() in ['base', 'bases', 'base name', 'basename']:
            base_col = col
        if col.lower() in ['checker', 'check']:
            checker_col = col
    
    if checker_col is None:
        checker_col = 'Checker' if 'Checker' in df.columns else 'checker'
    
    # Apply status filter
    if status_filter != "Show All" and checker_col in df.columns:
        checker_series = df[checker_col].astype(str).str.lower()
        
        if status_filter == "Approved":
            df = df[checker_series.str.contains('approved', na=False) & 
                    ~checker_series.str.contains('not approved', na=False)]
        elif status_filter == "Not Approved":
            df = df[checker_series.str.contains('not approved', na=False)]
        elif status_filter == "Not in Time":
            df = df[checker_series.str.contains('not in time', na=False)]
    
    # Page routing
    if page == "📋 Data View":
        st.markdown("### Data View")
        
        # Search box
        search_term = st.text_input("🔍 Search by any field...", key="data_search")
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df = df[mask]
        
        st.dataframe(df, use_container_width=True, height=600)
        st.caption(f"Showing {len(df)} of {len(original_df)} rows")
        
    elif page == "📈 Analytics":
        st.markdown("### Analytics Dashboard")
        
        stats = calculate_statistics(original_df, checker_col) if checker_col in original_df.columns else {}
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            approved_pct = (stats.get('approved', 0) / stats.get('total', 1) * 100) if stats.get('total', 0) > 0 else 0
            st.metric(
                "✓ APPROVED",
                f"{stats.get('approved', 0)}",
                f"{approved_pct:.1f}%"
            )
            st.progress(approved_pct / 100)
        
        with col2:
            not_approved_pct = (stats.get('not_approved', 0) / stats.get('total', 1) * 100) if stats.get('total', 0) > 0 else 0
            st.metric(
                "✗ NOT APPROVED",
                f"{stats.get('not_approved', 0)}",
                f"{not_approved_pct:.1f}%"
            )
            st.progress(not_approved_pct / 100)
        
        with col3:
            not_in_time_pct = (stats.get('not_in_time', 0) / stats.get('total', 1) * 100) if stats.get('total', 0) > 0 else 0
            st.metric(
                "⏱ NOT IN TIME",
                f"{stats.get('not_in_time', 0)}",
                f"{not_in_time_pct:.1f}%"
            )
            st.progress(not_in_time_pct / 100)
        
        st.markdown("---")
        st.markdown(f"**Total Records:** {stats.get('total', 0)}")
        
    elif page == "🔍 Search":
        st.markdown("### Search Terms")
        
        search_term = st.text_input("Enter search term (partial matches)...", key="search_input")
        
        if st.button("Search", type="primary"):
            if search_term:
                mask = original_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                results = original_df[mask]
                
                if len(results) == 0:
                    st.info(f"No results found for '{search_term}'")
                else:
                    st.success(f"Found {len(results)} result(s)")
                    st.dataframe(results, use_container_width=True, height=600)
            else:
                st.warning("Please enter a search term")
    
    elif page == "🔗 Combine":
        st.markdown("### Combine Base Names")
        
        col1, col2 = st.columns(2)
        
        with col1:
            base1 = st.text_input("First base name (e.g., MYWE)...", key="base1")
        
        with col2:
            base2 = st.text_input("Second base name (e.g., FISH)...", key="base2")
        
        if st.button("Combine", type="primary"):
            if base1 and base2 and base_col:
                base1_upper = base1.upper().strip()
                base2_upper = base2.upper().strip()
                
                combined = original_df[
                    original_df[base_col].astype(str).str.contains(base1_upper, case=False, na=False) |
                    original_df[base_col].astype(str).str.contains(base2_upper, case=False, na=False)
                ]
                
                if len(combined) == 0:
                    st.info("No records found for these base names")
                else:
                    stats = calculate_statistics(combined, checker_col)
                    total = stats.get('total', 0)
                    approved = stats.get('approved', 0)
                    not_approved = stats.get('not_approved', 0)
                    not_in_time = stats.get('not_in_time', 0)
                    
                    approved_pct = (approved / total * 100) if total > 0 else 0
                    not_approved_pct = (not_approved / total * 100) if total > 0 else 0
                    not_in_time_pct = (not_in_time / total * 100) if total > 0 else 0
                    
                    st.success(f"Combined Results:")
                    st.metric("Total Records", total)
                    st.metric("✓ Approved", f"{approved} ({approved_pct:.1f}%)")
                    st.metric("✗ Not Approved", f"{not_approved} ({not_approved_pct:.1f}%)")
                    st.metric("⏱ Not in Time", f"{not_in_time} ({not_in_time_pct:.1f}%)")
                    
                    st.dataframe(combined, use_container_width=True, height=400)
            else:
                st.warning("Please enter both base names")
    
    elif page == "💳 Test Card":
        st.markdown("### Test Card - PayAByPhone Automation")
        
        if not KEYBOARD_AUTOMATION_AVAILABLE:
            st.error("Keyboard automation libraries are not installed. Please install: pip install pyautogui pyperclip")
        else:
            # Initialize selected row index in session state
            if 'selected_test_row_index' not in st.session_state:
                st.session_state.selected_test_row_index = None
            
            # Find number/card column for display
            number_col = None
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['number', 'card number', 'cardnumber', 'card', 'num']:
                    number_col = col
                    break
            
            # Search box (like Data View)
            search_term = st.text_input("🔍 Search by any field...", key="test_card_search")
            display_df = df.copy()
            if search_term:
                mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                display_df = display_df[mask]
            
            # Add a "Select" checkbox column for row selection
            display_df_with_index = display_df.reset_index(drop=True)
            
            # Initialize selected row index if not set
            if 'selected_test_row_index' not in st.session_state:
                st.session_state.selected_test_row_index = 0 if len(display_df) > 0 else None
            
            # Add checkbox column for selection
            if len(display_df) > 0:
                # Create a copy with a Select column
                display_df_with_select = display_df_with_index.copy()
                
                # Initialize Select column - only the selected row is True
                select_values = [False] * len(display_df_with_select)
                if st.session_state.selected_test_row_index is not None and st.session_state.selected_test_row_index < len(select_values):
                    select_values[st.session_state.selected_test_row_index] = True
                
                display_df_with_select.insert(0, '✓ Select', select_values)
                
                # Configure columns - make Select editable, others read-only
                column_config = {}
                column_config['✓ Select'] = st.column_config.CheckboxColumn(
                    "Select",
                    help="Check this box to select the row for testing",
                    default=False,
                    width="small"
                )
                for col in display_df_with_index.columns:
                    column_config[col] = st.column_config.Column(disabled=True)
                
                # Display editable dataframe
                edited_df = st.data_editor(
                    display_df_with_select,
                    use_container_width=True,
                    height=400,
                    column_config=column_config,
                    key="test_card_editor",
                    hide_index=True,
                    num_rows="fixed"
                )
                
                # Find which row is selected (has checkmark)
                selected_option = None
                if '✓ Select' in edited_df.columns:
                    selected_rows = edited_df[edited_df['✓ Select'] == True]
                    if len(selected_rows) > 0:
                        # Get the first selected row index
                        selected_option = selected_rows.index[0]
                        # If multiple selected, keep only the first one (uncheck others on next render)
                        if len(selected_rows) > 1:
                            # Update session state to first selected
                            st.session_state.selected_test_row_index = selected_option
                            st.rerun()
                
                # Update session state when selection changes
                if selected_option is not None:
                    if st.session_state.selected_test_row_index != selected_option:
                        st.session_state.selected_test_row_index = selected_option
                elif st.session_state.selected_test_row_index is None and len(display_df) > 0:
                    # Default to first row if nothing selected
                    st.session_state.selected_test_row_index = 0
                    st.rerun()
                
                st.caption(f"Showing {len(display_df)} of {len(original_df)} rows. Check the box in the '✓ Select' column to choose which row to test.")
                
                # Get the selected row (remove the Select column for processing)
                if st.session_state.selected_test_row_index is not None and st.session_state.selected_test_row_index < len(display_df_with_index):
                    selected_row = display_df_with_index.iloc[st.session_state.selected_test_row_index]
                    
                    # Show selected row data in an expander
                    with st.expander("📋 Selected Row Data", expanded=True):
                        st.dataframe(selected_row.to_frame().T, use_container_width=True)
                    
                    st.warning("⚠️ Make sure your browser window (with this Streamlit app) is active and PayAByPhone is open in another tab.")
                    st.info("💡 The script will use Ctrl+Tab to switch to PayAByPhone, fill the form, then switch back.")
                    
                    if st.button("🚀 Test Card", type="primary"):
                        with st.spinner("Switching to PayAByPhone tab and filling form..."):
                            try:
                                # Prepare values to fill (collect before switching tabs)
                                # Order matters: Card Number, Expiration Date, CVV, CardHolder Name, Zip
                                values_to_fill = []
                                
                                # 1. Card Number - from "Card Number" column
                                card_number_col = None
                                for col in df.columns:
                                    if col.lower() in ['card number', 'cardnumber', 'card_number']:
                                        card_number_col = col
                                        break
                                
                                if card_number_col and card_number_col in selected_row.index:
                                    card_value = str(selected_row[card_number_col])
                                    if card_value and card_value.lower() not in ['nan', 'none', '']:
                                        values_to_fill.append(card_value)
                                elif number_col and number_col in selected_row.index:
                                    # Fallback to number column if card number column not found
                                    card_value = str(selected_row[number_col])
                                    if card_value and card_value.lower() not in ['nan', 'none', '']:
                                        values_to_fill.append(card_value)
                                
                                # 2. Expiration Date - from "Expire" column
                                expire_col = None
                                for col in df.columns:
                                    if col.lower() in ['expire', 'expiration', 'exp', 'expdate', 'exp_date']:
                                        expire_col = col
                                        break
                                
                                if expire_col and expire_col in selected_row.index:
                                    expire_value = str(selected_row[expire_col])
                                    if expire_value and expire_value.lower() not in ['nan', 'none', '']:
                                        values_to_fill.append(expire_value)
                                
                                # 3. CVV - from "CVV" column
                                cvv_col = None
                                for col in df.columns:
                                    if col.lower() in ['cvv', 'cvc', 'cvv2']:
                                        cvv_col = col
                                        break
                                
                                if cvv_col and cvv_col in selected_row.index:
                                    cvv_value = str(selected_row[cvv_col])
                                    if cvv_value and cvv_value.lower() not in ['nan', 'none', '']:
                                        values_to_fill.append(cvv_value)
                                
                                # 4. CardHolder Name - can be made up (use a placeholder)
                                cardholder_name = "Test User"  # Default placeholder name
                                values_to_fill.append(cardholder_name)
                                
                                # 5. Postal/Zip Code - from "Zip" column
                                zip_col = None
                                for col in df.columns:
                                    if col.lower() in ['zip', 'zipcode', 'zip_code', 'postal', 'postalcode', 'postal_code']:
                                        zip_col = col
                                        break
                                
                                if zip_col and zip_col in selected_row.index:
                                    zip_value = str(selected_row[zip_col])
                                    if zip_value and zip_value.lower() not in ['nan', 'none', '']:
                                        values_to_fill.append(zip_value)
                                
                                # Give user a moment to ensure browser is focused
                                time.sleep(2.0)  # Longer initial pause
                                
                                # Get current mouse position to determine which screen we're on
                                current_mouse_x, current_mouse_y = pyautogui.position()  # type: ignore
                                
                                # Switch to PayAByPhone tab using Ctrl+Tab
                                pyautogui.hotkey('ctrl', 'tab')  # type: ignore
                                time.sleep(2.5)  # Longer pause after switching to PayAByPhone tab
                                
                                # Get screen dimensions for the monitor containing the current mouse position
                                # For multi-monitor setups, we need to constrain clicks to the correct screen
                                try:
                                    import sys
                                    virtual_width, virtual_height = pyautogui.size()  # type: ignore
                                    
                                    if sys.platform == 'win32':
                                        try:
                                            # Try to use Windows API for accurate monitor detection
                                            import win32api  # type: ignore
                                            from win32api import GetSystemMetrics  # type: ignore
                                            
                                            # Get primary monitor dimensions
                                            primary_width = GetSystemMetrics(0)  # SM_CXSCREEN
                                            primary_height = GetSystemMetrics(1)  # SM_CYSCREEN
                                            
                                            # Determine which monitor the mouse is on
                                            # Primary monitor is typically at (0,0) with dimensions primary_width x primary_height
                                            if current_mouse_x >= 0 and current_mouse_x < primary_width and \
                                               current_mouse_y >= 0 and current_mouse_y < primary_height:
                                                # Mouse is on primary monitor
                                                screen_width = primary_width
                                                screen_height = primary_height
                                                primary_x = 0
                                                primary_y = 0
                                            else:
                                                # Mouse is on a secondary monitor
                                                # Use primary monitor dimensions but offset by primary monitor width
                                                # This assumes secondary monitor is to the right of primary
                                                screen_width = primary_width
                                                screen_height = primary_height
                                                primary_x = primary_width
                                                primary_y = 0
                                                # Adjust mouse x to be relative to secondary screen
                                                current_mouse_x = current_mouse_x - primary_x
                                        except ImportError:
                                            # Fallback: use heuristic based on common monitor layouts
                                            # Most common setup: primary at 1920x1080, secondary to the right
                                            # Assume primary is first 1920 pixels (or first half of virtual width, whichever is smaller)
                                            common_primary_width = min(1920, virtual_width // 2)
                                            
                                            if current_mouse_x < common_primary_width:
                                                # Likely on primary screen
                                                screen_width = common_primary_width
                                                screen_height = virtual_height
                                                primary_x = 0
                                                primary_y = 0
                                            else:
                                                # Likely on secondary screen to the right
                                                screen_width = virtual_width - common_primary_width
                                                screen_height = virtual_height
                                                primary_x = common_primary_width
                                                primary_y = 0
                                    else:
                                        # Non-Windows: use virtual screen, but constrain clicks near mouse position
                                        # Assume primary screen is at (0,0) and use primary screen size if available
                                        screen_width, screen_height = pyautogui.size()  # type: ignore
                                        primary_x = 0
                                        primary_y = 0
                                        # Try to detect if we're on a secondary screen by checking if mouse is far from origin
                                        # This is a rough heuristic
                                        if current_mouse_x > 2000:  # Common primary screen width is 1920
                                            # Likely on secondary screen, adjust accordingly
                                            primary_x = 1920
                                            screen_width = virtual_width - 1920
                                except Exception as e:
                                    # Ultimate fallback: constrain to reasonable screen area
                                    screen_width, screen_height = pyautogui.size()  # type: ignore
                                    # Use primary screen (first 1920 pixels or half, whichever is smaller)
                                    screen_width = min(1920, screen_width // 2)
                                    primary_x = 0
                                    primary_y = 0
                                
                                # Take a screenshot of the primary screen area only
                                try:
                                    screenshot = pyautogui.screenshot(region=(primary_x, primary_y, screen_width, screen_height))  # type: ignore
                                except TypeError:
                                    # Older pyautogui doesn't support region parameter
                                    screenshot = pyautogui.screenshot()  # type: ignore
                                    # Crop to primary screen area
                                    screenshot = screenshot.crop((primary_x, primary_y, primary_x + screen_width, primary_y + screen_height))
                                
                                # Helper function to find field label using OCR
                                def find_field_with_ocr(screenshot, search_terms, screen_width, screen_height, primary_x, primary_y):
                                    """Find a field label using OCR and return its click coordinates"""
                                    if not OCR_AVAILABLE or not pytesseract:
                                        return None, None
                                    
                                    try:
                                        # Search in the upper 60% of screen where form labels typically are
                                        search_area = screenshot.crop((0, 0, screen_width, int(screen_height * 0.6)))
                                        
                                        # Get text and bounding boxes
                                        data = pytesseract.image_to_data(search_area, output_type=pytesseract.Output.DICT)  # type: ignore
                                        
                                        # Search for any of the search terms
                                        for i, text in enumerate(data['text']):
                                            text_lower = text.lower().strip()
                                            if text_lower and data['conf'][i] > 30:  # Confidence threshold
                                                # Check if this text matches any search term
                                                for term in search_terms:
                                                    if term.lower() in text_lower:
                                                        # Found matching text, get its position
                                                        x = data['left'][i] + data['width'][i] // 2
                                                        y = data['top'][i] + data['height'][i] // 2
                                                        # Adjust coordinates to be relative to screen origin
                                                        field_x = primary_x + x
                                                        field_y = primary_y + y
                                                        # Ensure coordinates are within screen bounds
                                                        field_x = max(primary_x, min(primary_x + screen_width - 1, field_x))
                                                        field_y = max(primary_y, min(primary_y + screen_height - 1, field_y))
                                                        return field_x, field_y
                                    except Exception:
                                        pass
                                    
                                    return None, None
                                
                                # First, find and fill the Card Number field using OCR
                                card_number_value = values_to_fill[0] if len(values_to_fill) > 0 else None
                                if card_number_value:
                                    # Find the card number field using OCR
                                    card_number_x, card_number_y = find_field_with_ocr(
                                        screenshot, ['card number', 'cardnumber'], screen_width, screen_height, primary_x, primary_y
                                    )
                                    
                                    # If OCR didn't find it, use default position
                                    if card_number_x is None or card_number_y is None:
                                        card_number_x = primary_x + screen_width // 2
                                        card_number_y = primary_y + screen_height // 4
                                    
                                    # Pause before clicking
                                    time.sleep(0.8)  # Longer pause before each field operation
                                    
                                    # Click on the card number field
                                    pyautogui.click(card_number_x, card_number_y)  # type: ignore
                                    time.sleep(1.0)  # Wait for field to focus after click
                                    
                                    # Copy value to clipboard
                                    pyperclip.copy(card_number_value)  # type: ignore
                                    time.sleep(0.3)  # Longer pause after copying
                                    
                                    # Clear any existing text first
                                    pyautogui.hotkey('ctrl', 'a')  # type: ignore
                                    time.sleep(0.4)  # Longer pause after select all
                                    
                                    # Paste the value
                                    pyautogui.hotkey('ctrl', 'v')  # type: ignore
                                    time.sleep(0.8)  # Longer pause after pasting
                                    
                                    # Press Tab twice to move to the expiration date field
                                    time.sleep(0.5)  # Brief pause before tabbing
                                    pyautogui.press('tab')  # type: ignore
                                    time.sleep(0.5)  # Brief pause between tabs
                                    pyautogui.press('tab')  # type: ignore
                                    time.sleep(1.0)  # Wait for expiration field to focus
                                
                                # Fill expiration date
                                expiration_value = values_to_fill[1] if len(values_to_fill) > 1 else None
                                if expiration_value:
                                    # Copy value to clipboard
                                    pyperclip.copy(expiration_value)  # type: ignore
                                    time.sleep(0.3)  # Longer pause after copying
                                    
                                    # Clear any existing text first
                                    pyautogui.hotkey('ctrl', 'a')  # type: ignore
                                    time.sleep(0.4)  # Longer pause after select all
                                    
                                    # Paste the value
                                    pyautogui.hotkey('ctrl', 'v')  # type: ignore
                                    time.sleep(0.8)  # Longer pause after pasting
                                    
                                    # Press Tab once to move to CVV field
                                    time.sleep(0.5)  # Brief pause before tabbing
                                    pyautogui.press('tab')  # type: ignore
                                    time.sleep(1.0)  # Wait for CVV field to focus
                                
                                # Fill CVV
                                cvv_value = values_to_fill[2] if len(values_to_fill) > 2 else None
                                if cvv_value:
                                    # Copy value to clipboard
                                    pyperclip.copy(cvv_value)  # type: ignore
                                    time.sleep(0.3)  # Longer pause after copying
                                    
                                    # Clear any existing text first
                                    pyautogui.hotkey('ctrl', 'a')  # type: ignore
                                    time.sleep(0.4)  # Longer pause after select all
                                    
                                    # Paste the value
                                    pyautogui.hotkey('ctrl', 'v')  # type: ignore
                                    time.sleep(0.8)  # Longer pause after pasting
                                
                                # Now fill remaining fields (Cardholder, Zip) using Tab navigation
                                filled_fields = 1  # Card number
                                if expiration_value:
                                    filled_fields += 1
                                if cvv_value:
                                    filled_fields += 1
                                
                                remaining_values = values_to_fill[3:] if len(values_to_fill) > 3 else []
                                
                                for value in remaining_values:
                                    if value is None:
                                        continue
                                    
                                    # Press Tab to move to next field
                                    time.sleep(0.8)  # Longer pause before each field operation
                                    pyautogui.press('tab')  # type: ignore
                                    time.sleep(1.0)  # Wait for next field to focus
                                    
                                    # Copy value to clipboard
                                    pyperclip.copy(value)  # type: ignore
                                    time.sleep(0.3)  # Longer pause after copying
                                    
                                    # Clear any existing text first
                                    pyautogui.hotkey('ctrl', 'a')  # type: ignore
                                    time.sleep(0.4)  # Longer pause after select all
                                    
                                    # Paste the value
                                    pyautogui.hotkey('ctrl', 'v')  # type: ignore
                                    time.sleep(0.8)  # Longer pause after pasting
                                    
                                    filled_fields += 1
                                
                                # Switch back to Streamlit tab using Ctrl+Tab (or Ctrl+Shift+Tab to go back)
                                # Since we only have 2 tabs, Ctrl+Tab again will switch back
                                time.sleep(1.0)  # Longer pause before switching back
                                pyautogui.hotkey('ctrl', 'tab')  # type: ignore
                                time.sleep(1.0)  # Pause after switching back
                                
                                # Get card number for success message
                                card_display = values_to_fill[0] if len(values_to_fill) > 0 else "N/A"
                                st.success(f"✅ Card number '{card_display}' and {filled_fields} other field(s) have been filled in!")
                                st.info("💡 Form has been filled. Review the PayAByPhone tab to verify and submit.")
                                
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                                st.warning("⚠️ Make sure your browser window is active and PayAByPhone is open in another tab.")
            else:
                st.info("No rows found. Please adjust your search or load data with card information.")
    
    elif page == "📍 Bases":
        st.markdown("### Base Selection & Statistics")
        
        if base_col and st.session_state.base_name_mapping:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Available Bases")
                
                all_bases = list(st.session_state.base_name_mapping.keys())
                selected_bases = st.multiselect(
                    "Select bases to filter:",
                    all_bases,
                    default=all_bases,
                    key="base_selector"
                )
                
                if st.button("Apply Filter", type="primary"):
                    if selected_bases:
                        # Collect all original values that belong to selected base names
                        all_original_values = []
                        for base_name in selected_bases:
                            original_values = st.session_state.base_name_mapping.get(base_name, [])
                            all_original_values.extend(original_values)
                        
                        # Filter data
                        base_series = original_df[base_col].astype(str).str.strip().str.upper()
                        mask = base_series.isin(all_original_values)
                        st.session_state.df = original_df[mask].copy()
                        st.rerun()
                    else:
                        st.warning("Please select at least one base")
                
                if st.button("Reset Filter"):
                    if st.session_state.original_df is not None:
                        st.session_state.df = st.session_state.original_df.copy()
                        st.rerun()
            
            with col2:
                st.markdown("#### Base Statistics")
                
                display_bases = selected_bases if selected_bases else all_bases
                
                for base_name in sorted(display_bases):
                    with st.expander(f"📊 {base_name}", expanded=True):
                        stats = calculate_base_statistics(
                            original_df, base_name, st.session_state.base_name_mapping, 
                            base_col, checker_col
                        )
                        
                        total = stats.get('total', 0)
                        approved = stats.get('approved', 0)
                        not_approved = stats.get('not_approved', 0)
                        not_in_time = stats.get('not_in_time', 0)
                        
                        approved_pct = (approved / total * 100) if total > 0 else 0
                        not_approved_pct = (not_approved / total * 100) if total > 0 else 0
                        not_in_time_pct = (not_in_time / total * 100) if total > 0 else 0
                        
                        st.metric("Total", total)
                        st.metric("✓ Approved", f"{approved} ({approved_pct:.1f}%)")
                        st.metric("✗ Not Approved", f"{not_approved} ({not_approved_pct:.1f}%)")
                        st.metric("⏱ Not in Time", f"{not_in_time} ({not_in_time_pct:.1f}%)")
                        
                        # Show grouped original values
                        original_values = st.session_state.base_name_mapping.get(base_name, [])
                        if len(original_values) > 1:
                            st.caption(f"Groups: {', '.join(original_values)}")
        else:
            st.info("Base column not found in the data. Please ensure your file has a 'Base' column.")

