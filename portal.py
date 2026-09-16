import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import time
import io
import bcrypt

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Nyamauru High School Portal",
    page_icon="SA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# BRANDING
# ============================================================
SCHOOL_NAME = "Nyamauru High School"
SCHOOL_LOGO_URL = "https://raw.githubusercontent.com/MisheckMusiteyi/School-AIS/main/school_logo_enhanced_white_bg.png"
# NOTE: SHEET_NAME must match the exact filename of your Google Sheet
# document. If you ever rename the Sheet itself, update this to match.
# NOTE: SHEET_NAME is just for display/reference — the app actually opens
# the spreadsheet by its ID (below), not by searching for its name. The
# ID is the long string in the middle of the Sheet's URL:
# https://docs.google.com/spreadsheets/d/THIS_PART_HERE/edit
SHEET_NAME = "School AIS"
SPREADSHEET_ID = "11rQPWhtGymnAjJ_xmFsHVsX1mdlli6AnSouSj5JQL3w"

# Colors (from logo — sky blue and white)
PRIMARY = "#0A9EE8"
PRIMARY_DARK = "#0678B0"
TEXT_DARK = "#0B2A3D"
WHITE = "#FFFFFF"
OFF_WHITE = "#F7FBFE"
CARD_BORDER = "#CFE8F7"
CARD_ALT_ROW = "#EAF6FD"
GREEN = "#4CAF50"
RED = "#E74C3C"
SKY_BLUE = "#4A7A99"
LIGHT_GREY = "#CFE8F7"
FAINT_BLUE = "#EAF6FD"
HOVER_PRIMARY = "#DCEFFB"

