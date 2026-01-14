import streamlit as st
import pandas as pd
import io
import datetime

# Page config
st.set_page_config(
    page_title="FDA Adverse Event Case Viewer",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #f8f9fa 0%, #e9ecef 100%);
    }
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
    }
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 20px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sub-section-header {
        background: #e9ecef;
        color: #495057;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 15px 0 10px 0;
        font-size: 16px;
        font-weight: 600;
        border-left: 5px solid #667eea;
    }
    .drug-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .drug-card-ps {
        border-color: #dc3545;
        background: linear-gradient(to right, #fff5f5 0%, #ffffff 100%);
    }
    .drug-card-ss {
        border-color: #ffc107;
        background: linear-gradient(to right, #fffbf0 0%, #ffffff 100%);
    }
    .drug-card-c {
        border-color: #6c757d;
        background: linear-gradient(to right, #f8f9fa 0%, #ffffff 100%);
    }
    .role-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-ps {
        background: #dc3545;
        color: white;
    }
    .badge-ss {
        background: #ffc107;
        color: #000;
    }
    .badge-c {
        background: #6c757d;
        color: white;
    }
    .reaction-tag {
        display: inline-block;
        background: #dc3545;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    .field-label {
        font-size: 11px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .field-value {
        font-size: 14px;
        color: #212529;
        margin-bottom: 15px;
        font-weight: 500;
    }
    .assessment-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #d1d1d1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

def format_date_std(date_str):
    """Format date string to YYYY-MM-DD"""
    if pd.isna(date_str) or date_str == '' or str(date_str).strip().upper() == 'NA':
        return 'NA'
    
    # Clean up string
    date_str = str(date_str).strip()
    
    try:
        # Try parsing with pandas, which handles many formats (ISO, YYYYMMDD, etc.)
        dt = pd.to_datetime(date_str, errors='raise')
        return dt.strftime('%Y-%m-%d')
    except:
        # Return original if parsing fails
        return date_str

def parse_separated_values(value):
    """Parse semicolon-separated values"""
    if pd.isna(value) or value == '' or value == 'NA':
        return []
    return [v.strip() for v in str(value).split(';')]

def get_role_label(code):
    """Get full label for role code"""
    labels = {
        'PS': 'Primary Suspect',
        'SS': 'Secondary Suspect',
        'C': 'Concomitant',
        'I': 'Interacting'
    }
    return labels.get(code, code)

def get_role_class(code):
    """Get CSS class for role code"""
    if code == 'PS':
        return 'ps'
    elif code == 'SS':
        return 'ss'
    else:
        return 'c'

def process_drug_data(row):
    """Process and structure drug data from a row"""
    sequences = parse_separated_values(row.get('drug_seq', ''))
    role_codes = parse_separated_values(row.get('role_cod', ''))
    drug_names = parse_separated_values(row.get('drugname', ''))
    product_ai = parse_separated_values(row.get('prod_ai', ''))
    routes = parse_separated_values(row.get('route', ''))
    dose_amts = parse_separated_values(row.get('dose_amt', ''))
    dose_units = parse_separated_values(row.get('dose_unit', ''))
    dose_forms = parse_separated_values(row.get('dose_form', ''))
    dose_freqs = parse_separated_values(row.get('dose_freq', ''))
    indications = parse_separated_values(row.get('indi_pt', ''))
    start_dates = parse_separated_values(row.get('start_dt', ''))
    end_dates = parse_separated_values(row.get('end_dt', ''))
    dechals = parse_separated_values(row.get('dechal', ''))
    rechals = parse_separated_values(row.get('rechal', ''))
    lot_nums = parse_separated_values(row.get('lot_num', ''))
    
    # Additional fields
    val_vbms = parse_separated_values(row.get('val_vbm', ''))
    dose_vbms = parse_separated_values(row.get('dose_vbm', ''))
    cum_dose_chrs = parse_separated_values(row.get('cum_dose_chr', ''))
    cum_dose_units = parse_separated_values(row.get('cum_dose_unit', ''))
    exp_dts = parse_separated_values(row.get('exp_dt', ''))
    nda_nums = parse_separated_values(row.get('nda_num', ''))
    durs = parse_separated_values(row.get('dur', ''))
    dur_cods = parse_separated_values(row.get('dur_cod', ''))
    
    drugs = []
    for i in range(len(sequences)):
        drugs.append({
            'sequence': sequences[i] if i < len(sequences) else 'NA',
            'role_code': role_codes[i] if i < len(role_codes) else 'NA',
            'drug_name': drug_names[i] if i < len(drug_names) else 'NA',
            'product_ai': product_ai[i] if i < len(product_ai) else 'NA',
            'route': routes[i] if i < len(routes) else 'NA',
            'dose_amount': dose_amts[i] if i < len(dose_amts) else 'NA',
            'dose_unit': dose_units[i] if i < len(dose_units) else 'NA',
            'dose_form': dose_forms[i] if i < len(dose_forms) else 'NA',
            'dose_frequency': dose_freqs[i] if i < len(dose_freqs) else 'NA',
            'indication': indications[i] if i < len(indications) else 'NA',
            # Format dates here
            'start_date': format_date_std(start_dates[i]) if i < len(start_dates) else 'NA',
            'end_date': format_date_std(end_dates[i]) if i < len(end_dates) else 'NA',
            'dechallenge': dechals[i] if i < len(dechals) else 'NA',
            'rechallenge': rechals[i] if i < len(rechals) else 'NA',
            'lot_number': lot_nums[i] if i < len(lot_nums) else 'NA',
            'val_vbm': val_vbms[i] if i < len(val_vbms) else 'NA',
            'dose_vbm': dose_vbms[i] if i < len(dose_vbms) else 'NA',
            'cum_dose_chr': cum_dose_chrs[i] if i < len(cum_dose_chrs) else 'NA',
            'cum_dose_unit': cum_dose_units[i] if i < len(cum_dose_units) else 'NA',
            'exp_dt': format_date_std(exp_dts[i]) if i < len(exp_dts) else 'NA',
            'nda_num': nda_nums[i] if i < len(nda_nums) else 'NA',
            'duration': durs[i] if i < len(durs) else 'NA',
            'duration_code': dur_cods[i] if i < len(dur_cods) else 'NA'
        })
    
    return drugs

def display_field(label, value, col=None):
    """Display a labeled field"""
    container = col if col else st
    # If the label implies a date, format it
    if 'Date' in label or label.endswith('dt') or label.endswith('Dt'):
         value = format_date_std(value)
         
    container.markdown(f'<div class="field-label">{label}</div>', unsafe_allow_html=True)
    container.markdown(f'<div class="field-value">{value if value else "NA"}</div>', unsafe_allow_html=True)

# Main app
def main():
    st.title("💊 FDA Adverse Event Case Viewer")
    st.markdown("### Professional Assessment Interface")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Source")
        
        uploaded_file = st.file_uploader(
            "Upload CSV/TSV file",
            type=['csv', 'tsv', 'txt'],
            help="Upload your adverse event data file"
        )
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Use"):
            st.markdown("""
            **Steps:**
            1. **Upload your CSV/TSV file** above
            2. **Enter Primary ID or Case ID** to search
            3. **Fill the Assessment** at the bottom
            4. **Download** the result
            
            **Search:**
            - Enter Primary ID or Case ID
            - Use Advanced Filters (Assessor, Country)
            - Click Search button
            
            **Color Codes:**
            - 🔴 Red = Primary Suspect
            - 🟠 Orange = Secondary Suspect
            - ⚫ Gray = Concomitant
            """)
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **FDA Adverse Event Case Viewer**
            
            Version 2.3 - Assessment Enabled
            
            Features:
            - Search 55,000+ cases instantly
            - Independent Status/Assessor section
            - Integrated Assessment Template
            - Downloadable Evaluation
            
            Created for clinical assessors.
            """)
    
    # Load data from file upload
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.tsv') or uploaded_file.name.endswith('.txt'):
                df = pd.read_csv(uploaded_file, sep='\t')
            else:
                df = pd.read_csv(uploaded_file)
            st.session_state['df'] = df
            
            # Show dataset statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Cases", f"{len(df):,}")
            with col2:
                unique_primary = df['primaryid'].nunique() if 'primaryid' in df.columns else 0
                st.metric("Unique Primary IDs", f"{unique_primary:,}")
            with col3:
                unique_case = df['caseid'].nunique() if 'caseid' in df.columns else 0
                st.metric("Unique Case IDs", f"{unique_case:,}")
            with col4:
                assessors = df['assessor'].nunique() if 'assessor' in df.columns else 0
                st.metric("Assessors", f"{assessors:,}")
            
            st.success(f"✅ Data loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return
    
    # Check if data is loaded
    if 'df' not in st.session_state or st.session_state['df'] is None:
        st.info("👆 Please upload a file from the sidebar to begin")
        return
    
    df = st.session_state['df']
    
    # Search interface
    st.markdown("---")
    
    # Advanced search toggle
    with st.expander("🔍 Advanced Search Options", expanded=False):
        adv_col1, adv_col2 = st.columns(2)
        with adv_col1:
            search_assessor = st.selectbox(
                "Filter by Assessor",
                options=['All'] + sorted(df['assessor'].dropna().unique().tolist()) if 'assessor' in df.columns else ['All'],
                help="Filter cases by assessor"
            )
        with adv_col2:
            search_country = st.selectbox(
                "Filter by Country",
                options=['All'] + sorted(df['occr_country'].dropna().unique().tolist()) if 'occr_country' in df.columns else ['All'],
                help="Filter cases by occurrence country"
            )
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_primary = st.text_input(
            "🔍 Search by Primary ID",
            placeholder="Enter Primary ID (e.g., 102854963)",
            help="Enter the Primary ID to find a specific case"
        )
    
    with col2:
        search_case = st.text_input(
            "🔍 Search by Case ID",
            placeholder="Enter Case ID (e.g., 10285496)",
            help="Enter the Case ID to find a specific case"
        )
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_button = st.button("🔎 Search", use_container_width=True)
    
    # Search logic
    row = None
    filtered_df = df.copy()
    
    # Apply advanced filters
    if 'search_assessor' in locals() and search_assessor != 'All':
        filtered_df = filtered_df[filtered_df['assessor'] == search_assessor]
    if 'search_country' in locals() and search_country != 'All':
        filtered_df = filtered_df[filtered_df['occr_country'] == search_country]
    
    if search_button or search_primary or search_case:
        if search_primary:
            # Search by primary ID
            mask = filtered_df['primaryid'].astype(str) == str(search_primary)
            matches = filtered_df[mask]
            
            if len(matches) > 0:
                row = matches.iloc[0]
                st.success(f"✅ Found case with Primary ID: {search_primary}")
            else:
                st.error(f"❌ No case found with Primary ID: {search_primary}")
                return
        
        elif search_case:
            # Search by case ID
            mask = filtered_df['caseid'].astype(str) == str(search_case)
            matches = filtered_df[mask]
            
            if len(matches) > 0:
                row = matches.iloc[0]
                st.success(f"✅ Found case with Case ID: {search_case}")
            else:
                st.error(f"❌ No case found with Case ID: {search_case}")
                return
        else:
            st.warning("⚠️ Please enter a Primary ID or Case ID to search")
            return
    else:
        # Show prompt to search
        st.info("👆 Enter a Primary ID or Case ID above and click Search")
        return
    
    st.markdown("---")
    
    # === NEW SECTION: Status & Assessor ===
    st.markdown('<div class="section-header">📌 Status & Assignment</div>', unsafe_allow_html=True)
    status_cols = st.columns(3)
    with status_cols[0]:
        display_field("Status", row.get('status', 'NA'))
    with status_cols[1]:
        display_field("Assessor", row.get('assessor', 'NA'))
    with status_cols[2]:
        display_field("Assignment Date", row.get('date_assignement', 'NA'))

    # Administrative Section (Updated: Removed Status/Assessor)
    st.markdown('<div class="section-header">📋 Administrative Information</div>', unsafe_allow_html=True)
    
    # Row 1: Primary identifiers
    admin_cols1 = st.columns(4)
    with admin_cols1[0]:
        display_field("Case ID", row.get('caseid', 'NA'))
    with admin_cols1[1]:
        display_field("Primary ID", row.get('primaryid', 'NA'))
    with admin_cols1[2]:
        display_field("Case Version", row.get('caseversion', 'NA'))
    with admin_cols1[3]:
        display_field("I/F Code", row.get('i_f_code', 'NA'))
    
    # Row 2: Dates (Event Date is also here for reference, but repeated in drugs)
    admin_cols2 = st.columns(4)
    with admin_cols2[0]:
        display_field("Event Date", row.get('event_dt', 'NA'))
    with admin_cols2[1]:
        display_field("Manufacture Date", row.get('mfr_dt', 'NA'))
    with admin_cols2[2]:
        display_field("Initial FDA Date", row.get('init_fda_dt', 'NA'))
    with admin_cols2[3]:
        display_field("FDA Date", row.get('fda_dt', 'NA'))
    
    # Row 3: Report info
    admin_cols3 = st.columns(4)
    with admin_cols3[0]:
        display_field("Report Date", row.get('rept_dt', 'NA'))
    with admin_cols3[1]:
        display_field("Report Code", row.get('rept_cod', 'NA'))
    with admin_cols3[2]:
        display_field("To Manufacturer", row.get('to_mfr', 'NA'))
    with admin_cols3[3]:
        display_field("Reporter Country", row.get('reporter_country', 'NA'))
    
    # Row 4: Manufacturer info
    admin_cols4 = st.columns(5)
    with admin_cols4[0]:
        display_field("Manufacturer Number", row.get('mfr_num', 'NA'))
    with admin_cols4[1]:
        display_field("Manufacturer Sender", row.get('mfr_sndr', 'NA'))
    with admin_cols4[2]:
        display_field("Authorization Number", row.get('auth_num', 'NA'))
    with admin_cols4[3]:
        display_field("Literature Reference", row.get('lit_ref', 'NA'))
    with admin_cols4[4]:
        display_field("Occurrence Country", row.get('occr_country', 'NA'))
    
    # Demographics Section
    st.markdown('<div class="section-header">👤 Patient Demographics</div>', unsafe_allow_html=True)
    demo_cols = st.columns(6)
    with demo_cols[0]:
        age_str = f"{row.get('age', 'NA')} {row.get('age_cod', '')}"
        display_field("Age", age_str.strip())
    with demo_cols[1]:
        display_field("Age Group", row.get('age_grp', 'NA'))
    with demo_cols[2]:
        display_field("Sex", row.get('sex', 'NA'))
    with demo_cols[3]:
        wt_str = f"{row.get('wt', 'NA')} {row.get('wt_cod', '')}"
        display_field("Weight", wt_str.strip())
    with demo_cols[4]:
        display_field("E-Sub", row.get('e_sub', 'NA'))
    with demo_cols[5]:
        display_field("Occupation Code", row.get('occp_cod', 'NA'))
    
    # Adverse Reactions Section
    st.markdown('<div class="section-header">⚠️ Adverse Reactions</div>', unsafe_allow_html=True)
    reactions = parse_separated_values(row.get('pt', ''))
    if reactions:
        reactions_html = ''.join([f'<span class="reaction-tag">{r}</span>' for r in reactions])
        st.markdown(reactions_html, unsafe_allow_html=True)
    else:
        st.info("No adverse reactions recorded")
    
    # Drugs Section
    drugs = process_drug_data(row)
    case_event_date = format_date_std(row.get('event_dt', 'NA'))
    
    st.markdown(f'<div class="section-header">💊 Drug Information ({len(drugs)} drugs)</div>', unsafe_allow_html=True)
    
    for drug in drugs:
        role_class = get_role_class(drug['role_code'])
        role_label = get_role_label(drug['role_code'])
        
        # Drug card
        st.markdown(f'<div class="drug-card drug-card-{role_class}">', unsafe_allow_html=True)
        
        # Header
        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.markdown(f"### Drug #{drug['sequence']}: {drug['drug_name']}")
        with header_cols[1]:
            st.markdown(f'<div class="role-badge badge-{role_class}">{role_label}</div>', unsafe_allow_html=True)
        
        # Drug details - Row 1: Basic Info
        st.markdown("**Basic Information**")
        drug_cols1 = st.columns(4)
        
        with drug_cols1[0]:
            display_field("Product/Active Ingredient", drug['product_ai'])
        with drug_cols1[1]:
            display_field("Indication", drug['indication'])
        with drug_cols1[2]:
            display_field("Route", drug['route'])
        with drug_cols1[3]:
            # === NEW: Event Date repeated here ===
            display_field("Event Date", case_event_date)
        
        # Row 2: Dosing
        st.markdown("**Dosing Information**")
        drug_cols2 = st.columns(5)
        
        with drug_cols2[0]:
            dose_str = f"{drug['dose_amount']} {drug['dose_unit']}"
            display_field("Dose", dose_str.strip())
        with drug_cols2[1]:
            display_field("Dose Form", drug['dose_form'])
        with drug_cols2[2]:
            display_field("Dose Frequency", drug['dose_frequency'])
        with drug_cols2[3]:
            display_field("Dose VBM", drug['dose_vbm'])
        with drug_cols2[4]:
            cum_dose_str = f"{drug['cum_dose_chr']} {drug['cum_dose_unit']}"
            display_field("Cumulative Dose", cum_dose_str.strip())
        
        # Row 3: Dates and Duration
        st.markdown("**Timeline**")
        drug_cols3 = st.columns(5)
        
        with drug_cols3[0]:
            display_field("Start Date", drug['start_date'])
        with drug_cols3[1]:
            display_field("End Date", drug['end_date'])
        with drug_cols3[2]:
            dur_str = f"{drug['duration']} {drug['duration_code']}"
            display_field("Duration", dur_str.strip())
        with drug_cols3[3]:
            display_field("Expiration Date", drug['exp_dt'])
        with drug_cols3[4]:
            display_field("Lot Number", drug['lot_number'])
        
        # Row 4: Challenge and Other Info
        st.markdown("**Challenge & Regulatory**")
        drug_cols4 = st.columns(4)
        
        with drug_cols4[0]:
            display_field("Dechallenge", drug['dechallenge'])
        with drug_cols4[1]:
            display_field("Rechallenge", drug['rechallenge'])
        with drug_cols4[2]:
            display_field("NDA Number", drug['nda_num'])
        with drug_cols4[3]:
            display_field("Val VBM", drug['val_vbm'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Narrative Section
    if 'narrative' in row and pd.notna(row.get('narrative')) and str(row.get('narrative')).strip() not in ['', 'NA']:
        st.markdown('<div class="section-header">📝 Case Narrative</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; white-space: pre-wrap; font-family: monospace; font-size: 13px;">
        {row.get('narrative', 'NA')}
        </div>
        """, unsafe_allow_html=True)
        
    # === NEW SECTION: Assessment Form ===
    st.markdown("---")
    st.markdown('<div class="section-header">⚖️ Case Assessment</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="assessment-box">', unsafe_allow_html=True)
        st.markdown("### Evaluate Case")
        st.caption("Complete the assessment based on the ICSR template. Download the result below.")
        
        with st.form("assessment_form"):
            # Header info (Pre-filled)
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                asm_case = st.text_input("Case Number", value=str(row.get('caseid', '')), disabled=True)
            with col_a2:
                # Pre-fill PTs
                default_pt = str(row.get('pt', '')).replace(';', ', ')
                asm_pt = st.text_area("Preferred Terms (PT)", value=default_pt, height=68)

            # Pre-fill Drug Names
            default_drugs = ", ".join([d['drug_name'] for d in drugs])
            asm_drug = st.text_area("Drug Name(s)", value=default_drugs)
            
            st.markdown("#### Clinical Questions")
            
            # Generate 10 Questions based on template structure
            # Using tabs for better organization
            tab1, tab2 = st.tabs(["Questions 1-5", "Questions 6-10"])
            
            scores = {}
            reasonings = {}
            
            with tab1:
                for i in range(1, 6):
                    st.markdown(f"**Question {i}**")
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        scores[f'q{i}_score'] = st.number_input(f"Q{i} Score", min_value=-10, max_value=10, value=0, key=f"q{i}s")
                    with c2:
                        reasonings[f'q{i}_reasoning'] = st.text_input(f"Q{i} Reasoning", key=f"q{i}r")
                    st.divider()

            with tab2:
                for i in range(6, 11):
                    st.markdown(f"**Question {i}**")
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        scores[f'q{i}_score'] = st.number_input(f"Q{i} Score", min_value=-10, max_value=10, value=0, key=f"q{i}s")
                    with c2:
                        reasonings[f'q{i}_reasoning'] = st.text_input(f"Q{i} Reasoning", key=f"q{i}r")
                    st.divider()
            
            st.markdown("#### Final Evaluation")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                asm_final_score = st.number_input("Final Score", value=0)
            with col_f2:
                asm_outcome = st.selectbox("Outcome", ["", "Related", "Not Related", "Indeterminate", "Unlikely"])
            
            asm_desc = st.text_area("Description / Conclusion")
            
            # Hidden narrative field for the file
            asm_narrative = row.get('narrative', '')
            
            submitted = st.form_submit_button("✅ Generate Assessment", use_container_width=True)
            
            if submitted:
                # Create dictionary for DataFrame matching template columns
                data = {
                    'case': [asm_case], # assuming case matches case_id in this context
                    'case_id': [asm_case],
                    'pt': [asm_pt],
                    'drug_name': [asm_drug]
                }
                
                # Add scores and reasonings
                for i in range(1, 11):
                    data[f'q{i}_score'] = [scores[f'q{i}_score']]
                    data[f'q{i}_reasoning'] = [reasonings[f'q{i}_reasoning']]
                
                # Add finals
                data['final_score'] = [asm_final_score]
                data['outcome'] = [asm_outcome]
                data['description'] = [asm_desc]
                data['case_narrative'] = [asm_narrative]
                
                # Convert to DataFrame
                result_df = pd.DataFrame(data)
                
                # Convert to CSV for download
                csv = result_df.to_csv(index=False).encode('utf-8')
                
                st.success("Assessment generated! Download below.")
                st.download_button(
                    label="📥 Download Assessment (CSV)",
                    data=csv,
                    file_name=f"assessment_{asm_case}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
