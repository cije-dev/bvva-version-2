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
        
        if not SELENIUM_AVAILABLE:
            st.error("Selenium is not installed. Please install it: pip install selenium webdriver-manager")
        else:
            st.info("This feature will open PayAByPhone in a browser window and fill in card details from your data.")
            
            # Find number/card column
            number_col = None
            card_col = None
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['number', 'card number', 'cardnumber', 'card', 'num']:
                    number_col = col
                    card_col = col
                    break
            
            if number_col is None:
                st.warning("Could not find a 'Number' or 'Card Number' column in the data.")
                st.info("Available columns: " + ", ".join(df.columns.tolist()[:10]))
            else:
                # Display available numbers
                st.markdown(f"#### Select a number from column: **{number_col}**")
                
                # Get unique numbers (remove NaN and empty values)
                available_numbers = df[number_col].dropna().astype(str).str.strip()
                available_numbers = available_numbers[available_numbers != ''].unique()
                available_numbers = sorted(available_numbers)
                
                if len(available_numbers) == 0:
                    st.warning(f"No valid numbers found in column '{number_col}'")
                else:
                    selected_number = st.selectbox(
                        "Select a number:",
                        available_numbers,
                        key="test_card_number"
                    )
                    
                    # Get the row for this number
                    selected_row = df[df[number_col].astype(str).str.strip() == selected_number].iloc[0]  # type: ignore
                    
                    # Show the row data
                    with st.expander("📋 Selected Row Data", expanded=False):
                        st.dataframe(selected_row.to_frame().T, use_container_width=True)
                    
                    if st.button("🚀 Test Card", type="primary"):
                        with st.spinner("Opening browser and filling form..."):
                            try:
                                driver = None
                                try:
                                    # Setup Chrome options
                                    chrome_options = Options()
                                    chrome_options.add_argument("--start-maximized")
                                    # chrome_options.add_argument("--headless")  # Uncomment to run in background
                                    
                                    # Initialize driver
                                    service = Service(ChromeDriverManager().install())
                                    driver = webdriver.Chrome(service=service, options=chrome_options)
                                    
                                    # Try to find PayAByPhone tab by checking window titles
                                    # First, open a new tab or navigate to common PayAByPhone URLs
                                    # Common PayAByPhone URLs - you may need to adjust
                                    # Try to find existing PayAByPhone window
                                    found_tab = False
                                    for window_handle in driver.window_handles:
                                        driver.switch_to.window(window_handle)
                                        if "payabyp" in driver.title.lower() or "pay a byp" in driver.title.lower():
                                            found_tab = True
                                            break
                                    
                                    if not found_tab:
                                        # Open PayAByPhone - you'll need to provide the actual URL
                                        st.warning("PayAByPhone tab not found. Please provide the URL or ensure the tab is open.")
                                        url = st.text_input("Enter PayAByPhone URL:", key="payabyp_url", value="")
                                        if url:
                                            driver.get(url)
                                            time.sleep(2)
                                        else:
                                            st.error("Please provide the PayAByPhone URL")
                                            driver.quit()
                                            st.stop()
                                    
                                    # Wait for page to load
                                    time.sleep(2)
                                    
                                    # Find and fill card number field (common selectors - adjust as needed)
                                    card_number_field = None
                                    selectors = [
                                        ("id", "cardNumber"),
                                        ("name", "cardNumber"),
                                        ("id", "card-number"),
                                        ("name", "card-number"),
                                        ("id", "card"),
                                        ("name", "card"),
                                        ("xpath", "//input[@type='text' and contains(@placeholder, 'card') or contains(@placeholder, 'number')]"),
                                        ("xpath", "//input[contains(@class, 'card') or contains(@class, 'number')]")
                                    ]
                                    
                                    for selector_type, selector_value in selectors:
                                        try:
                                            if selector_type == "id":
                                                card_number_field = driver.find_element(By.ID, selector_value)
                                            elif selector_type == "name":
                                                card_number_field = driver.find_element(By.NAME, selector_value)
                                            elif selector_type == "xpath":
                                                card_number_field = driver.find_element(By.XPATH, selector_value)
                                            
                                            if card_number_field:
                                                break
                                        except:
                                            continue
                                    
                                    if card_number_field:
                                        # Clear and fill card number
                                        card_number_field.clear()
                                        card_number_field.send_keys(str(selected_number))
                                        
                                        # Try to fill other fields based on common patterns
                                        # You may need to adjust these selectors based on the actual form
                                        try:
                                            # Common field names - adjust based on actual form
                                            field_mappings = {
                                                'name': ['name', 'cardholder', 'holder', 'cardholderName'],
                                                'expiry': ['expiry', 'exp', 'expDate', 'expiration'],
                                                'cvv': ['cvv', 'cvc', 'security', 'securityCode'],
                                                'zip': ['zip', 'postal', 'postalCode', 'zipCode']
                                            }
                                            
                                            # Try to fill other fields from the row
                                            for field_name, possible_names in field_mappings.items():
                                                for col in df.columns:
                                                    if any(name in col.lower() for name in possible_names):
                                                        if col in selected_row.index:
                                                            value = str(selected_row[col])
                                                            if value and value != 'nan':
                                                                for name in possible_names:
                                                                    try:
                                                                        field = driver.find_element(By.NAME, name)
                                                                        field.clear()
                                                                        field.send_keys(value)
                                                                        break
                                                                    except:
                                                                        try:
                                                                            field = driver.find_element(By.ID, name)
                                                                            field.clear()
                                                                            field.send_keys(value)
                                                                            break
                                                                        except:
                                                                            continue
                                        except Exception as e:
                                            st.warning(f"Could not auto-fill all fields: {str(e)}")
                                        
                                        st.success(f"✅ Card number '{selected_number}' has been filled in!")
                                        st.info("💡 Browser window is still open. You can review and submit the form manually.")
                                    else:
                                        st.error("Could not find card number field. Please check the form structure.")
                                
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                                
                                finally:
                                    # Keep browser open - user can close it manually
                                    # driver.quit()  # Uncomment to auto-close
                                    pass
                                    
                            except Exception as e:
                                st.error(f"Failed to open browser: {str(e)}")
                                st.info("Make sure Chrome is installed and ChromeDriver is available.")
    
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

