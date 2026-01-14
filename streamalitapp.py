import streamlit as st
import pandas as pd
from io import StringIO

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
</style>
""", unsafe_allow_html=True)

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
            'start_date': start_dates[i] if i < len(start_dates) else 'NA',
            'end_date': end_dates[i] if i < len(end_dates) else 'NA',
            'dechallenge': dechals[i] if i < len(dechals) else 'NA',
            'rechallenge': rechals[i] if i < len(rechals) else 'NA',
            'lot_number': lot_nums[i] if i < len(lot_nums) else 'NA'
        })
    
    return drugs

def display_field(label, value, col=None):
    """Display a labeled field"""
    container = col if col else st
    container.markdown(f'<div class="field-label">{label}</div>', unsafe_allow_html=True)
    container.markdown(f'<div class="field-value">{value if value else "NA"}</div>', unsafe_allow_html=True)

def load_sample_data():
    """Load sample data"""
    sample_csv = """date_assignement,assessor,status,primaryid,caseid,drug_seq,role_cod,drugname,prod_ai,val_vbm,route,dose_vbm,cum_dose_chr,cum_dose_unit,dechal,rechal,lot_num,exp_dt,nda_num,dose_amt,dose_unit,dose_form,dose_freq,start_dt,end_dt,dur,dur_cod,caseversion,i_f_code,event_dt,mfr_dt,init_fda_dt,fda_dt,rept_cod,auth_num,mfr_num,mfr_sndr,lit_ref,age,age_cod,age_grp,sex,e_sub,wt,wt_cod,rept_dt,to_mfr,occp_cod,reporter_country,occr_country,pt,indi_pt