# ============================================================
# CSS - ZEBRA ACADEMY PRIMARY THEME
# ============================================================
def inject_css():
    st.markdown(f"""
    <style>
        :root, [data-theme="light"], [data-theme="dark"] {{
            --background-color: {OFF_WHITE} !important;
            --secondary-background-color: {WHITE} !important;
            --text-color: {TEXT_DARK} !important;
            --font: 'Georgia', 'Times New Roman', serif !important;
            --primary-color: {PRIMARY} !important;
            color-scheme: light !important;
        }}
        
        html {{
            color-scheme: light !important;
        }}
        
        html, body, [data-testid="stAppViewContainer"], .main, .block-container,
        [data-testid="stApp"], [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stBottomBlockContainer"] {{
            background-color: {OFF_WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        
        html, body, div, p, span, a, li, td, th, label, input, select, textarea, button {{
            font-family: 'Georgia', 'Times New Roman', serif !important;
        }}
        
        [style*="Material Symbols"], .material-symbols-outlined, .material-symbols-rounded,
        .material-symbols-sharp, [data-testid="stMarkdownContainer"] span[style*="font-family: Material"] {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                         'Material Symbols Sharp', sans-serif !important;
        }}
        
        .stButton > button {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
        }}
        .stButton > button:hover {{
            background-color: {PRIMARY_DARK} !important;
            color: {WHITE} !important;
        }}
        .stButton > button p, .stButton > button span, .stButton > button div,
        .stButton > button label, .stButton > button * {{
            color: {WHITE} !important;
            font-family: 'Georgia', 'Times New Roman', serif !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
        }}
        .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span,
        .stTabs [aria-selected="true"] div, .stTabs [aria-selected="true"] * {{
            color: {WHITE} !important;
        }}
        .stTabs [aria-selected="false"] {{
            color: {TEXT_DARK} !important;
        }}
        .stTabs [aria-selected="false"] p, .stTabs [aria-selected="false"] span {{
            color: {TEXT_DARK} !important;
        }}
        
        section[data-testid="stSidebar"][aria-expanded="true"] {{
            background-color: {PRIMARY} !important;
            min-width: 300px !important;
            max-width: 300px !important;
            width: 300px !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}
        [data-testid="stSidebar"] button {{
            background-color: {PRIMARY_DARK} !important;
            border: none !important;
            border-radius: 6px !important;
            color: {WHITE} !important;
        }}
        [data-testid="stSidebar"] button:hover {{
            background-color: #4A1522 !important;
        }}
        [data-testid="stSidebar"] button p, [data-testid="stSidebar"] button span,
        [data-testid="stSidebar"] button div, [data-testid="stSidebar"] button * {{
            color: {WHITE} !important;
        }}
        
        [data-testid*="ollapse" i] svg,
        [data-testid*="ollapse" i] span,
        [data-testid*="ollapse" i] p {{
            font-size: 0 !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
        }}
        [data-testid*="ollapse" i] button {{
            background-color: {PRIMARY} !important;
            border: none !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            min-width: 30px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
        }}
        [data-testid="collapsedControl"] button::after {{
            content: ">" !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 16px !important;
            font-weight: bold !important;
            color: {WHITE} !important;
            line-height: 1 !important;
        }}
        [data-testid*="ollapse" i]:not([data-testid="collapsedControl"]) button::after {{
            content: "<" !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 16px !important;
            font-weight: bold !important;
            color: {WHITE} !important;
            line-height: 1 !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {PRIMARY} !important;
            font-family: 'Georgia', 'Times New Roman', serif !important;
        }}
        
        input, textarea, select {{
            color: {TEXT_DARK} !important;
            background-color: {WHITE} !important;
            border: 1px solid {CARD_BORDER} !important;
        }}
        label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label {{
            color: {TEXT_DARK} !important;
        }}
        
        [data-testid="stDataFrame"] table,
        .stDataFrame table,
        .dataframe table {{
            border-collapse: collapse !important;
            border: 1px solid {CARD_BORDER} !important;
        }}
        [data-testid="stDataFrame"] th,
        .stDataFrame th,
        .dataframe th {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            padding: 12px 15px !important;
            font-weight: bold !important;
            border-bottom: 2px solid {PRIMARY_DARK} !important;
        }}
        [data-testid="stDataFrame"] td,
        .stDataFrame td,
        .dataframe td {{
            padding: 10px 15px !important;
            color: {TEXT_DARK} !important;
            border-bottom: 1px solid {CARD_BORDER} !important;
        }}
        [data-testid="stDataFrame"] tr:nth-child(odd) td,
        .stDataFrame tr:nth-child(odd) td,
        .dataframe tr:nth-child(odd) td {{
            background-color: {WHITE} !important;
        }}
        [data-testid="stDataFrame"] tr:nth-child(even) td,
        .stDataFrame tr:nth-child(even) td,
        .dataframe tr:nth-child(even) td {{
            background-color: {FAINT_BLUE} !important;
        }}
        [data-testid="stDataFrame"] tr:hover td,
        .stDataFrame tr:hover td,
        .dataframe tr:hover td {{
            background-color: {HOVER_PRIMARY} !important;
        }}
        
        [data-testid="stTable"] table {{
            border-collapse: collapse !important;
            border: 1px solid {CARD_BORDER} !important;
        }}
        [data-testid="stTable"] th {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            padding: 12px 15px !important;
            font-weight: bold !important;
        }}
        [data-testid="stTable"] td {{
            padding: 10px 15px !important;
            color: {TEXT_DARK} !important;
            border-bottom: 1px solid {CARD_BORDER} !important;
        }}
        [data-testid="stTable"] tr:nth-child(odd) td {{
            background-color: {WHITE} !important;
        }}
        [data-testid="stTable"] tr:nth-child(even) td {{
            background-color: {FAINT_BLUE} !important;
        }}
        [data-testid="stTable"] tr:hover td {{
            background-color: {HOVER_PRIMARY} !important;
        }}
        
        [data-testid="stMetricValue"] {{
            color: {PRIMARY} !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {TEXT_DARK} !important;
        }}
        
        .stAlert, [data-testid="stAlert"] {{
            color: {TEXT_DARK} !important;
        }}
        .stAlert p, [data-testid="stAlert"] p {{
            color: {TEXT_DARK} !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] > div {{
            color: {TEXT_DARK} !important;
            background-color: {WHITE} !important;
        }}
        
        .stRadio label, .stRadio p, .stRadio span {{
            color: {TEXT_DARK} !important;
        }}
        
        .stCheckbox label, .stCheckbox p, .stCheckbox span {{
            color: {TEXT_DARK} !important;
        }}
        
        .streamlit-expanderHeader {{
            color: {TEXT_DARK} !important;
        }}
        
        .block-container {{
            padding-top: 24px !important;
        }}
        
        .top-banner {{
            background-color: {PRIMARY};
            padding: 20px 40px;
            display: flex;
            align-items: center;
            gap: 20px;
            border-radius: 10px;
            margin: 0 0 30px 0;
        }}
        .top-banner img {{
            height: 60px;
            border-radius: 8px;
        }}
        .top-banner h1 {{
            color: #000000 !important;
            margin: 0;
            font-size: 28px;
        }}
        
        .login-container {{
            max-width: 450px;
            margin: 0 auto;
            background: {WHITE};
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid {CARD_BORDER};
        }}
        .login-container h3 {{
            color: {PRIMARY} !important;
        }}
        .login-container label {{
            color: {TEXT_DARK} !important;
        }}
        
        .bottom-footer {{
            background-color: {PRIMARY};
            color: {WHITE};
            text-align: center;
            padding: 15px;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            font-size: 13px;
        }}
        
        .dash-card {{
            background: {WHITE};
            border-radius: 10px;
            border: 1px solid {CARD_BORDER};
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .dash-card-header {{
            background-color: {PRIMARY};
            color: {WHITE} !important;
            padding: 14px 20px;
            font-size: 16px;
            font-weight: bold;
        }}
        .dash-card-body {{
            padding: 20px;
        }}
        
        /* Native st.container(border=True) — used for any card that holds
           live widgets (inputs, buttons, dataframes), since wrapping those
           in a plain HTML <div> via st.markdown doesn't actually nest them
           in the DOM and leaves an empty box behind. This gives the real
           Streamlit container the same rounded-card look as .dash-card. */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 10px !important;
            border-color: {CARD_BORDER} !important;
            background: {WHITE} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] h4 {{
            color: {PRIMARY} !important;
            border-bottom: 2px solid {CARD_BORDER};
            padding-bottom: 10px;
            margin-bottom: 14px;
            margin-top: 0;
        }}
        .dash-card-body p, .dash-card-body span, .dash-card-body div,
        .dash-card-body label, .dash-card-body li {{
            color: {TEXT_DARK} !important;
        }}
        
        .dash-card table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid {CARD_BORDER};
        }}
        .dash-card th {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            padding: 12px 15px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid {PRIMARY_DARK};
        }}
        .dash-card td {{
            padding: 10px 15px;
            border-bottom: 1px solid {CARD_BORDER};
            color: {TEXT_DARK} !important;
        }}
        .dash-card tr:nth-child(odd) td {{
            background-color: {WHITE};
        }}
        .dash-card tr:nth-child(even) td {{
            background-color: {FAINT_BLUE};
        }}
        .dash-card tr:hover td {{
            background-color: {HOVER_PRIMARY} !important;
        }}
        
        .dash-card-body table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid {CARD_BORDER};
        }}
        .dash-card-body table th {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            padding: 12px 15px;
            text-align: left;
            font-weight: bold;
        }}
        .dash-card-body table td {{
            padding: 10px 15px;
            border-bottom: 1px solid {CARD_BORDER};
            color: {TEXT_DARK} !important;
        }}
        .dash-card-body table tr:nth-child(odd) td {{
            background-color: {WHITE};
        }}
        .dash-card-body table tr:nth-child(even) td {{
            background-color: {FAINT_BLUE};
        }}
        .dash-card-body table tr:hover td {{
            background-color: {HOVER_PRIMARY} !important;
        }}
        
        .metric-card {{
            background: {WHITE};
            border-radius: 10px;
            border: 1px solid {CARD_BORDER};
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: {PRIMARY};
        }}
        .metric-label {{
            font-size: 13px;
            color: {SKY_BLUE};
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-grid {{
            display: grid;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .metric-grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
        .metric-grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
        .metric-grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
        .metric-grid-6 {{ grid-template-columns: repeat(6, 1fr); }}
        @media (max-width: 900px) {{
            .metric-grid-3, .metric-grid-4, .metric-grid-6 {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 550px) {{
            .metric-grid-2, .metric-grid-3, .metric-grid-4, .metric-grid-6 {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .positive {{
            color: {GREEN} !important;
            font-weight: bold;
        }}
        .negative {{
            color: {RED} !important;
            font-weight: bold;
        }}
        
        .avatar-circle {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background-color: {PRIMARY};
            color: {WHITE};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
            margin: 0 auto;
        }}
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        [data-testid="stFileUploadDropzone"] {{
            background-color: {WHITE} !important;
            border: 2px dashed {CARD_BORDER} !important;
            border-radius: 10px !important;
            padding: 20px !important;
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 16px !important;
            min-height: 70px !important;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] {{
            display: flex !important;
            flex-direction: column !important;
            gap: 2px !important;
            flex: 1 1 auto !important;
            min-width: 180px !important;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] div,
        [data-testid="stFileUploaderDropzoneInstructions"] span,
        [data-testid="stFileUploaderDropzoneInstructions"] small {{
            color: {TEXT_DARK} !important;
            font-family: 'Georgia', 'Times New Roman', serif !important;
            display: block !important;
            position: static !important;
        }}
        [data-testid="stFileUploadDropzone"] section {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            width: 100% !important;
            gap: 16px !important;
            position: static !important;
        }}
        [data-testid="stFileUploadDropzone"] button {{
            position: static !important;
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
            border: none !important;
            border-radius: 6px !important;
            flex: 0 0 auto !important;
            white-space: nowrap !important;
        }}
        [data-testid="stFileUploadDropzone"] button span,
        [data-testid="stFileUploadDropzone"] button p {{
            color: {WHITE} !important;
            position: static !important;
        }}
        
        .lifetime-badge {{
            display: inline-block;
            background-color: {PRIMARY};
            color: {WHITE} !important;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-left: 8px;
        }}
        .term-badge {{
            display: inline-block;
            background-color: {SKY_BLUE};
            color: {WHITE} !important;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-left: 8px;
        }}
        
        hr, .section-divider {{
            border: none;
            border-top: 2px solid {PRIMARY};
            margin: 30px 0;
        }}
        
        .stMultiSelect label {{
            color: {TEXT_DARK} !important;
        }}
        .stMultiSelect div[data-baseweb="select"] > div {{
            color: {TEXT_DARK} !important;
        }}
        
        .stDateInput label {{
            color: {TEXT_DARK} !important;
        }}
        .stDateInput input {{
            color: {TEXT_DARK} !important;
        }}
        
        /* --- Widgets that pull from Streamlit's live theme color rather than
           plain CSS, and so can drift from the palette above on theme changes --- */
        
        a, a:visited {{
            color: {PRIMARY} !important;
        }}
        
        [data-baseweb="tooltip"], [data-baseweb="popover"] {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        
        /* Toggle switches */
        [data-baseweb="checkbox"] [aria-checked="true"] > div:first-child,
        [data-testid="stToggle"] [aria-checked="true"] {{
            background-color: {PRIMARY} !important;
            border-color: {PRIMARY} !important;
        }}
        
        /* Slider track/handle/labels */
        [data-testid="stSlider"] [role="slider"] {{
            background-color: {PRIMARY} !important;
            border-color: {PRIMARY} !important;
        }}
        [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{
            background-color: {PRIMARY} !important;
        }}
        [data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
        [data-testid="stSliderThumbValue"] {{
            color: {TEXT_DARK} !important;
        }}
        
        /* Progress bar */
        [data-testid="stProgress"] > div > div > div {{
            background-color: {PRIMARY} !important;
        }}
        
        /* Spinner */
        [data-testid="stSpinner"] svg circle {{
            stroke: {PRIMARY} !important;
        }}
        [data-testid="stSpinner"] p {{
            color: {TEXT_DARK} !important;
        }}
        
        /* Toasts / notifications */
        [data-testid="stToast"] {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        
        /* Multiselect selected-item pills */
        [data-baseweb="tag"] {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
        }}
        [data-baseweb="tag"] span {{
            color: {WHITE} !important;
        }}
        
        /* --- Date input box + its calendar popover ---
           BaseWeb's Datepicker draws its own colors and ignores the page's
           color-scheme, so every layer of its wrapper needs to be forced
           white explicitly — different Streamlit versions nest this
           slightly differently, so every plausible selector is covered. */
        
        [data-testid^="stDateInput"],
        [data-testid^="stDateInput"] > div,
        [data-testid^="stDateInput"] div,
        [data-testid="stDateInput"] [data-baseweb="base-input"],
        [data-testid="stDateInput"] [data-baseweb="input"] {{
            background-color: {WHITE} !important;
        }}
        [data-testid^="stDateInput"] input {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        [data-testid^="stDateInput"] svg {{
            fill: {TEXT_DARK} !important;
        }}
        
        [data-baseweb="calendar"] {{
            background-color: {WHITE} !important;
        }}
        [data-baseweb="calendar"] *, [data-baseweb="calendar"] *::before, [data-baseweb="calendar"] *::after {{
            color: {TEXT_DARK} !important;
            opacity: 1 !important;
        }}
        [data-baseweb="calendar"] div {{
            background-color: {WHITE} !important;
        }}
        
        /* --- Text / number / textarea inputs, same treatment as date
           inputs above, so nothing renders with a stray dark background
           regardless of which Streamlit internals happen to apply. --- */
        [data-testid^="stTextInput"],
        [data-testid^="stTextInput"] div,
        [data-testid^="stNumberInput"],
        [data-testid^="stNumberInput"] div,
        [data-testid^="stTextArea"],
        [data-testid^="stTextArea"] div {{
            background-color: {WHITE} !important;
        }}
        [data-testid^="stTextInput"] input,
        [data-testid^="stNumberInput"] input,
        [data-testid^="stTextArea"] textarea {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        [data-baseweb="calendar"] button {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        [data-baseweb="calendar"] button:hover {{
            background-color: {HOVER_PRIMARY} !important;
        }}
        [data-baseweb="calendar"] [aria-disabled="true"] {{
            color: {CARD_BORDER} !important;
        }}
        [data-baseweb="calendar"] [aria-selected="true"],
        [data-baseweb="calendar"] [aria-selected="true"]:hover {{
            background-color: {PRIMARY} !important;
            color: {WHITE} !important;
        }}
        [data-baseweb="calendar"] svg {{
            fill: {TEXT_DARK} !important;
        }}
        
        /* Same dark-render issue can hit selectbox/multiselect dropdown menus */
        [data-baseweb="menu"], [data-baseweb="popover"] ul[role="listbox"] {{
            background-color: {WHITE} !important;
        }}
        [data-baseweb="menu"] li, [role="option"] {{
            background-color: {WHITE} !important;
            color: {TEXT_DARK} !important;
        }}
        [role="option"]:hover, [role="option"][aria-selected="true"] {{
            background-color: {HOVER_PRIMARY} !important;
            color: {TEXT_DARK} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session():
    defaults = {
        'logged_in': False,
        'username': None,
        'admin_page': "Overview",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================
@st.cache_resource
def connect_to_sheets():
    try:
        creds_dict = dict(st.secrets["connections"]["gsheet"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
    except Exception:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json",
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
    client = gspread.authorize(credentials)
    return client

@st.cache_data(ttl=60, show_spinner=False)
def load_data(sheet_name):
    """
    Cached for 60 seconds. Several pages (Income Statement, Balance
    Sheet in particular) call load_data() for the same sheet multiple
    times in one page render — without caching, that burns through
    Google's free-tier read quota (60 reads/minute) almost immediately.
    write_data/update_cell/overwrite_sheet all clear this cache after a
    successful write, so new entries still show up right away rather
    than waiting out the 60-second window.
    """
    client = connect_to_sheets()
    for attempt in range(3):
        try:
            sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
            df = pd.DataFrame(sheet.get_all_records())
            df.columns = df.columns.astype(str).str.strip()
            return df
        except Exception as e:
            if attempt < 2:
                connect_to_sheets.clear()
                client = connect_to_sheets()
                time.sleep(1)
            else:
                st.error(f"Failed to load '{sheet_name}': {e}")
                return pd.DataFrame()

def write_data(sheet_name, data_dict):
    """
    Write one row to a worksheet, keyed by COLUMN HEADER NAME rather than
    position. This makes writes immune to the sheet's columns being
    reordered, and means a typo in a header shows up as a blank cell
    instead of data silently landing under the wrong column.

    data_dict: {"Header Name": value, ...}
    Any header present in the sheet but missing from data_dict is written
    as an empty string. Keys in data_dict that don't match any header in
    the sheet are ignored (so double-check your header spelling matches
    exactly, including capitalization).
    """
    client = connect_to_sheets()
    for attempt in range(3):
        try:
            sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
            headers = [h.strip() for h in sheet.row_values(1)]
            if not headers:
                st.error(f"'{sheet_name}' has no header row — cannot map columns.")
                return False
            row = [data_dict.get(h, "") for h in headers]
            sheet.append_row(row, value_input_option="USER_ENTERED")
            time.sleep(0.7)  # let Sheets settle before any immediate re-read
            load_data.clear()
            return True
        except Exception as e:
            if attempt < 2:
                connect_to_sheets.clear()
                client = connect_to_sheets()
                time.sleep(2)
            else:
                st.error(f"Failed to write to '{sheet_name}': {e}")
                return False

def update_cell(sheet_name, row, col, value):
    client = connect_to_sheets()
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        sheet.update_cell(row, col, value)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to update cell: {e}")
        return False

# ============================================================
# STUDENT NUMBER & DROPDOWN HELPERS
# ============================================================
def generate_student_number(df_students):
    """
    Generates the next Student Number in the form R{YY}{NNN}, e.g.
    R26001, R26002... Sequence is scoped to the current year and derived
    from the highest number seen under that year's prefix ACROSS BOTH the
    Students sheet and Fee Payments — not just Students alone.

    Why both: removing a student only deletes their Students row, on
    purpose, so their payment history stays intact (see admin_all_students).
    But if the generator only looked at Students, a freed-up number could
    get handed to a brand new student — and that new student would then
    inherit the removed student's old payments, since they're matched by
    Student Number. Checking Fee Payments too means a number stays
    retired forever once it's been used, even after the student who held
    it is removed.
    """
    year_prefix = f"R{datetime.now().strftime('%y')}"
    max_seq = 0

    def scan(df, col):
        nonlocal max_seq
        if df is None or df.empty or col not in df.columns:
            return
        for val in df[col].astype(str).str.strip():
            if val.startswith(year_prefix) and val[len(year_prefix):].isdigit():
                max_seq = max(max_seq, int(val[len(year_prefix):]))

    scan(df_students, "Student Number")
    scan(load_data("Fee Payments"), "Student Number")

    return f"{year_prefix}{max_seq + 1:03d}"

def build_student_dropdown(df_students):
    """
    Returns (display_labels, label_to_student_number) for an admin
    selectbox. Shows just the student's name normally; if two students
    share the exact same name, appends the Student Number in parentheses
    for just that pair so they stay distinguishable.
    """
    label_to_id = {}
    if df_students.empty or "Student Number" not in df_students.columns:
        return ["Select student..."], label_to_id

    df = df_students.copy()
    df.columns = df.columns.astype(str).str.strip()
    name_counts = df["Student Name"].astype(str).str.strip().value_counts()

    for _, row in df.iterrows():
        name = str(row.get("Student Name", "")).strip()
        sid = str(row.get("Student Number", "")).strip()
        if not name or not sid:
            continue
        label = f"{name} ({sid})" if name_counts.get(name, 0) > 1 else name
        label_to_id[label] = sid

    return ["Select student..."] + sorted(label_to_id.keys()), label_to_id

# ============================================================
# LEVELS & ANNUAL FEE STRUCTURE
# ============================================================
# Edit this to match your actual fee structure — plain Python, no need
# to touch the Google Sheet to change it. Students enrol on a
# year-by-year basis; each enrolment year has its own annual fee.
LEVELS = ["O Level", "A Level"]

ANNUAL_FEE_BY_LEVEL = {
    "O Level": 450.0,
    "A Level": 600.0,
}

# ============================================================

# ACCOUNTING MODULE — REGISTERS + FINANCIAL STATEMENTS
# ============================================================
# New Google Sheet tabs required (create these with EXACTLY these
# header rows for the statements below to work):
#
#   "Students"         -> Student Number | Student Name | Academic Year | Level | Annual Fee
#   "Fee Payments"     -> Student Number | Student Name | Academic Year | Date | Amount Paid | Payment Method
#   "Staff Register"   -> Financial Year | Category | Number of Staff | Monthly Salary per Staff
#   "Fixed Assets"     -> Category | Description | Cost | Date Acquired | Depreciation Rate (%)
#   "Loans"            -> Loan Type | Lender | Principal Amount | Interest Rate (%) | Start Date
#   "Creditors"        -> Description | Amount | Date
#   "Equity"           -> Item | Amount | Date
#   "Opening Balance"  -> Date | Amount
#
# Financial-year handling, spelled out:
#   - Expenses / Other Income: the year is simply the calendar year of
#     the Date column — no separate month/year field to keep in sync.
#   - Staff Register: keeps its own explicit Financial Year, since it's
#     a standing rate ("this many staff at this salary, for 2026"), not
#     a dated transaction.
#   - Fixed Assets / Loans: no year field — depreciation and interest
#     are worked out fresh from Date Acquired / Start Date every time.
#   - Fee Payments carries TWO dates on purpose: Date (when the cash
#     came in — drives Cash) and Academic Year (which year's fees this
#     payment is FOR — drives which year's revenue it counts as). A
#     payment dated 2026 with Academic Year 2027 is a prepayment: it
#     adds to Cash now but shows as Deferred Income (a liability) until
#     the 2027 Income Statement is run.
#
# Other simplifications, stated plainly (this is a lightweight system,
# not full double-entry bookkeeping):
#   - Staff Register is entered ONCE PER financial year per category.
#     Re-saving a year overwrites that year's figures for each category
#     (the app keeps the latest entry per Category+Year, so correcting
#     a mistake is just re-submitting the form).
#   - Depreciation is straight-line, non-prorated: Cost x Rate% x full
#     years owned, capped so Net Book Value never goes below 0.
#   - Finance costs (loan interest) are simple, non-compounding:
#     Principal x Rate% per year the loan's been active, treated as
#     paid in cash the same year incurred.
#   - Income tax is a flat 25% of Surplus before tax (0 if a deficit),
#     and is assumed UNPAID at each year end for the CURRENT year only
#     (shown as a Tax Liability); earlier years' tax is assumed since
#     settled, so it reduces cash.
#   - The Balance Sheet is always "as at today" (a live snapshot from
#     all data entered so far). The Income Statement is run for
#     whichever financial year you pick.
#   - Retained earnings is the residual needed to balance the Balance
#     Sheet (Assets - Liabilities - Share Capital - Share Premium -
#     Revaluation Reserve) — standard practice for a system that isn't
#     running full double-entry ledgers.
#   - Fixed Assets, Loans, Creditors and Equity registers are add-only;
#     to correct or remove an entry (e.g. a loan repaid, an asset sold,
#     a creditor paid off), edit the Google Sheet tab directly.

STAFF_CATEGORIES = [
    "Student Teachers", "Ordinary Teachers", "Senior Teachers",
    "Vice Headmaster", "Headmaster", "Caretakers", "Admin Team",
]

ASSET_CATEGORIES = [
    "Buildings", "Fixtures and Fittings", "Computer Software",
    "Motor Vehicles", "Computers",
]

LOAN_TYPES = ["Long-term", "Short-term"]

EQUITY_ITEMS = ["Ordinary Share Capital", "Share Premium", "Revaluation Reserve"]

# Expenses-sheet categories folded into the Income Statement, mapped to
# IFRS-style presentation labels. Staff costs come from the Staff
# Register, not from this list — "Salaries" is not a category here.
EXPENSE_LINE_LABELS = {
    "Utilities": "Utilities",
    "Supplies": "Teaching materials and supplies",
    "Maintenance": "Repairs and maintenance",
    "Food": "Food and catering",
    "Transport": "Transport",
    "Printing": "Printing and stationery",
    "Events": "Events and extracurricular activities",
    "Other": "Sundry expenses",
}

CORPORATE_TAX_RATE = 0.25


def overwrite_sheet(sheet_name, df):
    """Replace ALL rows in a worksheet with the given DataFrame (used for
    'register' style tabs where old rows sometimes need to disappear,
    unlike the append-only transaction logs elsewhere in this app)."""
    client = connect_to_sheets()
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        sheet.clear()
        values = [df.columns.tolist()] + df.astype(str).values.tolist()
        sheet.update(values)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to save '{sheet_name}': {e}")
        return False


def _year_of(value):
    """Extract a calendar year from a date-like value, or 0 if unusable."""
    try:
        return pd.to_datetime(value).year
    except Exception:
        return 0


def get_financial_years():
    """Distinct financial years seen anywhere in the system, plus the
    current year, newest first. Includes Fee Payments' Academic Year
    even when it's a future year (a prepayment), so that year is
    selectable on the Income Statement once it arrives."""
    years = {date.today().year}
    for sheet_name, date_col in [("Expenses", "Date"), ("Other Income", "Date")]:
        df = load_data(sheet_name)
        if not df.empty and date_col in df.columns:
            df.columns = df.columns.astype(str).str.strip()
            for d in df[date_col].dropna():
                y = _year_of(d)
                if y:
                    years.add(y)
    df_fees = load_data("Fee Payments")
    if not df_fees.empty and "Academic Year" in df_fees.columns:
        df_fees.columns = df_fees.columns.astype(str).str.strip()
        for y in df_fees["Academic Year"].dropna().unique():
            try:
                years.add(int(y))
            except (ValueError, TypeError):
                pass
    df_staff = load_data("Staff Register")
    if not df_staff.empty and "Financial Year" in df_staff.columns:
        df_staff.columns = df_staff.columns.astype(str).str.strip()
        for y in df_staff["Financial Year"].dropna().unique():
            try:
                years.add(int(y))
            except (ValueError, TypeError):
                pass
    return sorted(years, reverse=True)


def compute_staff_costs_for_year(year):
    """Returns (annual staff cost total, breakdown DataFrame) for a
    financial year, taking the latest saved row per category."""
    df = load_data("Staff Register")
    empty_cols = ["Category", "Number of Staff", "Monthly Salary per Staff", "Monthly Total", "Annual Total"]
    if df.empty or "Financial Year" not in df.columns:
        return 0.0, pd.DataFrame(columns=empty_cols)
    df.columns = df.columns.astype(str).str.strip()
    df_year = df[df["Financial Year"].astype(str).str.strip() == str(year)].copy()
    if df_year.empty:
        return 0.0, pd.DataFrame(columns=empty_cols)
    df_year = df_year.drop_duplicates(subset=["Category"], keep="last")
    df_year["Number of Staff"] = pd.to_numeric(df_year["Number of Staff"], errors="coerce").fillna(0)
    df_year["Monthly Salary per Staff"] = pd.to_numeric(df_year["Monthly Salary per Staff"], errors="coerce").fillna(0)
    df_year["Monthly Total"] = df_year["Number of Staff"] * df_year["Monthly Salary per Staff"]
    df_year["Annual Total"] = df_year["Monthly Total"] * 12
    return df_year["Annual Total"].sum(), df_year[empty_cols]


def compute_fixed_assets():
    """Returns (assets DataFrame with NBV/depreciation columns added,
    total annual depreciation charge, total net book value), both as
    at today."""
    df = load_data("Fixed Assets")
    if df.empty:
        return pd.DataFrame(), 0.0, 0.0
    df.columns = df.columns.astype(str).str.strip()
    df["Cost"] = pd.to_numeric(df.get("Cost", 0), errors="coerce").fillna(0)
    df["Depreciation Rate (%)"] = pd.to_numeric(df.get("Depreciation Rate (%)", 0), errors="coerce").fillna(0)
    df["Years Owned"] = df.get("Date Acquired", "").apply(lambda d: max(date.today().year - _year_of(d), 0))
    df["Annual Depreciation"] = df["Cost"] * df["Depreciation Rate (%)"] / 100
    df["Accumulated Depreciation"] = (df["Annual Depreciation"] * df["Years Owned"]).clip(upper=df["Cost"])
    df["Net Book Value"] = (df["Cost"] - df["Accumulated Depreciation"]).clip(lower=0)
    return df, df["Annual Depreciation"].sum(), df["Net Book Value"].sum()


def compute_loans():
    """Returns (loans DataFrame, total long-term principal, total
    short-term principal, total annual finance cost/interest)."""
    df = load_data("Loans")
    if df.empty:
        return pd.DataFrame(), 0.0, 0.0, 0.0
    df.columns = df.columns.astype(str).str.strip()
    df["Principal Amount"] = pd.to_numeric(df.get("Principal Amount", 0), errors="coerce").fillna(0)
    df["Interest Rate (%)"] = pd.to_numeric(df.get("Interest Rate (%)", 0), errors="coerce").fillna(0)
    df["Annual Interest"] = df["Principal Amount"] * df["Interest Rate (%)"] / 100
    long_term = df[df.get("Loan Type", "").astype(str).str.strip() == "Long-term"]["Principal Amount"].sum()
    short_term = df[df.get("Loan Type", "").astype(str).str.strip() == "Short-term"]["Principal Amount"].sum()
    return df, long_term, short_term, df["Annual Interest"].sum()


def compute_total_debtors():
    """Total unpaid fees as at today: for every student-enrolment row
    (one row per student per academic year) up to and including the
    current year, Annual Fee minus whatever's been paid against that
    same Academic Year."""
    today_year = date.today().year
    df_students = load_data("Students")
    if df_students.empty or "Student Number" not in df_students.columns:
        return 0.0
    df_students.columns = df_students.columns.astype(str).str.strip()
    df_payments = load_data("Fee Payments")
    if not df_payments.empty:
        df_payments.columns = df_payments.columns.astype(str).str.strip()

    total_owing = 0.0
    for _, row in df_students.iterrows():
        try:
            acad_year = int(row.get("Academic Year", 0))
        except (ValueError, TypeError):
            continue
        if acad_year <= 0 or acad_year > today_year:
            continue
        expected = pd.to_numeric(row.get("Annual Fee", 0), errors="coerce") or 0.0
        sid = str(row.get("Student Number", "")).strip()
        paid = 0.0
        if not df_payments.empty and "Student Number" in df_payments.columns and "Academic Year" in df_payments.columns:
            match = df_payments[
                (df_payments["Student Number"].astype(str).str.strip() == sid) &
                (df_payments["Academic Year"].astype(str).str.strip() == str(acad_year))
            ]
            paid = safe_sum(match, "Amount Paid")
        total_owing += max(expected - paid, 0.0)
    return total_owing


def compute_deferred_income():
    """Fees already received (as cash) for an Academic Year that hasn't
    arrived yet — Income received in advance, a current liability."""
    today_year = date.today().year
    df_payments = load_data("Fee Payments")
    if df_payments.empty or "Academic Year" not in df_payments.columns:
        return 0.0
    df_payments.columns = df_payments.columns.astype(str).str.strip()
    future = df_payments[pd.to_numeric(df_payments["Academic Year"], errors="coerce") > today_year]
    return safe_sum(future, "Amount Paid")


def compute_income_statement(year):
    """Statement of Comprehensive Income for one financial year. Fee
    revenue is recognised by Academic Year (when the fee is FOR), not
    by when the cash was received — so a prepayment for a later year
    doesn't count as this year's revenue."""
    df_fees = load_data("Fee Payments")
    df_other = load_data("Other Income")
    df_exp = load_data("Expenses")
    for df in (df_fees, df_other, df_exp):
        if not df.empty:
            df.columns = df.columns.astype(str).str.strip()

    fee_income = 0.0
    if not df_fees.empty and "Academic Year" in df_fees.columns:
        rows = df_fees[pd.to_numeric(df_fees["Academic Year"], errors="coerce") == year]
        fee_income = safe_sum(rows, "Amount Paid")

    def year_filter_by_date(df):
        if df.empty or "Date" not in df.columns:
            return df
        return df[df["Date"].apply(_year_of) == year]

    other_income = safe_sum(year_filter_by_date(df_other), "Amount")
    df_exp_y = year_filter_by_date(df_exp)
    total_revenue = fee_income + other_income

    expense_lines = {cat: 0.0 for cat in EXPENSE_LINE_LABELS}
    if not df_exp_y.empty and "Category" in df_exp_y.columns:
        for cat in EXPENSE_LINE_LABELS:
            rows = df_exp_y[df_exp_y["Category"].astype(str).str.strip() == cat]
            expense_lines[cat] = safe_sum(rows, "Amount")

    staff_costs, _ = compute_staff_costs_for_year(year)

    df_assets, _, _ = compute_fixed_assets()
    depreciation = 0.0
    if not df_assets.empty and "Date Acquired" in df_assets.columns:
        owned_by_then = df_assets[df_assets["Date Acquired"].apply(_year_of) <= year]
        depreciation = owned_by_then["Annual Depreciation"].sum()

    df_loans, _, _, _ = compute_loans()
    finance_costs = 0.0
    if not df_loans.empty and "Start Date" in df_loans.columns:
        active_loans = df_loans[df_loans["Start Date"].apply(_year_of) <= year]
        finance_costs = active_loans["Annual Interest"].sum()

    total_opex = staff_costs + sum(expense_lines.values()) + depreciation
    operating_surplus = total_revenue - total_opex
    surplus_before_tax = operating_surplus - finance_costs
    tax_expense = max(surplus_before_tax, 0.0) * CORPORATE_TAX_RATE
    surplus_for_year = surplus_before_tax - tax_expense

    return {
        "year": year,
        "fee_income": fee_income, "other_income": other_income, "total_revenue": total_revenue,
        "staff_costs": staff_costs, "expense_lines": expense_lines, "depreciation": depreciation,
        "total_opex": total_opex, "operating_surplus": operating_surplus,
        "finance_costs": finance_costs, "surplus_before_tax": surplus_before_tax,
        "tax_expense": tax_expense, "surplus_for_year": surplus_for_year,
    }


def compute_cash_position():
    """Cumulative cash and cash equivalents as at today. Unlike the
    Income Statement, fee cash counts in the year it was actually
    RECEIVED (Date), regardless of which Academic Year it's for —
    that gap between cash timing and revenue timing is exactly what
    Deferred Income captures on the Balance Sheet. Depreciation is
    excluded (non-cash). The current year's tax is excluded too
    (assumed unpaid — see Tax Liability); earlier years' tax is
    assumed since settled."""
    today_year = date.today().year

    df_fees = load_data("Fee Payments")
    cash_in_fees = safe_sum(df_fees, "Amount Paid") if not df_fees.empty else 0.0

    df_other = load_data("Other Income")
    cash_in_other = safe_sum(df_other, "Amount") if not df_other.empty else 0.0

    df_exp = load_data("Expenses")
    cash_out_expenses = safe_sum(df_exp, "Amount") if not df_exp.empty else 0.0

    df_staff = load_data("Staff Register")
    cash_out_staff = 0.0
    if not df_staff.empty and "Financial Year" in df_staff.columns:
        df_staff.columns = df_staff.columns.astype(str).str.strip()
        for y in df_staff["Financial Year"].dropna().unique():
            try:
                y_int = int(y)
            except (ValueError, TypeError):
                continue
            if y_int <= today_year:
                total, _ = compute_staff_costs_for_year(y_int)
                cash_out_staff += total

    df_loans, _, _, _ = compute_loans()
    cash_out_interest = 0.0
    if not df_loans.empty:
        for _, row in df_loans.iterrows():
            years_elapsed = max(today_year - _year_of(row.get("Start Date", "")), 0)
            cash_out_interest += row["Principal Amount"] * row["Interest Rate (%)"] / 100 * years_elapsed

    cash_out_tax = 0.0
    for y in get_financial_years():
        if y < today_year:
            cash_out_tax += compute_income_statement(y)["tax_expense"]

    return (cash_in_fees + cash_in_other) - (cash_out_expenses + cash_out_staff + cash_out_interest + cash_out_tax)


def compute_balance_sheet():
    """Statement of Financial Position as at today."""
    today_year = date.today().year
    df_assets, _, _ = compute_fixed_assets()
    nbv_by_category = {}
    for cat in ASSET_CATEGORIES:
        if not df_assets.empty and "Category" in df_assets.columns:
            nbv_by_category[cat] = df_assets[df_assets["Category"].astype(str).str.strip() == cat]["Net Book Value"].sum()
        else:
            nbv_by_category[cat] = 0.0
    total_non_current_assets = sum(nbv_by_category.values())

    debtors = compute_total_debtors()
    cash = compute_cash_position()
    total_current_assets = debtors + cash
    total_assets = total_non_current_assets + total_current_assets

    _, long_term_loans, short_term_loans, _ = compute_loans()

    current_year_tax = compute_income_statement(today_year)["tax_expense"]
    deferred_income = compute_deferred_income()

    df_creditors = load_data("Creditors")
    creditors_total = safe_sum(df_creditors, "Amount") if not df_creditors.empty else 0.0

    total_current_liabilities = short_term_loans + current_year_tax + creditors_total + deferred_income
    total_liabilities = long_term_loans + total_current_liabilities

    df_equity = load_data("Equity")
    share_capital = share_premium = revaluation_reserve = 0.0
    if not df_equity.empty:
        df_equity.columns = df_equity.columns.astype(str).str.strip()
        share_capital = safe_sum(df_equity[df_equity.get("Item", "") == "Ordinary Share Capital"], "Amount")
        share_premium = safe_sum(df_equity[df_equity.get("Item", "") == "Share Premium"], "Amount")
        revaluation_reserve = safe_sum(df_equity[df_equity.get("Item", "") == "Revaluation Reserve"], "Amount")

    retained_earnings = total_assets - total_liabilities - share_capital - share_premium - revaluation_reserve
    total_equity = share_capital + share_premium + revaluation_reserve + retained_earnings

    return {
        "nbv_by_category": nbv_by_category, "total_non_current_assets": total_non_current_assets,
        "debtors": debtors, "cash": cash, "total_current_assets": total_current_assets,
        "total_assets": total_assets,
        "long_term_loans": long_term_loans, "short_term_loans": short_term_loans,
        "current_year_tax": current_year_tax, "creditors_total": creditors_total,
        "deferred_income": deferred_income,
        "total_current_liabilities": total_current_liabilities, "total_liabilities": total_liabilities,
        "share_capital": share_capital, "share_premium": share_premium,
        "revaluation_reserve": revaluation_reserve, "retained_earnings": retained_earnings,
        "total_equity": total_equity,
    }


def df_to_excel_download(df, sheet_label):
    """Turn a (Line, Amount) style DataFrame into an in-memory .xlsx
    file for st.download_button."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_label[:31])
    return buffer.getvalue()


def bank_statement_to_excel(df_stmt, opening_amount, closing_balance, statement_start):
    """
    Builds a properly formatted .xlsx bank statement — letterhead-style
    header block, a colored/bold table header row, currency number
    formatting, borders, and alternating row shading — rather than a
    bare data dump. Returns bytes for st.download_button.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Bank Statement"

    title_font = Font(name="Calibri", size=16, bold=True, color="0B2A3D")
    subtitle_font = Font(name="Calibri", size=11, color="4A7A99")
    header_label_font = Font(name="Calibri", size=10, bold=True)
    body_font = Font(name="Calibri", size=10)
    table_header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    table_header_fill = PatternFill(start_color="0A9EE8", end_color="0A9EE8", fill_type="solid")
    alt_row_fill = PatternFill(start_color="EAF6FD", end_color="EAF6FD", fill_type="solid")
    thin_border = Border(bottom=Side(style="thin", color="CFE8F7"))
    money_format = '#,##0.00'

    ws.merge_cells("A1:F1")
    ws["A1"] = "STATEMENT OF ACCOUNT"
    ws["A1"].font = title_font

    ws.merge_cells("A2:F2")
    ws["A2"] = BANK_NAME
    ws["A2"].font = subtitle_font

    info_rows = [
        ("Account Holder", SCHOOL_NAME),
        ("Statement Date", date.today().strftime("%B %d, %Y")),
        ("Account No", BANK_ACCOUNT_NUMBER),
        ("Account Type", BANK_ACCOUNT_TYPE),
        ("Statement Period From", statement_start.strftime("%d %B %Y") if hasattr(statement_start, "strftime") else str(statement_start)),
        ("Opening Balance", f"${opening_amount:,.2f}"),
        ("Closing Balance", f"${closing_balance:,.2f}"),
    ]
    row = 4
    for label, value in info_rows:
        ws.cell(row=row, column=1, value=label).font = header_label_font
        ws.cell(row=row, column=2, value=value).font = body_font
        row += 1

    table_start = row + 1
    headers = ["Date", "Narration", "Ref No.", "Debit", "Credit", "Balance"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=table_start, column=c, value=h)
        cell.font = table_header_font
        cell.fill = table_header_fill
        cell.alignment = Alignment(horizontal="left")

    for i, (_, r) in enumerate(df_stmt.iterrows()):
        rr = table_start + 1 + i
        values = [r["Date"], r["Narration"], r["Ref No."], r["Debit"] or None, r["Credit"] or None, r["Balance"]]
        for c, v in enumerate(values, start=1):
            cell = ws.cell(row=rr, column=c, value=v)
            cell.font = body_font
            cell.border = thin_border
            if i % 2 == 0:
                cell.fill = alt_row_fill
            if c in (4, 5, 6) and v is not None:
                cell.number_format = money_format

    widths = [12, 38, 12, 12, 12, 14]
    for c, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def bank_statement_to_pdf(df_stmt, opening_amount, closing_balance, statement_start):
    """
    Builds a PDF version of the bank statement using the same
    letterhead-style layout as the Excel export. Returns bytes for
    st.download_button.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("StmtTitle", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#0B2A3D"), spaceAfter=2)
    subtitle_style = ParagraphStyle("StmtSubtitle", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#4A7A99"), spaceAfter=10)
    info_style = ParagraphStyle("StmtInfo", parent=styles["Normal"], fontSize=9.5, leading=14)

    story = [
        Paragraph("STATEMENT OF ACCOUNT", title_style),
        Paragraph(BANK_NAME, subtitle_style),
        Paragraph(
            f"<b>Account Holder:</b> {SCHOOL_NAME}<br/>"
            f"<b>Statement Date:</b> {date.today().strftime('%B %d, %Y')}<br/>"
            f"<b>Account No:</b> {BANK_ACCOUNT_NUMBER} &nbsp;&nbsp; <b>Account Type:</b> {BANK_ACCOUNT_TYPE}<br/>"
            f"<b>Statement Period From:</b> {statement_start.strftime('%d %B %Y') if hasattr(statement_start, 'strftime') else statement_start}<br/>"
            f"<b>Opening Balance:</b> ${opening_amount:,.2f} &nbsp;&nbsp; <b>Closing Balance:</b> ${closing_balance:,.2f}",
            info_style,
        ),
        Spacer(1, 12),
    ]

    table_data = [["Date", "Narration", "Ref No.", "Debit", "Credit", "Balance"]]
    for _, r in df_stmt.iterrows():
        table_data.append([
            r["Date"],
            Paragraph(str(r["Narration"]), styles["Normal"]),
            r["Ref No."],
            f"{r['Debit']:,.2f}" if r["Debit"] else "",
            f"{r['Credit']:,.2f}" if r["Credit"] else "",
            f"{r['Balance']:,.2f}",
        ])

    table = Table(table_data, colWidths=[20 * mm, 62 * mm, 20 * mm, 22 * mm, 22 * mm, 25 * mm], repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A9EE8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (3, 0), (5, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#CFE8F7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(table_data)):
        if i % 2 == 1:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#EAF6FD")))
    table.setStyle(TableStyle(style_commands))
    story.append(table)

    doc.build(story)
    return buffer.getvalue()


# ============================================================
# BANK STATEMENT
# ============================================================
# Presents every cash-affecting transaction (Fee Payments and Other
# Income as credits; Expenses as debits) as a single running ledger,
# styled like a real bank statement. Needs one more Google Sheet tab:
#
#   "Opening Balance" -> Date | Amount
#
# Add-only, like the other registers — the LATEST row is what governs
# (re-submit the form to correct it). Transactions dated before the
# Opening Balance's date are excluded from the ledger, on the
# assumption they're already folded into that opening figure.
BANK_NAME = "NMB Bank Limited"
BANK_ACCOUNT_NUMBER = "59950371005284"
BANK_ACCOUNT_TYPE = "Business Current Account"


def get_opening_balance():
    """Returns (amount, date) from the latest row in the Opening
    Balance register, or (0.0, None) if it hasn't been set yet."""
    df = load_data("Opening Balance")
    if df.empty or "Date" not in df.columns or "Amount" not in df.columns:
        return 0.0, None
    last_row = df.iloc[-1]
    amount = pd.to_numeric(last_row.get("Amount", 0), errors="coerce") or 0.0
    try:
        parsed_date = pd.to_datetime(last_row.get("Date")).date()
    except Exception:
        parsed_date = None
    return amount, parsed_date


def compute_bank_statement(start_date=None, end_date=None):
    """
    Combines Fee Payments + Other Income (credits) and Expenses (debits)
    into one chronological ledger with a running balance, starting from
    the Opening Balance register. start_date/end_date optionally narrow
    the ledger further (on top of the opening-balance date cutoff).
    Returns (DataFrame, opening_amount, opening_date).
    """
    opening_amount, opening_date = get_opening_balance()

    rows = []
    df_fees = load_data("Fee Payments")
    if not df_fees.empty:
        df_fees.columns = df_fees.columns.astype(str).str.strip()
        for _, r in df_fees.iterrows():
            rows.append({
                "Date": r.get("Date", ""),
                "Narration": f"Fee payment - {r.get('Student Name', '')}".strip(),
                "Ref No.": str(r.get("Student Number", "")).strip(),
                "Debit": 0.0,
                "Credit": pd.to_numeric(r.get("Amount Paid", 0), errors="coerce") or 0.0,
            })

    df_other = load_data("Other Income")
    if not df_other.empty:
        df_other.columns = df_other.columns.astype(str).str.strip()
        for _, r in df_other.iterrows():
            desc = str(r.get("Income Description", "")).strip()
            rows.append({
                "Date": r.get("Date", ""),
                "Narration": desc if desc else "Other income",
                "Ref No.": "",
                "Debit": 0.0,
                "Credit": pd.to_numeric(r.get("Amount", 0), errors="coerce") or 0.0,
            })

    df_exp = load_data("Expenses")
    if not df_exp.empty:
        df_exp.columns = df_exp.columns.astype(str).str.strip()
        for _, r in df_exp.iterrows():
            desc = str(r.get("Description", "")).strip()
            cat = str(r.get("Category", "")).strip()
            narration = f"{desc} ({cat})" if desc and cat else (desc or cat or "Expense")
            rows.append({
                "Date": r.get("Date", ""),
                "Narration": narration,
                "Ref No.": "",
                "Debit": pd.to_numeric(r.get("Amount", 0), errors="coerce") or 0.0,
                "Credit": 0.0,
            })

    empty_cols = ["Date", "Narration", "Ref No.", "Debit", "Credit", "Balance"]
    if not rows:
        return pd.DataFrame(columns=empty_cols), opening_amount, opening_date

    df = pd.DataFrame(rows)
    df["_date_parsed"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["_date_parsed"])

    if opening_date:
        df = df[df["_date_parsed"].dt.date >= opening_date]
    if start_date:
        df = df[df["_date_parsed"].dt.date >= start_date]
    if end_date:
        df = df[df["_date_parsed"].dt.date <= end_date]

    if df.empty:
        return pd.DataFrame(columns=empty_cols), opening_amount, opening_date

    df = df.sort_values("_date_parsed", kind="stable").reset_index(drop=True)
    df["Ref No."] = [rn if str(rn).strip() else f"{i + 1:05d}" for i, rn in enumerate(df["Ref No."])]

    balance = opening_amount
    balances = []
    for _, r in df.iterrows():
        balance += r["Credit"] - r["Debit"]
        balances.append(balance)
    df["Balance"] = balances
    df["Date"] = df["_date_parsed"].dt.strftime("%Y-%m-%d")

    return df[empty_cols], opening_amount, opening_date


def hash_password(plain_password):
    """One-way hash for storage. There is no function to reverse this —
    verification only ever checks 'does this input match', it never
    recovers the original password."""
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, stored_value):
    """Check a login attempt against a stored value.

    Supports two shapes of stored_value:
    - A bcrypt hash (starts with $2b$/$2a$/$2y$) -> proper hash check.
    - A legacy plaintext row from before this change -> direct string
      compare, so old rows in the sheet don't lock anyone out. Callers
      should re-hash and save the password after a successful legacy
      match, so rows get upgraded automatically the next time someone
      logs in with them.
    """
    stored_value = str(stored_value)
    if stored_value.startswith(("$2b$", "$2a$", "$2y$")):
        try:
            return bcrypt.checkpw(plain_password.encode(), stored_value.encode())
        except ValueError:
            return False
    return plain_password.strip() == stored_value.strip()

def is_hashed(stored_value):
    return str(stored_value).startswith(("$2b$", "$2a$", "$2y$"))

def render_kv_table(pairs):
    """Render a list of (label, value) pairs as a bordered table with
    alternating faint-blue rows."""
    html = f'<table style="width:100%; border-collapse:collapse; border:1px solid {CARD_BORDER};">'
    for i, (label, value) in enumerate(pairs):
        bg = FAINT_BLUE if i % 2 == 0 else WHITE
        html += f'<tr style="background-color:{bg};">'
        html += f'<td style="padding:10px 12px; border:1px solid {CARD_BORDER}; color:{TEXT_DARK}; width:45%;"><strong>{label}</strong></td>'
        html += f'<td style="padding:10px 12px; border:1px solid {CARD_BORDER}; color:{TEXT_DARK};">{value}</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

# ============================================================
# LOGIN PAGE (admin/management only — no student portal)
# ============================================================
def login_page():
    st.markdown(f"""
    <div class="top-banner">
        <img src="{SCHOOL_LOGO_URL}" alt="School Logo">
        <h1>{SCHOOL_NAME} Portal</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Admin Login")
            admin_username = st.text_input("Admin Username", key="admin_user", value="admin")
            admin_pass = st.text_input("Admin Password", type="password", key="admin_pass")

            if st.button("Login", key="admin_login_btn", use_container_width=True):
                df_admins = load_data("Admin Logins")

                if df_admins.empty:
                    # First-ever admin login: seed the sheet with a hashed
                    # account instead of leaving the password hardcoded in
                    # source. Uses the same bootstrap password as before,
                    # once, to avoid locking anyone out on rollout.
                    if admin_username.strip() == "admin" and admin_pass == "admin2026":
                        write_data("Admin Logins", {
                            "Username": "admin",
                            "Password": hash_password("admin2026"),
                        })
                        st.session_state.logged_in = True
                        st.session_state.username = "admin"
                        st.rerun()
                    else:
                        st.error("Invalid admin username or password.")
                else:
                    df_admins.columns = df_admins.columns.astype(str).str.strip()
                    admin_match = df_admins[df_admins["Username"].astype(str).str.strip() == admin_username.strip()]
                    if not admin_match.empty and verify_password(admin_pass, admin_match.iloc[0].get("Password", "")):
                        admin_row = admin_match.iloc[0]

                        # Upgrade a legacy plaintext admin row the same way
                        # student rows used to get upgraded.
                        if not is_hashed(admin_row.get("Password", "")):
                            row_idx = admin_match.index[0] + 2
                            pw_col_idx = df_admins.columns.get_loc("Password") + 1
                            update_cell("Admin Logins", row_idx, pw_col_idx, hash_password(admin_pass))

                        st.session_state.logged_in = True
                        st.session_state.username = admin_username.strip()
                        st.rerun()
                    else:
                        st.error("Invalid admin username or password.")


    st.markdown(f"""
    <div class="bottom-footer">
        &copy; {datetime.now().year} {SCHOOL_NAME}. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ADMIN DASHBOARD - HELPERS
# ============================================================
def safe_sum(df, column_name):
    if df.empty or column_name not in df.columns:
        return 0.0
    return pd.to_numeric(
        df[column_name].astype(str).str.replace(r'[$,]', '', regex=True),
        errors='coerce'
    ).sum()

# ============================================================
# ADMIN DASHBOARD - MAIN
# ============================================================
def admin_dashboard():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <img src="{SCHOOL_LOGO_URL}" style="width: 80px; border-radius: 8px; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0;">{SCHOOL_NAME}</h3>
            <p style="color: #E0D5D8; margin: 5px 0;">Admin Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        admin_pages = [
            "Overview",
            "Register Student",
            "All Students",
            "Record Fee Payment",
            "Fees Owing",
            "Record Expense",
            "Record Other Income",
            "Staff Register",
            "Fixed Assets Register",
            "Loans Register",
            "Creditors Register",
            "Equity Register",
            "Bank Statement",
            "Income Statement",
            "Balance Sheet",
            "Account Settings",
        ]
        
        for page in admin_pages:
            if st.button(page, key=f"admin_{page}", use_container_width=True):
                st.session_state.admin_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("Logout", key="admin_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    page = st.session_state.admin_page
    
    if page == "Overview":
        admin_overview()
    elif page == "Register Student":
        admin_register_student()
    elif page == "All Students":
        admin_all_students()
    elif page == "Record Fee Payment":
        admin_record_fee()
    elif page == "Fees Owing":
        admin_fees_owing()
    elif page == "Record Expense":
        admin_record_expense()
    elif page == "Record Other Income":
        admin_record_other_income()
    elif page == "Staff Register":
        admin_staff_register()
    elif page == "Fixed Assets Register":
        admin_fixed_assets_register()
    elif page == "Loans Register":
        admin_loans_register()
    elif page == "Creditors Register":
        admin_creditors_register()
    elif page == "Equity Register":
        admin_equity_register()
    elif page == "Bank Statement":
        admin_bank_statement_page()
    elif page == "Income Statement":
        admin_income_statement_page()
    elif page == "Balance Sheet":
        admin_balance_sheet_page()
    elif page == "Account Settings":
        admin_account_settings()

# ============================================================
# ADMIN OVERVIEW
# ============================================================
def admin_overview():
    st.markdown("## Admin Overview")

    years = get_financial_years()
    col_filter, col_space = st.columns([1, 3])
    with col_filter:
        selected_year = st.selectbox("Financial Year", years, key="overview_year_filter")

    df_students = load_data("Students")
    total_students = len(df_students) if not df_students.empty else 0

    stmt = compute_income_statement(selected_year)
    debtors = compute_total_debtors()
    deferred = compute_deferred_income()
    profit_color = GREEN if stmt["surplus_for_year"] >= 0 else RED

    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-card-header">Enrollment<span class="lifetime-badge">ALL TIME</span></div>
        <div class="dash-card-body">
            <div class="metric-grid metric-grid-3">
                <div class="metric-card"><div class="metric-value">{total_students}</div><div class="metric-label">Enrollment</div></div>
                <div class="metric-card"><div class="metric-value">${debtors:,.0f}</div><div class="metric-label">Fees Owing (Debtors)</div></div>
                <div class="metric-card"><div class="metric-value">${deferred:,.0f}</div><div class="metric-label">Prepaid Fees (Deferred Income)</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-card-header">Financials<span class="term-badge">{selected_year}</span></div>
        <div class="dash-card-body">
            <h4>Revenue</h4>
            <div class="metric-grid metric-grid-3">
                <div class="metric-card"><div class="metric-value">${stmt['fee_income']:,.0f}</div><div class="metric-label">Fee Income</div></div>
                <div class="metric-card"><div class="metric-value">${stmt['other_income']:,.0f}</div><div class="metric-label">Other Income</div></div>
                <div class="metric-card"><div class="metric-value" style="color:{PRIMARY};">${stmt['total_revenue']:,.0f}</div><div class="metric-label">Total Revenue</div></div>
            </div>
            <h4>Expenses</h4>
            <div class="metric-grid metric-grid-2">
                <div class="metric-card"><div class="metric-value">${stmt['staff_costs']:,.0f}</div><div class="metric-label">Staff Costs</div></div>
                <div class="metric-card"><div class="metric-value" style="color:{RED};">${stmt['total_opex']:,.0f}</div><div class="metric-label">Total Operating Expenses</div></div>
            </div>
            <h4>Surplus</h4>
            <div class="metric-grid metric-grid-3">
                <div class="metric-card"><div class="metric-value">${stmt['surplus_before_tax']:,.0f}</div><div class="metric-label">Surplus Before Tax</div></div>
                <div class="metric-card"><div class="metric-value" style="color:{RED};">${stmt['tax_expense']:,.0f}</div><div class="metric-label">Income Tax (25%)</div></div>
                <div class="metric-card" style="border:2px solid {profit_color};"><div class="metric-value" style="color:{profit_color};">${stmt['surplus_for_year']:,.0f}</div><div class="metric-label">Surplus for the Year</div></div>
            </div>
            <p style="font-size:13px; color:{SKY_BLUE}; margin-top:8px;">See the Income Statement page for the full breakdown by category, and the Balance Sheet for assets, liabilities and equity.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ADMIN DATA ENTRY PAGES
# ============================================================

def admin_register_student():
    st.markdown("## Register Student")
    st.caption("Students enrol on a year-by-year basis. Re-register the same student next year with a new Academic Year row if they continue.")

    with st.container(border=True):
        st.markdown("#### Student Information")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Full Name*")
            academic_year = st.number_input("Academic Year*", min_value=2020, max_value=2100, value=date.today().year, step=1)
        with col2:
            level = st.selectbox("Level*", LEVELS)
            default_fee = ANNUAL_FEE_BY_LEVEL.get(level, 0.0)
            annual_fee = st.number_input("Annual Fee ($)*", min_value=0.0, step=10.0, value=default_fee)

        if st.button("Register Student", use_container_width=True):
            if not student_name.strip():
                st.error("Please enter the student's name.")
            else:
                df_students_existing = load_data("Students")
                new_student_number = generate_student_number(df_students_existing)
                success = write_data("Students", {
                    "Student Number": new_student_number,
                    "Student Name": student_name.strip(),
                    "Academic Year": academic_year,
                    "Level": level,
                    "Annual Fee": annual_fee,
                })
                if success:
                    st.success(f"{student_name} registered for {academic_year} ({level}) — Student Number {new_student_number}.")
                    st.balloons()
                else:
                    st.error("There was an error saving to the database.")


def admin_fees_owing():
    st.markdown("## Fees Owing (Debtors)")
    st.caption("Annual Fee (from the Students tab, per student per academic year) minus what they've paid toward that same Academic Year.")

    df_students = load_data("Students")
    if df_students.empty or "Student Number" not in df_students.columns:
        st.info("No students registered yet.")
        return
    df_students.columns = df_students.columns.astype(str).str.strip()

    df_payments = load_data("Fee Payments")
    if not df_payments.empty:
        df_payments.columns = df_payments.columns.astype(str).str.strip()

    rows = []
    today_year = date.today().year
    for _, srow in df_students.iterrows():
        sid = str(srow.get("Student Number", "")).strip()
        name = str(srow.get("Student Name", "")).strip()
        try:
            acad_year = int(srow.get("Academic Year", 0))
        except (ValueError, TypeError):
            continue
        if acad_year <= 0 or acad_year > today_year:
            continue  # a future enrolment isn't owed yet — matches compute_total_debtors()
        expected = pd.to_numeric(srow.get("Annual Fee", 0), errors="coerce") or 0.0
        paid = 0.0
        if not df_payments.empty and "Student Number" in df_payments.columns and "Academic Year" in df_payments.columns:
            match = df_payments[
                (df_payments["Student Number"].astype(str).str.strip() == sid) &
                (df_payments["Academic Year"].astype(str).str.strip() == str(acad_year))
            ]
            paid = safe_sum(match, "Amount Paid")
        owing = round(expected - paid, 2)
        rows.append({
            "Student Number": sid, "Student Name": name, "Academic Year": acad_year,
            "Expected": expected, "Paid": paid, "Owing": owing,
        })

    if not rows:
        st.info("No billable enrolments found.")
        return

    df_report = pd.DataFrame(rows).sort_values("Owing", ascending=False)
    total_expected = df_report["Expected"].sum()
    total_paid = df_report["Paid"].sum()
    total_owing = df_report["Owing"].clip(lower=0).sum()

    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-card-header">Summary</div>
        <div class="dash-card-body">
            <div class="metric-grid metric-grid-3">
                <div class="metric-card"><div class="metric-value">${total_expected:,.0f}</div><div class="metric-label">Expected</div></div>
                <div class="metric-card"><div class="metric-value" style="color:{GREEN};">${total_paid:,.0f}</div><div class="metric-label">Paid</div></div>
                <div class="metric-card" style="border:2px solid {RED if total_owing > 0 else GREEN};"><div class="metric-value" style="color:{RED if total_owing > 0 else GREEN};">${total_owing:,.0f}</div><div class="metric-label">Total Owing</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Per-Student Breakdown</div><div class="dash-card-body">', unsafe_allow_html=True)
    html = '<table style="width:100%; border-collapse:collapse; font-size:14px;">'
    html += f'<tr style="background-color:{PRIMARY}; color:{WHITE};">'
    for col in ["Student Number", "Student Name", "Academic Year", "Expected", "Paid", "Owing"]:
        html += f'<th style="padding:10px 12px; text-align:left;">{col}</th>'
    html += '</tr>'
    for i, (_, row) in enumerate(df_report.iterrows()):
        bg = FAINT_BLUE if i % 2 == 0 else WHITE
        owing_color = RED if row["Owing"] > 0 else GREEN
        html += '<tr>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{TEXT_DARK};">{row["Student Number"]}</td>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{TEXT_DARK};">{row["Student Name"]}</td>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{TEXT_DARK};">{row["Academic Year"]}</td>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{TEXT_DARK};">${row["Expected"]:,.2f}</td>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{TEXT_DARK};">${row["Paid"]:,.2f}</td>'
        html += f'<td style="padding:10px 12px; background-color:{bg}; color:{owing_color}; font-weight:bold;">${row["Owing"]:,.2f}</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)


def admin_record_fee():
    st.markdown("## Record Fee Payment")
    st.caption("Academic Year is which year's fees this payment is FOR — set it ahead to record a prepayment (Deferred Income) for a future year.")

    with st.container(border=True):
        st.markdown("#### Payment Details")

        df_students = load_data("Students")
        if not df_students.empty:
            df_students.columns = df_students.columns.astype(str).str.strip()
        student_display_list, student_label_to_id = build_student_dropdown(df_students)

        col1, col2 = st.columns(2)
        with col1:
            selected_label = st.selectbox("Student Name*", student_display_list)
            payment_date = st.date_input("Payment Date", value=date.today())
        with col2:
            academic_year = st.number_input("Academic Year (fees this payment is FOR)*", min_value=2020, max_value=2100, value=date.today().year, step=1)
            amount = st.number_input("Amount Paid*", min_value=0.0, step=10.0, format="%.2f")
            payment_method = st.selectbox("Payment Method", ["Cash", "EFT", "Mobile Money", "Cheque", "Other"])

        if academic_year > date.today().year:
            st.info(f"This will be recorded as a prepayment for {academic_year} — it adds to Cash now but shows as Deferred Income (a liability) on the Balance Sheet until {academic_year} arrives.")

        if st.button("Record Payment", use_container_width=True):
            if selected_label == "Select student...":
                st.error("Please select a student.")
            elif amount <= 0:
                st.error("Please enter an amount.")
            else:
                student_number = student_label_to_id.get(selected_label, "")
                student_name = selected_label.split(" (")[0]
                success = write_data("Fee Payments", {
                    "Student Number": student_number,
                    "Student Name": student_name,
                    "Academic Year": academic_year,
                    "Date": str(payment_date),
                    "Amount Paid": float(amount),
                    "Payment Method": payment_method,
                })
                if success:
                    st.success(f"Payment of ${amount:,.2f} recorded for {student_name} ({academic_year}).")
                    st.rerun()  # clears the form fields, so an accidental second click can't resubmit the same payment
                else:
                    st.error("Failed to record payment.")


def admin_record_expense():
    st.markdown("## Record Expense")
    
    with st.container(border=True):
        st.markdown("#### Expense Details")
    
        col1, col2 = st.columns(2)
    
        with col1:
            expense_date = st.date_input("Date", value=date.today(), key="exp_date")
            category = st.selectbox("Category", list(EXPENSE_LINE_LABELS.keys()))
    
        with col2:
            description = st.text_area("Expense Description")
            amount = st.number_input("Amount*", min_value=0.0, step=10.0, key="exp_amount")
    
        if st.button("Record Expense", use_container_width=True):
            if amount <= 0:
                st.error("Please enter an amount.")
            else:
                # Headers expected in the "Expenses" tab:
                # Timestamp | Date | Description | Amount | Category
                # (Financial year is derived from Date — no Month field needed.)
                success = write_data("Expenses", {
                    "Timestamp": str(datetime.now()),
                    "Date": str(expense_date),
                    "Description": description,
                    "Amount": amount,
                    "Category": category,
                })
                if success:
                    st.success(f"Expense of ${amount:,.2f} recorded!")
                else:
                    st.error("Failed to record expense.")
    

def admin_record_other_income():
    st.markdown("## Record Other Income")
    
    with st.container(border=True):
        st.markdown("#### Income Details")
    
        col1, col2 = st.columns(2)
    
        with col1:
            income_date = st.date_input("Date", value=date.today(), key="inc_date")
    
        with col2:
            description = st.text_area("Income Description", key="inc_desc")
            amount = st.number_input("Amount*", min_value=0.0, step=10.0, key="inc_amount")
    
        if st.button("Record Income", use_container_width=True):
            if amount <= 0:
                st.error("Please enter an amount.")
            else:
                success = write_data("Other Income", {
                    "Timestamp": str(datetime.now()),
                    "Date": str(income_date),
                    "Income Description": description,
                    "Amount": amount,
                })
                if success:
                    st.success(f"Income of ${amount:,.2f} recorded!")
                else:
                    st.error("Failed to record income.")
    

def admin_all_students():
    st.markdown("## All Students")
    
    df_students = load_data("Students")
    if not df_students.empty:
        df_students.columns = df_students.columns.astype(str).str.strip()
        
        search = st.text_input("Search by name...")
        display_df = df_students
        if search:
            display_df = df_students[df_students["Student Name"].astype(str).str.contains(search, case=False)]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown(f"**Total:** {len(display_df)} student(s)")

        with st.container(border=True):
            st.markdown("#### Remove a Student")
            st.caption(
                "Removes this registration row only — any Fee Payments already recorded "
                "against them are left untouched, so past financial statements don't change. "
                "This can't be undone from within the app."
            )

            options = ["Select student..."]
            row_lookup = {}
            for idx, row in df_students.iterrows():
                sid = str(row.get("Student Number", "")).strip()
                name = str(row.get("Student Name", "")).strip()
                year = row.get("Academic Year", "")
                label = f"{name} — {year} ({sid})"
                options.append(label)
                row_lookup[label] = idx

            selected = st.selectbox("Student to remove", options, key="remove_student_select")

            if selected != "Select student...":
                confirm = st.checkbox(f"I'm sure I want to permanently remove '{selected}'", key="remove_student_confirm")
                if st.button("Remove Student", use_container_width=True, key="remove_student_btn"):
                    if not confirm:
                        st.error("Please tick the confirmation box first.")
                    else:
                        remaining = df_students.drop(index=row_lookup[selected]).reset_index(drop=True)
                        success = overwrite_sheet("Students", remaining)
                        if success:
                            st.success(f"'{selected}' removed.")
                            st.rerun()
                        else:
                            st.error("Failed to remove student.")
    else:
        st.info("No students registered yet.")

def admin_account_settings():
    st.markdown("## Account Settings")
    
    with st.container(border=True):
        st.markdown("#### Change Your Password")
        st.markdown(f"**Logged in as:** {st.session_state.username}")
    
        current_password = st.text_input("Current Password", type="password", key="admin_current_pw")
        new_password = st.text_input("New Password", type="password", key="admin_new_pw")
        confirm_password = st.text_input("Confirm New Password", type="password", key="admin_confirm_pw")
    
        if st.button("Update Password", use_container_width=True, key="admin_update_pw_btn"):
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all three fields.")
            elif new_password != confirm_password:
                st.error("New password and confirmation don't match.")
            elif len(new_password) < 6:
                st.error("New password should be at least 6 characters.")
            else:
                df_admins = load_data("Admin Logins")
                if df_admins.empty:
                    st.error("Unable to load admin login data.")
                else:
                    df_admins.columns = df_admins.columns.astype(str).str.strip()
                    my_row = df_admins[df_admins["Username"].astype(str).str.strip() == st.session_state.username.strip()]
                    if my_row.empty:
                        st.error("Could not find your admin login record.")
                    elif not verify_password(current_password, my_row.iloc[0].get("Password", "")):
                        st.error("Current password is incorrect.")
                    else:
                        row_idx = my_row.index[0] + 2
                        pw_col_idx = df_admins.columns.get_loc("Password") + 1
                        success = update_cell("Admin Logins", row_idx, pw_col_idx, hash_password(new_password))
                        if success:
                            st.success("Password updated. Use your new password next time you log in.")
                        else:
                            st.error("Failed to update password.")
    
    
    with st.container(border=True):
        st.markdown("#### Add Another Admin Account")
    
        new_admin_username = st.text_input("New Admin Username", key="new_admin_user")
        new_admin_password = st.text_input("New Admin Password", type="password", key="new_admin_pw")
    
        if st.button("Create Admin Account", use_container_width=True, key="create_admin_btn"):
            if not new_admin_username.strip() or not new_admin_password:
                st.error("Please fill in both fields.")
            elif len(new_admin_password) < 6:
                st.error("Password should be at least 6 characters.")
            else:
                df_admins = load_data("Admin Logins")
                taken = False
                if not df_admins.empty and "Username" in df_admins.columns:
                    df_admins.columns = df_admins.columns.astype(str).str.strip()
                    taken = not df_admins[df_admins["Username"].astype(str).str.strip().str.lower() == new_admin_username.strip().lower()].empty
            
                if taken:
                    st.error(f"Username '{new_admin_username.strip()}' is already taken.")
                else:
                    success = write_data("Admin Logins", {
                        "Username": new_admin_username.strip(),
                        "Password": hash_password(new_admin_password),
                    })
                    if success:
                        st.success(f"Admin account '{new_admin_username.strip()}' created.")
                    else:
                        st.error("Failed to create admin account.")
    

def admin_staff_register():
    st.markdown("## Staff Register")
    st.caption("Enter headcount and monthly salary per staff category, for one financial year at a time. Monthly and annual costs are calculated automatically.")

    with st.container(border=True):
        st.markdown("#### Set Staffing for a Year")

        years = list(range(date.today().year - 1, date.today().year + 3))
        selected_year = st.selectbox("Financial Year", years, index=years.index(date.today().year))

        _, existing = compute_staff_costs_for_year(selected_year)
        existing_map = {}
        if not existing.empty:
            for _, row in existing.iterrows():
                existing_map[row["Category"]] = row

        entries = {}
        for cat in STAFF_CATEGORIES:
            col1, col2 = st.columns(2)
            default_n = int(existing_map[cat]["Number of Staff"]) if cat in existing_map else 0
            default_s = float(existing_map[cat]["Monthly Salary per Staff"]) if cat in existing_map else 0.0
            with col1:
                n = st.number_input(f"{cat} — Number of Staff", min_value=0, step=1, value=default_n, key=f"staff_n_{cat}")
            with col2:
                s = st.number_input(f"{cat} — Monthly Salary per Staff ($)", min_value=0.0, step=10.0, value=default_s, key=f"staff_s_{cat}")
            entries[cat] = (n, s)

        if st.button(f"Save Staff Register for {selected_year}", use_container_width=True):
            ok = True
            for cat, (n, s) in entries.items():
                success = write_data("Staff Register", {
                    "Financial Year": selected_year,
                    "Category": cat,
                    "Number of Staff": n,
                    "Monthly Salary per Staff": s,
                })
                ok = ok and success
            if ok:
                st.success(f"Staff Register saved for {selected_year}.")
            else:
                st.error("Some rows failed to save — check the 'Staff Register' tab exists with the right headers.")


    annual_total, breakdown = compute_staff_costs_for_year(selected_year)
    if not breakdown.empty:
        with st.container(border=True):
            st.markdown("#### Current Staff Costs Summary")
            st.dataframe(breakdown, use_container_width=True, hide_index=True)
            st.markdown(f"**Total annual staff costs for {selected_year}:** ${annual_total:,.2f}")


def admin_fixed_assets_register():
    st.markdown("## Fixed Assets Register")
    st.caption("Each row is one asset. Depreciation is straight-line based on the rate you enter.")

    with st.container(border=True):
        st.markdown("#### Add an Asset")
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", ASSET_CATEGORIES)
            description = st.text_input("Description", key="asset_desc")
            date_acquired = st.date_input("Date Acquired", value=date.today(), key="asset_date")
        with col2:
            cost = st.number_input("Cost ($)*", min_value=0.0, step=50.0, key="asset_cost")
            dep_rate = st.number_input("Depreciation Rate (% per year)*", min_value=0.0, max_value=100.0, step=1.0, key="asset_rate")

        if st.button("Add Asset", use_container_width=True):
            if cost <= 0:
                st.error("Please enter a cost.")
            else:
                success = write_data("Fixed Assets", {
                    "Category": category,
                    "Description": description,
                    "Cost": cost,
                    "Date Acquired": str(date_acquired),
                    "Depreciation Rate (%)": dep_rate,
                })
                if success:
                    st.success(f"{category} asset added.")
                else:
                    st.error("Failed to add asset — check the 'Fixed Assets' tab exists with the right headers.")

    df_assets, total_dep, total_nbv = compute_fixed_assets()
    if not df_assets.empty:
        with st.container(border=True):
            st.markdown("#### Asset Register")
            st.dataframe(df_assets, use_container_width=True, hide_index=True)
            st.markdown(f"**Total annual depreciation:** ${total_dep:,.2f} &nbsp;&nbsp; **Total net book value:** ${total_nbv:,.2f}")
    else:
        st.info("No fixed assets recorded yet.")


def admin_loans_register():
    st.markdown("## Loans Register")
    st.caption("Each row is one loan. To record a repayment or write-off, edit the 'Loans' tab in Google Sheets directly.")

    with st.container(border=True):
        st.markdown("#### Add a Loan")
        col1, col2 = st.columns(2)
        with col1:
            loan_type = st.selectbox("Loan Type", LOAN_TYPES)
            lender = st.text_input("Lender", key="loan_lender")
            start_date = st.date_input("Start Date", value=date.today(), key="loan_start")
        with col2:
            principal = st.number_input("Principal Amount ($)*", min_value=0.0, step=100.0, key="loan_principal")
            rate = st.number_input("Interest Rate (% per year)*", min_value=0.0, max_value=100.0, step=0.5, key="loan_rate")

        if st.button("Add Loan", use_container_width=True):
            if principal <= 0:
                st.error("Please enter a principal amount.")
            else:
                success = write_data("Loans", {
                    "Loan Type": loan_type,
                    "Lender": lender,
                    "Principal Amount": principal,
                    "Interest Rate (%)": rate,
                    "Start Date": str(start_date),
                })
                if success:
                    st.success(f"{loan_type} loan added.")
                else:
                    st.error("Failed to add loan — check the 'Loans' tab exists with the right headers.")

    df_loans, long_term, short_term, interest = compute_loans()
    if not df_loans.empty:
        with st.container(border=True):
            st.markdown("#### Loan Register")
            st.dataframe(df_loans, use_container_width=True, hide_index=True)
            st.markdown(f"**Long-term loans:** ${long_term:,.2f} &nbsp;&nbsp; **Short-term loans:** ${short_term:,.2f} &nbsp;&nbsp; **Annual finance costs:** ${interest:,.2f}")
    else:
        st.info("No loans recorded yet.")


def admin_creditors_register():
    st.markdown("## Creditors Register")
    st.caption("Amounts currently owed to suppliers. Remove a line by editing the 'Creditors' tab once it's paid.")

    with st.container(border=True):
        st.markdown("#### Add a Creditor")
        description = st.text_input("Description", key="cred_desc")
        amount = st.number_input("Amount Owed ($)*", min_value=0.0, step=10.0, key="cred_amount")
        cred_date = st.date_input("Date", value=date.today(), key="cred_date")

        if st.button("Add Creditor", use_container_width=True):
            if amount <= 0:
                st.error("Please enter an amount.")
            else:
                success = write_data("Creditors", {
                    "Description": description, "Amount": amount, "Date": str(cred_date),
                })
                if success:
                    st.success("Creditor added.")
                else:
                    st.error("Failed to add creditor — check the 'Creditors' tab exists with the right headers.")

    df_creditors = load_data("Creditors")
    if not df_creditors.empty:
        with st.container(border=True):
            st.markdown("#### Outstanding Creditors")
            st.dataframe(df_creditors, use_container_width=True, hide_index=True)
            st.markdown(f"**Total creditors:** ${safe_sum(df_creditors, 'Amount'):,.2f}")


def admin_equity_register():
    st.markdown("## Equity Register")
    st.caption("Share capital, share premium and revaluation reserve movements. Retained earnings is calculated automatically on the Balance Sheet.")

    with st.container(border=True):
        st.markdown("#### Add an Equity Movement")
        item = st.selectbox("Item", EQUITY_ITEMS)
        amount = st.number_input("Amount ($)*", step=10.0, key="equity_amount")
        eq_date = st.date_input("Date", value=date.today(), key="equity_date")

        if st.button("Add Equity Entry", use_container_width=True):
            success = write_data("Equity", {"Item": item, "Amount": amount, "Date": str(eq_date)})
            if success:
                st.success(f"{item} entry added.")
            else:
                st.error("Failed to add entry — check the 'Equity' tab exists with the right headers.")

    df_equity = load_data("Equity")
    if not df_equity.empty:
        with st.container(border=True):
            st.markdown("#### Equity Entries")
            st.dataframe(df_equity, use_container_width=True, hide_index=True)


def admin_bank_statement_page():
    st.markdown("## Bank Statement")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        filter_from = st.date_input("From", value=None, key="stmt_from")
    with col2:
        filter_to = st.date_input("To", value=None, key="stmt_to")

    df_stmt, opening_amount, opening_date = compute_bank_statement(
        start_date=filter_from if filter_from else None,
        end_date=filter_to if filter_to else None,
    )

    closing_balance = df_stmt["Balance"].iloc[-1] if not df_stmt.empty else opening_amount
    statement_start = filter_from or opening_date or date.today()

    st.markdown(f"""
    <div style="border:1px solid {CARD_BORDER}; border-radius:10px; padding:24px 28px; margin-bottom:20px; background:{WHITE};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
            <div>
                <div style="font-size:22px; font-weight:700; color:{TEXT_DARK};">STATEMENT OF ACCOUNT</div>
                <div style="font-size:13px; color:{SKY_BLUE}; margin-top:4px;">{BANK_NAME}</div>
            </div>
            <div style="text-align:right; font-size:13px; color:{TEXT_DARK};">
                <div><strong>STATEMENT DATE</strong> &nbsp; {date.today().strftime('%B %d, %Y')}</div>
                <div><strong>ACCOUNT NO</strong> &nbsp; {BANK_ACCOUNT_NUMBER}</div>
                <div><strong>ACCOUNT TYPE</strong> &nbsp; {BANK_ACCOUNT_TYPE}</div>
            </div>
        </div>
        <hr style="border-color:{CARD_BORDER}; margin:16px 0;">
        <div style="font-size:14px; color:{TEXT_DARK};">
            <strong>{SCHOOL_NAME}</strong><br>
            Statement period from {statement_start.strftime('%d %B %Y') if hasattr(statement_start, 'strftime') else statement_start}
            &nbsp;|&nbsp; Opening balance: ${opening_amount:,.2f}
            &nbsp;|&nbsp; Closing balance: ${closing_balance:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_stmt.empty:
        st.info("No transactions in this period yet.")
        return

    html = '<table style="width:100%; border-collapse:collapse; font-size:13px;">'
    html += f'<tr style="background-color:{PRIMARY}; color:{WHITE};">'
    for col in ["Date", "Narration", "Ref No.", "Debit", "Credit", "Balance"]:
        html += f'<th style="padding:10px 12px; text-align:left;">{col.upper()}</th>'
    html += '</tr>'
    for i, (_, row) in enumerate(df_stmt.iterrows()):
        bg = FAINT_BLUE if i % 2 == 0 else WHITE
        debit_str = f"{row['Debit']:,.2f}" if row["Debit"] else ""
        credit_str = f"{row['Credit']:,.2f}" if row["Credit"] else ""
        html += f'<tr style="background-color:{bg};">'
        html += f'<td style="padding:8px 12px; color:{TEXT_DARK};">{row["Date"]}</td>'
        html += f'<td style="padding:8px 12px; color:{TEXT_DARK};">{row["Narration"]}</td>'
        html += f'<td style="padding:8px 12px; color:{TEXT_DARK};">{row["Ref No."]}</td>'
        html += f'<td style="padding:8px 12px; color:{RED};">{debit_str}</td>'
        html += f'<td style="padding:8px 12px; color:{GREEN};">{credit_str}</td>'
        html += f'<td style="padding:8px 12px; color:{TEXT_DARK}; font-weight:bold;">{row["Balance"]:,.2f}</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "Download as Excel",
            data=bank_statement_to_excel(df_stmt, opening_amount, closing_balance, statement_start),
            file_name=f"{SCHOOL_NAME.replace(' ', '_')}_Bank_Statement_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            "Download as PDF",
            data=bank_statement_to_pdf(df_stmt, opening_amount, closing_balance, statement_start),
            file_name=f"{SCHOOL_NAME.replace(' ', '_')}_Bank_Statement_{date.today().isoformat()}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


def admin_income_statement_page():
    st.markdown("## Statement of Comprehensive Income (SOCI)")

    years = get_financial_years()
    selected_year = st.selectbox("Financial Year", years, key="is_year")
    st.caption(f"For the year ended 31 December {selected_year}")
    stmt = compute_income_statement(selected_year)

    revenue_lines = [
        ("Fee income", f"${stmt['fee_income']:,.2f}"),
        ("Other income", f"${stmt['other_income']:,.2f}"),
        ("Total revenue", f"${stmt['total_revenue']:,.2f}"),
    ]

    expense_lines = [("Staff costs", f"(${stmt['staff_costs']:,.2f})")]
    for cat, label in EXPENSE_LINE_LABELS.items():
        expense_lines.append((label, f"(${stmt['expense_lines'][cat]:,.2f})"))
    expense_lines += [
        ("Depreciation", f"(${stmt['depreciation']:,.2f})"),
        ("Total operating expenses", f"(${stmt['total_opex']:,.2f})"),
    ]

    result_lines = [
        ("Operating surplus/(deficit)", f"${stmt['operating_surplus']:,.2f}"),
        ("Finance costs", f"(${stmt['finance_costs']:,.2f})"),
        ("Surplus/(deficit) before tax", f"${stmt['surplus_before_tax']:,.2f}"),
        (f"Income tax expense ({CORPORATE_TAX_RATE*100:.0f}%)", f"(${stmt['tax_expense']:,.2f})"),
        ("SURPLUS/(DEFICIT) FOR THE YEAR", f"${stmt['surplus_for_year']:,.2f}"),
    ]

    st.markdown('<div class="dash-card"><div class="dash-card-header">Revenue</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(revenue_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Operating Expenses</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(expense_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Result for the Year</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(result_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    all_lines = revenue_lines + expense_lines + result_lines
    export_rows = [{"Line Item": l, "Amount": v} for l, v in all_lines]
    df_export = pd.DataFrame(export_rows)
    st.download_button(
        "Download as Excel",
        data=df_to_excel_download(df_export, "SOCI"),
        file_name=f"{SCHOOL_NAME.replace(' ', '_')}_SOCI_{selected_year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


def admin_balance_sheet_page():
    st.markdown("## Statement of Financial Position")
    st.caption(f"As at {date.today().strftime('%d %B %Y')}")

    bs = compute_balance_sheet()

    non_current_asset_lines = [(cat, f"${bs['nbv_by_category'][cat]:,.2f}") for cat in ASSET_CATEGORIES]
    non_current_asset_lines.append(("Total non-current assets", f"${bs['total_non_current_assets']:,.2f}"))

    current_asset_lines = [
        ("Debtors (fees receivable)", f"${bs['debtors']:,.2f}"),
        ("Cash and cash equivalents", f"${bs['cash']:,.2f}"),
        ("Total current assets", f"${bs['total_current_assets']:,.2f}"),
    ]

    equity_lines = [
        ("Ordinary share capital", f"${bs['share_capital']:,.2f}"),
        ("Share premium", f"${bs['share_premium']:,.2f}"),
        ("Revaluation reserve", f"${bs['revaluation_reserve']:,.2f}"),
        ("Retained earnings", f"${bs['retained_earnings']:,.2f}"),
        ("Total equity", f"${bs['total_equity']:,.2f}"),
    ]

    non_current_liability_lines = [
        ("Long-term loans", f"${bs['long_term_loans']:,.2f}"),
    ]

    current_liability_lines = [
        ("Short-term loans", f"${bs['short_term_loans']:,.2f}"),
        ("Tax liabilities", f"${bs['current_year_tax']:,.2f}"),
        ("Creditors", f"${bs['creditors_total']:,.2f}"),
        ("Deferred income (prepaid fees)", f"${bs['deferred_income']:,.2f}"),
        ("Total current liabilities", f"${bs['total_current_liabilities']:,.2f}"),
    ]

    st.markdown("### ASSETS")
    st.markdown('<div class="dash-card"><div class="dash-card-header">Non-Current Assets</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(non_current_asset_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Current Assets</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(current_asset_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(f"<p style='font-size:16px;'><strong>TOTAL ASSETS: ${bs['total_assets']:,.2f}</strong></p>", unsafe_allow_html=True)

    st.markdown("### EQUITY AND LIABILITIES")
    st.markdown('<div class="dash-card"><div class="dash-card-header">Equity</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(equity_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Non-Current Liabilities</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(non_current_liability_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dash-card"><div class="dash-card-header">Current Liabilities</div><div class="dash-card-body">', unsafe_allow_html=True)
    render_kv_table(current_liability_lines)
    st.markdown('</div></div>', unsafe_allow_html=True)

    total_equity_and_liabilities = bs["total_equity"] + bs["total_liabilities"]
    st.markdown(f"<p style='font-size:16px;'><strong>TOTAL EQUITY AND LIABILITIES: ${total_equity_and_liabilities:,.2f}</strong></p>", unsafe_allow_html=True)

    check_color = GREEN if abs(bs["total_assets"] - total_equity_and_liabilities) < 0.01 else RED
    st.markdown(f"<p style='color:{check_color};'><strong>Balance check:</strong> Total Assets (${bs['total_assets']:,.2f}) = Total Equity and Liabilities (${total_equity_and_liabilities:,.2f})</p>", unsafe_allow_html=True)

    export_rows = (
        [{"Section": "Non-Current Assets", "Line Item": l, "Amount": v} for l, v in non_current_asset_lines] +
        [{"Section": "Current Assets", "Line Item": l, "Amount": v} for l, v in current_asset_lines] +
        [{"Section": "TOTAL ASSETS", "Line Item": "", "Amount": f"${bs['total_assets']:,.2f}"}] +
        [{"Section": "Equity", "Line Item": l, "Amount": v} for l, v in equity_lines] +
        [{"Section": "Non-Current Liabilities", "Line Item": l, "Amount": v} for l, v in non_current_liability_lines] +
        [{"Section": "Current Liabilities", "Line Item": l, "Amount": v} for l, v in current_liability_lines] +
        [{"Section": "TOTAL EQUITY AND LIABILITIES", "Line Item": "", "Amount": f"${total_equity_and_liabilities:,.2f}"}]
    )
    df_export = pd.DataFrame(export_rows)
    st.download_button(
        "Download as Excel",
        data=df_to_excel_download(df_export, "Balance Sheet"),
        file_name=f"{SCHOOL_NAME.replace(' ', '_')}_Balance_Sheet_{date.today().isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


# ============================================================
# MAIN APP
# ============================================================
def main():
    inject_css()
    init_session()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()
