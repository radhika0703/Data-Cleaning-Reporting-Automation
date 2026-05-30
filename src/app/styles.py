def inject_premium_styles():
    """
    Returns custom CSS block to override defaults and give a stunning,
    premium, modern visual interface to the Streamlit app.
    Includes custom fonts, glassmorphism containers, linear gradients,
    pulsing animations, and tailored metric card overlays.
    """
    import streamlit as st
    
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* General body & typography setup */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Elegant gradient title header */
    .title-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F766E 50%, #0D9488 100%);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(15, 118, 110, 0.2);
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .title-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 80%);
        pointer-events: none;
    }
    .title-banner h1 {
        font-size: 2.8rem;
        margin: 0;
        font-weight: 800;
        text-shadow: 0 4px 12px rgba(0,0,0,0.25);
        color: #ffffff !important;
    }
    .title-banner p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: #CCFBF1;
        font-weight: 400;
    }
    
    /* Premium Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(15, 118, 110, 0.08);
        border-color: rgba(15, 118, 110, 0.3);
    }
    
    /* Styled Metric Grid */
    .custom-metric {
        background: white;
        border-radius: 12px;
        border-left: 6px solid #0F766E;
        padding: 1rem 1.25rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    .custom-metric:hover {
        border-left-color: #1E1B4B;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }
    .custom-metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E1B4B;
        line-height: 1.2;
    }
    .custom-metric-lbl {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Primary buttons glowing effects */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(15, 118, 110, 0.3) !important;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 20px rgba(15, 118, 110, 0.45) !important;
        background: linear-gradient(135deg, #1E1B4B 0%, #0F766E 100%) !important;
    }
    div.stButton > button:first-child:active {
        transform: scale(0.98) !important;
    }
    
    /* Styled uploader area */
    section[data-testid="stFileUploader"] {
        border: 2px dashed #0F766E !important;
        background-color: #F8FAFC !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Status indicators */
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 10rem;
    }
    .badge-success {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