06-01-2026,Lorrie,,102854963,10285496,1 ; 4 ; 2 ; 5 ; 7 ; 3 ; 6,PS ; SS ; SS ; SS ; C ; SS ; C,ERIVEDGE ; ERIVEDGE ; ERIVEDGE ; ERIVEDGE ; DILTIAZEM ; ERIVEDGE ; LISINOPRIL,ERIVEDGE ; ERIVEDGE ; ERIVEDGE ; ERIVEDGE ; DILTIAZEM ; ERIVEDGE ; LISINOPRIL,1 ; 1 ; 1 ; 1 ; 1 ; 1 ; 1,Other ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,Y ; Y ; Y ; Y ; NA ; Y ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,50242-0140-01 ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,15000 ; NA ; NA ; NA ; NA ; NA ; NA,MG ; NA ; NA ; NA ; NA ; NA ; NA,Capsule ; NA ; NA ; NA ; NA ; NA ; NA,QD ; NA ; NA ; NA ; NA ; NA ; NA,2008 ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,NA ; NA ; NA ; NA ; NA ; NA ; NA,3,F,20080101,20250116,20140709,20250128,EXP,,US-ROCHE-1428166,ROCHE,,58,YR,A,M,Y,,,20250128,,CN,US,US,Mood swings ; Upper limb fracture ; Alopecia ; Basal cell carcinoma ; Arthropathy ; Vitamin D deficiency ; Impaired healing ; Fall ; Gastrointestinal disorder ; Weight decreased,Basal cell carcinoma ; Basal cell carcinoma ; Basal cell naevus syndrome ; Basal cell carcinoma ; Basal cell carcinoma ; Basal cell carcinoma ; Hypertension ; Hypertension"""
    
    return pd.read_csv(StringIO(sample_csv))

# Main app
def main():
    st.title("💊 FDA Adverse Event Case Viewer")
    st.markdown("### Professional Assessment Interface")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Source")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV/TSV file",
            type=['csv', 'tsv', 'txt'],
            help="Export from Google Sheets as CSV or TSV"
        )
        
        st.markdown("---")
        
        # Load sample data button
        if st.button("📋 Load Sample Case", use_container_width=True):
            st.session_state['df'] = load_sample_data()
            st.session_state['selected_row'] = 0
            st.success("Sample data loaded!")
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Use"):
            st.markdown("""
            1. **Upload your data** (CSV/TSV)
            2. **Select a case** from the dropdown
            3. **View organized information** in three sections:
               - Administrative
               - Demographics
               - Drugs (color-coded by role)
            
            **Color Codes:**
            - 🔴 Red = Primary Suspect
            - 🟠 Orange = Secondary Suspect
            - ⚫ Gray = Concomitant
            """)
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **FDA Adverse Event Case Viewer**
            
            Version 1.0
            
            Created for clinical assessors to efficiently review adverse event reports with grouped drug information.
            """)
    
    # Load data
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.tsv') or uploaded_file.name.endswith('.txt'):
                df = pd.read_csv(uploaded_file, sep='\t')
            else:
                df = pd.read_csv(uploaded_file)
            st.session_state['df'] = df
            st.success(f"✅ Loaded {len(df)} cases")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return
    
    # Check if data is loaded
    if 'df' not in st.session_state or st.session_state['df'] is None:
        st.info("👆 Please upload a file or load sample data from the sidebar")
        return
    
    df = st.session_state['df']
    
    # Case selector
    case_options = [f"Case {row['caseid']} - {row.get('assessor', 'Unassigned')}" 
                   for idx, row in df.iterrows()]
    
    selected_case = st.selectbox(
        "Select a case to view:",
        range(len(case_options)),
        format_func=lambda x: case_options[x],
        key='case_selector'
    )
    
    # Get selected row
    row = df.iloc[selected_case]
    
    st.markdown("---")
    
    # Administrative Section
    st.markdown('<div class="section-header">📋 Administrative Information</div>', unsafe_allow_html=True)
    admin_cols = st.columns(4)
    with admin_cols[0]:
        display_field("Case ID", row.get('caseid', 'NA'))
        display_field("Event Date", row.get('event_dt', 'NA'))
    with admin_cols[1]:
        display_field("Primary ID", row.get('primaryid', 'NA'))
        display_field("FDA Date", row.get('fda_dt', 'NA'))
    with admin_cols[2]:
        display_field("Assessor", row.get('assessor', 'NA'))
        display_field("Report Date", row.get('rept_dt', 'NA'))
    with admin_cols[3]:
        display_field("Assignment Date", row.get('date_assignement', 'NA'))
        display_field("Reporter Country", row.get('reporter_country', 'NA'))
    
    # Demographics Section
    st.markdown('<div class="section-header">👤 Patient Demographics</div>', unsafe_allow_html=True)
    demo_cols = st.columns(4)
    with demo_cols[0]:
        age_str = f"{row.get('age', 'NA')} {row.get('age_cod', '')}"
        display_field("Age", age_str.strip())
    with demo_cols[1]:
        display_field("Sex", row.get('sex', 'NA'))
    with demo_cols[2]:
        wt_str = f"{row.get('wt', 'NA')} {row.get('wt_cod', '')}"
        display_field("Weight", wt_str.strip())
    with demo_cols[3]:
        display_field("Country", row.get('occr_country', 'NA'))
    
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
        
        # Drug details
        drug_cols = st.columns(3)
        
        with drug_cols[0]:
            display_field("Product/Active Ingredient", drug['product_ai'])
            display_field("Indication", drug['indication'])
            display_field("Route", drug['route'])
            display_field("Start Date", drug['start_date'])
        
        with drug_cols[1]:
            dose_str = f"{drug['dose_amount']} {drug['dose_unit']}"
            display_field("Dose", dose_str.strip())
            display_field("Dose Form", drug['dose_form'])
            display_field("Frequency", drug['dose_frequency'])
            display_field("End Date", drug['end_date'])
        
        with drug_cols[2]:
            display_field("Dechallenge", drug['dechallenge'])
            display_field("Rechallenge", drug['rechallenge'])
            display_field("Lot Number", drug['lot_number'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
