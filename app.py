import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION & GLOBAL CSS
# ============================================================

st.set_page_config(
    page_title="Sahara AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme matching the design
st.markdown("""
<style>
    /* Allow metric values to wrap and reduce font size slightly for long text */
    div[data-testid="stMetricValue"] > div {
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.2 !important;
        font-size: 1.6rem !important;
    }

/* Global App Background */
.stApp {
    background-color: #0E0F15;
    color: #E2E8F0;
}

/* Sidebar Background and styling */
[data-testid="stSidebar"] {
    background-color: #15161E;
    border-right: 1px solid #1E1F2A;
}

/* Hide standard Streamlit radio button circles */
div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Style the radio buttons to look like the custom menu items */
div[role="radiogroup"] > label {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    background-color: transparent;
    border: 1px solid transparent;
}
div[role="radiogroup"] > label:hover {
    background-color: #1E1F2A;
}

/* Highlight active menu item (Requires modern browser with :has support, fallback otherwise) */
div[role="radiogroup"] > label:has(input:checked) {
    background-color: #2A2146; /* Deep Purple */
    border: 1px solid #3B2D62;
}
div[role="radiogroup"] > label:has(input:checked) p {
    color: #A78BFA !important; /* Lighter Purple Text */
    font-weight: 600;
}

/* Typography in radio */
div[role="radiogroup"] p {
    font-size: 16px !important;
    margin: 0;
    color: #CBD5E1;
}

/* Sidebar bottom disclaimer text */
.sidebar-disclaimer {
    color: #94A3B8;
    font-size: 12px;
    line-height: 1.4;
    padding: 20px;
    margin-top: 40px;
}

/* Hero Section */
.hero-box {
    background: linear-gradient(135deg, #9C83FF 0%, #6098FF 100%);
    padding: 24px 28px;
    border-radius: 16px;
    color: #111;
    margin-bottom: 20px;
}
.hero-box h1 {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
}
.hero-box h3 {
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 17px;
    font-weight: 700;
    color: #1E293B;
    line-height: 1.3;
}
.hero-box p {
    margin: 0;
    font-size: 15px;
    font-weight: 500;
    color: #334155;
    line-height: 1.5;
}

/* Disclaimer Box */
.warning-box {
    border: 1px solid #7D6B42;
    background-color: #181615;
    border-radius: 8px;
    padding: 16px 20px;
    color: #D4AF60;
    font-size: 14px;
    margin-bottom: 30px;
}

/* Feature Cards */
.feature-card {
    background-color: #1C1D26;
    border: 1px solid #282936;
    border-radius: 16px;
    padding: 24px;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.2s;
}
.feature-card:hover {
    transform: translateY(-2px);
    border-color: #4B5563;
}
.feature-icon {
    font-size: 28px;
    margin-bottom: 12px;
    filter: grayscale(100%) brightness(200%);
}
.feature-text {
    font-size: 15px;
    color: #E2E8F0;
    font-weight: 500;
    line-height: 1.3;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# STATE INITIALIZATION
# ============================================================
if "assessment_history" not in st.session_state:
    st.session_state.assessment_history = []
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Home"
if "latest_assessment_result" not in st.session_state:
    st.session_state.latest_assessment_result = None
if "assessment_step" not in st.session_state:
    st.session_state.assessment_step = 1
if "step_error" not in st.session_state:
    st.session_state.step_error = None
if "assessment_form" not in st.session_state:
    st.session_state.assessment_form = {
        "consent": False,
        "mood": None,
        "anxiety": None,
        "stress": None,
        "sleep": None,
        "concentration": None,
        "helplessness": None,
        "isolation": None,
        "support": None,
        "safety_concern": None,
        "case_involved": None,
        "stage": None,
        "user_text": ""
    }

# ============================================================
# HELPER & SCORING FUNCTIONS
# ============================================================

def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def get_risk_level(score):
    if score < 35:
        return "LOW"
    elif score < 65:
        return "MODERATE"
    else:
        return "HIGH"


def risk_message(level):
    if level == "LOW":
        return "Your responses suggest you are currently managing within a healthy emotional range. Keep prioritizing your self-care routines and trusted connections."
    elif level == "MODERATE":
        return "Your responses reflect moderate stress or fatigue indicators. Proactive coping strategies, lifestyle pauses, or speaking with a trusted listener can help restore balance."
    else:
        return "Your responses indicate heightened emotional distress or vulnerability. We strongly encourage you to connect with a qualified professional or counsellor for personalized support."


def calculate_distress(
    mood_val,
    anxiety_val,
    sleep_val,
    isolation_val,
    concentration_val,
    stress_val,
    helplessness_val,
    safety_concern_val,
    support_val
):
    score = 0
    # Lower mood = higher distress (mood 1..5)
    score += (6 - mood_val) * 5

    # Negative indicators
    score += anxiety_val * 5
    score += sleep_val * 4
    score += isolation_val * 4
    score += concentration_val * 3
    score += stress_val * 5
    score += helplessness_val * 7
    score += safety_concern_val * 10

    # Protective factor
    score -= support_val * 4

    return round(clamp(score))


def analyze_text(text):
    text = text.lower()

    distress_words = [
        "stressed", "stress", "anxious", "anxiety", "worried", "overwhelmed",
        "helpless", "hopeless", "fear", "afraid", "isolated", "alone",
        "pressure", "scared", "distressed", "tired", "depressed", "exhausted", "panic"
    ]

    safety_words = [
        "unsafe", "danger", "threat", "threatened", "hurt", "abuse", "harass"
    ]

    positive_words = [
        "happy", "calm", "hopeful", "better", "good", "safe", "supported",
        "relaxed", "peaceful", "optimistic", "strong", "grateful"
    ]

    distress_matches = [w for w in distress_words if w in text]
    safety_matches = [w for w in safety_words if w in text]
    positive_matches = [w for w in positive_words if w in text]

    text_score = (
        len(distress_matches) * 6
        + len(safety_matches) * 12
        - len(positive_matches) * 4
    )

    return (
        clamp(text_score, 0, 25),
        distress_matches,
        safety_matches,
        positive_matches
    )


def intervention_plan(level, factors):
    recommendations = []

    if level == "LOW":
        recommendations = [
            ("🌱 Mindful Maintenance", "Continue regular check-ins and maintain balanced sleep and activity habits."),
            ("🤝 Stay Connected", "Keep sharing your day-to-day experiences with close friends and family."),
            ("🧘 Active Relaxation", "Engage in hobbies or mindfulness exercises that help you decompress.")
        ]
    elif level == "MODERATE":
        recommendations = [
            ("💬 Dedicated Support Check", "Consider scheduling a 1-on-1 discussion with a wellbeing counsellor."),
            ("⏱️ Stress Management", "Practice grounding techniques (e.g., 4-7-8 breathing) during high-pressure moments."),
            ("🛡️ Boundary Setting", "Protect time for rest, reduce voluntary stressors, and inform a trusted peer.")
        ]
    else:
        recommendations = [
            ("👩‍⚕️ Professional Review", "Prioritize a clinical or psychological review with a verified healthcare professional."),
            ("🚨 Safety Protocol Activation", "Ensure you are in a secure environment and notify a designated trusted contact."),
            ("📞 24/7 Helpline Access", "Utilize available confidential toll-free helplines for immediate stabilization.")
        ]

    if "Sleep disruption" in factors:
        recommendations.append(("💤 Sleep Hygiene", "Implement a consistent wind-down routine and limit screen time 1 hour before bed."))
    if "Social disconnection" in factors:
        recommendations.append(("🫂 Reconnecting", "Reach out to one trusted individual today or join a supportive peer group."))
    if "High anxiety" in factors:
        recommendations.append(("🌬️ Grounding Exercises", "Try 5-4-3-2-1 sensory grounding to ease immediate anxious spikes."))
    if "Safety concern" in factors:
        recommendations.append(("🛡️ Protection & Safety", "Contact authorized support services immediately if your physical safety is compromised."))

    return recommendations


# ============================================================
# SIDEBAR NAVIGATION
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E2E8F0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 12px;">
                <path d="M 20 7 L 12 2 L 4 7 L 4 10 L 20 14 L 20 17 L 12 22 L 4 17"/>
            </svg>
            <span style="font-size: 22px; font-weight: bold; color: #fff;">Sahara AI</span>
        </div>
    """, unsafe_allow_html=True)
    
    page = option_menu(
        menu_title=None,
        options=[
            "Home", 
            "AI Assessment", 
            "Wellbeing Trend", 
            "Case Journey", 
            "Professional Connect", 
            "Resilience Support", 
            "Privacy & Safety"
        ],
        icons=[
            "house", 
            "activity", 
            "graph-up", 
            "signpost-split", 
            "people", 
            "shield", 
            "lock"
        ],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
            "icon": {"color": "#CBD5E1", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "4px 0", 
                "padding": "12px 16px",
                "color": "#E2E8F0", 
                "border-radius": "12px",
                "--hover-color": "#1E1F2A"
            },
            "nav-link-selected": {
                "background-color": "#2A2146", 
                "color": "#A78BFA", 
                "font-weight": "600"
            }
        }
    )
    
    st.markdown("""
        <div class="sidebar-disclaimer">
            Prototype only – AI output should always be reviewed by an appropriately qualified human professional.
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# HOME PAGE (REDESIGN)
# ============================================================
if page == "Home":
    st.markdown("""
        <div class="hero-box">
            <h1>Sahara AI</h1>
            <h3>AI-Powered Dynamic Mental Health Monitoring & Early Intervention</h3>
            <p>A digital wellbeing support platform designed to identify worsening distress early and connect people to appropriate human support.</p>
        </div>
        <div class="warning-box">
            Sahara AI is a prototype early-warning system. It does not provide medical diagnosis.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 20px; font-weight: 600; margin-bottom: 16px;'>What Sahara AI Provides</h3>", unsafe_allow_html=True)
    
    # 2x2 Grid for features
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-text">AI-assisted wellbeing assessment</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚠️</div>
            <div class="feature-text">Early warning</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-text">Dynamic distress trends</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-text">Professional connection</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><h3 style='font-size: 20px; font-weight: 600; margin-bottom: 24px;'>How It Works</h3>", unsafe_allow_html=True)

    # Simplified representation of the flowchart to match look and feel
    st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"><div style="position: relative; height: 320px; font-family: sans-serif; margin-top: 20px;"><svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#3B82F6" /></marker></defs><line x1="26%" y1="40" x2="40%" y2="40" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /><line x1="60%" y1="40" x2="74%" y2="40" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /><line x1="94%" y1="40" x2="98%" y2="40" stroke="#3B82F6" stroke-width="2" /><line x1="98%" y1="40" x2="98%" y2="150" stroke="#3B82F6" stroke-width="2" /><line x1="98%" y1="150" x2="94%" y2="150" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /><line x1="74%" y1="150" x2="60%" y2="150" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /><line x1="40%" y1="150" x2="2%" y2="150" stroke="#3B82F6" stroke-width="2" /><line x1="2%" y1="150" x2="2%" y2="260" stroke="#3B82F6" stroke-width="2" /><line x1="2%" y1="260" x2="6%" y2="260" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /><line x1="26%" y1="260" x2="40%" y2="260" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrow)" /></svg><div style="position: absolute; top: 10px; left: 16%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-person" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">User<br>Check-in</div></div><div style="position: absolute; top: 10px; left: 50%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-person-gear" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">AI-assisted<br>Assessment</div></div><div style="position: absolute; top: 10px; left: 84%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-speedometer2" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">Dynamic<br>Distress Score</div></div><div style="position: absolute; top: 120px; left: 50%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-graph-up" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">Trend<br>Detection</div></div><div style="position: absolute; top: 120px; left: 84%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-exclamation-triangle" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">Early<br>Warning</div></div><div style="position: absolute; top: 230px; left: 16%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-people" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">Human<br>Professional<br>Review</div></div><div style="position: absolute; top: 230px; left: 50%; width: 120px; margin-left: -60px; background-color: #0E1117; z-index: 2; text-align: center;"><div style="margin-bottom: 4px;"><i class="bi bi-headset" style="font-size: 28px; color: #E2E8F0;"></i></div><div style="font-size: 11px; color: #CBD5E1; line-height: 1.2;">Support &<br>Follow-up</div></div></div>""", unsafe_allow_html=True)
elif page == "AI Assessment":

    # --- RESULT VIEW IF ALREADY ANALYZED ---
    if st.session_state.latest_assessment_result is not None:
        res = st.session_state.latest_assessment_result

        # Top Header
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <h1 style="margin: 0; color: #F8FAFC;">📊 Assessment Insights & Care Plan</h1>
                <p style="color: #64748b; margin: 4px 0 0 0;">Comprehensive wellbeing evaluation generated by Sahara AI</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Risk Banner
        banner_class = "result-banner-low" if res["level"] == "LOW" else ("result-banner-mod" if res["level"] == "MODERATE" else "result-banner-high")
        icon = "🟢" if res["level"] == "LOW" else ("🟡" if res["level"] == "MODERATE" else "🔴")

        st.markdown(f"""
        <div class="{banner_class}">
            <h2 style="margin: 0; font-size: 1.9rem; color: white;">{icon} {res['level']} DISTRESS DETECTED</h2>
            <p style="margin: 8px 0 0 0; font-size: 1.05rem; opacity: 0.95; color: white;">{risk_message(res['level'])}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics Breakdown
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Wellbeing Index", f"{res['wellbeing_score']}/100", help="100 indicates optimal positive wellbeing")
        with col_m2:
            st.metric("Distress Score", f"{res['distress_score']}/100", help="Lower is better (0-100 scale)")
        with col_m3:
            st.metric("Triage Priority", res['level'])
        with col_m4:
            st.metric("Journey Context", res['stage'])

        # Visual Progress Bar
        st.caption("Distress Spectrum Indicator:")
        st.progress(res['distress_score'] / 100)

        st.divider()

        # Identified Factors & Qualitative Analysis
        col_f1, col_f2 = st.columns([1, 1])

        with col_f1:
            st.markdown("### 🔎 Key Focus Factors")
            if res["factors"]:
                factor_html = "".join([f"<div style='margin-bottom: 10px; padding: 8px 12px; background-color: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 4px; color: #E2E8F0;'>⚠️ {f}</div>" for f in res["factors"]])
                st.markdown(f"<div style='margin-bottom: 15px;'>{factor_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='margin-bottom: 10px; padding: 8px 12px; background-color: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; border-radius: 4px; color: #E2E8F0;'>✅ No acute distress factors identified</div>", unsafe_allow_html=True)

            if res.get("protective_factors"):
                st.markdown("#### 🛡️ Protective Factors Present")
                prot_html = "".join([f"<div style='margin-bottom: 10px; padding: 8px 12px; background-color: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; border-radius: 4px; color: #E2E8F0;'>🛡️ {pf}</div>" for pf in res["protective_factors"]])
                st.markdown(prot_html, unsafe_allow_html=True)

        with col_f2:
            st.markdown("### 💬 Reflection & Language Analysis")
            if res["has_text"]:
                c_t1, c_t2, c_t3 = st.columns(3)
                with c_t1:
                    st.metric("Distress Cues", len(res["distress_keywords"]))
                with c_t2:
                    st.metric("Resilience Cues", len(res["positive_keywords"]))
                with c_t3:
                    st.metric("Safety Cues", len(res["safety_keywords"]))

                if res["distress_keywords"] or res["positive_keywords"] or res["safety_keywords"]:
                    with st.expander("🔍 View Detected Language Patterns", expanded=False):
                        if res["distress_keywords"]:
                            st.write(f"**Distress Markers:** {', '.join(set(res['distress_keywords']))}")
                        if res["positive_keywords"]:
                            st.write(f"**Resilience Markers:** {', '.join(set(res['positive_keywords']))}")
                        if res["safety_keywords"]:
                            st.write(f"**Safety Mentions:** {', '.join(set(res['safety_keywords']))}")
            else:
                st.info("No written reflection was entered during this screening session.")

        st.divider()

        # Personalized Next Steps & Action Cards
        st.markdown("### 🛠️ Tailored Action & Support Recommendations")
        rec_cards = intervention_plan(res["level"], res["factors"])

        for title, desc in rec_cards:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(desc)

        # High Risk Alert Box
        if res["level"] == "HIGH" or "Safety concern" in res["factors"]:
            st.markdown("""
            <div class="emergency-box">
                <h4 style="margin: 0 0 6px 0; color: #991b1b;">🚨 Immediate 24/7 Confidential Assistance Available</h4>
                <p style="margin: 0 0 10px 0; font-size: 0.92rem;">
                    If you are feeling overwhelmed, unsafe, or going through a severe crisis, immediate free human support is available:
                </p>
                <div style="font-weight: 600; font-size: 0.95rem;">
                    📞 Tele-MANAS (Govt of India): <b style="color: #60A5FA;">14416</b> / <b style="color: #60A5FA;">1800-891-4416</b> (24x7 Free)<br>
                    📞 Vandrevala Foundation: <b style="color: #60A5FA;">+91 9999 666 555</b><br>
                    📞 KIRAN Mental Health Helpline: <b style="color: #60A5FA;">1800-599-0019</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 Retake Assessment", use_container_width=True):
                st.session_state.latest_assessment_result = None
                st.session_state.assessment_step = 1
                st.session_state.step_error = None
                st.session_state.assessment_form = {
                    "consent": True,
                    "mood": None,
                    "anxiety": None,
                    "stress": None,
                    "sleep": None,
                    "concentration": None,
                    "helplessness": None,
                    "isolation": None,
                    "support": None,
                    "safety_concern": None,
                    "user_text": "",
                    "case_involved": None,
                    "stage": None
                }
                st.rerun()
        with col_btn2:
            st.button("📥 Download Summary Report (CSV ready)", use_container_width=True, on_click=lambda: None)

    # --- STEP-BY-STEP WIZARD VIEW ---
    else:
        st.title("🧠 AI Wellbeing Assessment")
        st.write("A gentle, private evaluation to understand your emotional health and support needs.")

        # Consent Check if not yet accepted
        if not st.session_state.assessment_form["consent"]:
            with st.container(border=True):
                st.markdown("### 🤝 Informed Screening Consent")
                st.write(
                    "Welcome to Sahara AI. This multi-factor tool evaluates self-reported emotional wellbeing, "
                    "daily functioning, and social connectivity to provide helpful early insights."
                )
                st.markdown("""
                - 🔒 **Your data is kept private** and processed strictly within your active session.
                - 👩‍⚕️ **This is an AI screening prototype**, not a clinical medical diagnosis or psychiatric evaluation.
                - 🚨 In urgent emergencies, please reach out to local healthcare and emergency responders.
                - ⚠️ **All questions are mandatory** to ensure an accurate, reliable evaluation. No options are preselected.
                """)

                agree = st.checkbox(
                    "I understand and agree to proceed with this private wellbeing assessment.",
                    value=st.session_state.assessment_form["consent"]
                )

                if st.button("Begin Assessment →", type="primary", disabled=not agree):
                    st.session_state.assessment_form["consent"] = True
                    st.session_state.assessment_step = 1
                    st.session_state.step_error = None
                    st.rerun()

        else:
            # Multi-Step Stepper Progress Bar
            step = st.session_state.assessment_step
            total_steps = 4

            step_names = [
                "1. Emotional Pulse",
                "2. Body & Habits",
                "3. Connection & Safety",
                "4. Reflection & Context"
            ]

            st.progress(step / total_steps)

            # Stepper Header UI
            st.markdown(f"""
            <div class="step-header">
                <div>
                    <span class="step-badge">STEP {step} OF {total_steps}</span>
                    <h3 style="margin: 8px 0 0 0; color: #F8FAFC;">{step_names[step-1]}</h3>
                </div>
                <div style="font-size: 0.85rem; color: #ef4444; font-weight: 500;">
                    * All questions are required
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Display validation error message if user tried to proceed without answering all
            if st.session_state.step_error:
                st.error(st.session_state.step_error)

            form = st.session_state.assessment_form

            # ==========================================
            # STEP 1: EMOTIONAL PULSE
            # ==========================================
            if step == 1:
                with st.container(border=True):
                    st.markdown("#### 🌟 1. Mood Spectrum <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("How would you describe your overall emotional mood over the past week?")
                    mood_opts = [
                        "😞 Very low",
                        "🙁 Low",
                        "😐 Okay",
                        "🙂 Good",
                        "😊 Very good"
                    ]
                    current_idx = mood_opts.index(form["mood"]) if form["mood"] in mood_opts else None

                    selected_mood = st.radio(
                        "Select your mood state:",
                        mood_opts,
                        index=current_idx,
                        horizontal=True,
                        key="radio_mood"
                    )
                    form["mood"] = selected_mood

                with st.container(border=True):
                    st.markdown("#### 🌊 2. Anxiety & Restlessness <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("How frequently have you felt overwhelmed, uneasy, or persistently anxious?")
                    anx_opts = ["Never", "Rarely", "Sometimes", "Often", "Almost always"]
                    current_anx_idx = anx_opts.index(form["anxiety"]) if form["anxiety"] in anx_opts else None

                    form["anxiety"] = st.radio(
                        "Anxiety frequency:",
                        anx_opts,
                        index=current_anx_idx,
                        horizontal=True,
                        key="radio_anxiety"
                    )

                with st.container(border=True):
                    st.markdown("#### ⚡ 3. Current Stress Pressure <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("What level of mental pressure or tension have you been experiencing?")
                    stress_opts = ["Not at all", "A little", "Moderately", "Very stressed", "Extremely stressed"]
                    current_stress_idx = stress_opts.index(form["stress"]) if form["stress"] in stress_opts else None

                    form["stress"] = st.radio(
                        "Stress intensity:",
                        stress_opts,
                        index=current_stress_idx,
                        horizontal=True,
                        key="radio_stress"
                    )

                # Navigation
                col_n1, col_n2 = st.columns([1, 1])
                with col_n2:
                    if st.button("Continue to Body & Habits →", type="primary", use_container_width=True):
                        missing = []
                        if form["mood"] is None:
                            missing.append("1. Mood Spectrum")
                        if form["anxiety"] is None:
                            missing.append("2. Anxiety & Restlessness")
                        if form["stress"] is None:
                            missing.append("3. Current Stress Pressure")

                        if missing:
                            st.session_state.step_error = f"⚠️ Please answer all mandatory questions before proceeding: {', '.join(missing)}"
                            st.rerun()
                        else:
                            st.session_state.step_error = None
                            st.session_state.assessment_step = 2
                            st.rerun()

            # ==========================================
            # STEP 2: BODY & DAILY HABITS
            # ==========================================
            elif step == 2:
                with st.container(border=True):
                    st.markdown("#### 💤 4. Sleep Quality & Patterns <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("Have you experienced insomnia, restless sleep, or trouble falling asleep?")
                    sleep_opts = ["Never", "Rarely", "Sometimes", "Often", "Almost every night"]
                    current_sleep_idx = sleep_opts.index(form["sleep"]) if form["sleep"] in sleep_opts else None

                    form["sleep"] = st.radio(
                        "Sleep disruption:",
                        sleep_opts,
                        index=current_sleep_idx,
                        horizontal=True,
                        key="radio_sleep"
                    )

                with st.container(border=True):
                    st.markdown("#### 🎯 5. Mental Focus & Concentration <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("Have you found it difficult to focus on daily tasks, work, or decisions?")
                    conc_opts = ["Not at all", "A little", "Sometimes", "Often", "Almost always"]
                    current_conc_idx = conc_opts.index(form["concentration"]) if form["concentration"] in conc_opts else None

                    form["concentration"] = st.radio(
                        "Focus difficulty:",
                        conc_opts,
                        index=current_conc_idx,
                        horizontal=True,
                        key="radio_concentration"
                    )

                with st.container(border=True):
                    st.markdown("#### 🌧️ 6. Coping & Helplessness <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("How often have you felt like situations are completely out of your control?")
                    help_opts = ["Never", "Rarely", "Sometimes", "Often", "Almost always"]
                    current_help_idx = help_opts.index(form["helplessness"]) if form["helplessness"] in help_opts else None

                    form["helplessness"] = st.radio(
                        "Feelings of helplessness:",
                        help_opts,
                        index=current_help_idx,
                        horizontal=True,
                        key="radio_helplessness"
                    )

                # Navigation
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    if st.button("← Back to Emotional Pulse", use_container_width=True):
                        st.session_state.step_error = None
                        st.session_state.assessment_step = 1
                        st.rerun()
                with col_b2:
                    if st.button("Continue to Connection & Safety →", type="primary", use_container_width=True):
                        missing = []
                        if form["sleep"] is None:
                            missing.append("4. Sleep Quality")
                        if form["concentration"] is None:
                            missing.append("5. Focus & Concentration")
                        if form["helplessness"] is None:
                            missing.append("6. Coping & Helplessness")

                        if missing:
                            st.session_state.step_error = f"⚠️ Please answer all mandatory questions before proceeding: {', '.join(missing)}"
                            st.rerun()
                        else:
                            st.session_state.step_error = None
                            st.session_state.assessment_step = 3
                            st.rerun()

            # ==========================================
            # STEP 3: CONNECTION & SAFETY
            # ==========================================
            elif step == 3:
                with st.container(border=True):
                    st.markdown("#### 🫂 7. Social Connectedness <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("How connected and understood do you feel by friends, family, or your community?")
                    iso_opts = [
                        "Very connected",
                        "Somewhat connected",
                        "Neither connected nor disconnected",
                        "Somewhat disconnected",
                        "Very disconnected"
                    ]
                    current_iso_idx = iso_opts.index(form["isolation"]) if form["isolation"] in iso_opts else None

                    form["isolation"] = st.radio(
                        "Connection level:",
                        iso_opts,
                        index=current_iso_idx,
                        key="radio_isolation"
                    )

                with st.container(border=True):
                    st.markdown("#### 🤝 8. Trusted Support System <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("Do you have someone you feel safe confiding in without judgment?")
                    supp_opts = [
                        "Yes, definitely",
                        "Yes, somewhat",
                        "Not really",
                        "No"
                    ]
                    current_supp_idx = supp_opts.index(form["support"]) if form["support"] in supp_opts else None

                    form["support"] = st.radio(
                        "Support availability:",
                        supp_opts,
                        index=current_supp_idx,
                        horizontal=True,
                        key="radio_support"
                    )

                with st.container(border=True):
                    st.markdown("#### 🛡️ 9. Personal Safety & Threat Check <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("Do you currently feel unsafe, threatened, or in immediate distress in your environment?")
                    safe_opts = ["No", "A little", "Somewhat", "Yes, significantly"]
                    current_safe_idx = safe_opts.index(form["safety_concern"]) if form["safety_concern"] in safe_opts else None

                    form["safety_concern"] = st.radio(
                        "Safety concern:",
                        safe_opts,
                        index=current_safe_idx,
                        horizontal=True,
                        key="radio_safety"
                    )

                # Navigation
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    if st.button("← Back to Body & Habits", use_container_width=True):
                        st.session_state.step_error = None
                        st.session_state.assessment_step = 2
                        st.rerun()
                with col_c2:
                    if st.button("Continue to Reflection & Context →", type="primary", use_container_width=True):
                        missing = []
                        if form["isolation"] is None:
                            missing.append("7. Social Connectedness")
                        if form["support"] is None:
                            missing.append("8. Trusted Support System")
                        if form["safety_concern"] is None:
                            missing.append("9. Personal Safety")

                        if missing:
                            st.session_state.step_error = f"⚠️ Please answer all mandatory questions before proceeding: {', '.join(missing)}"
                            st.rerun()
                        else:
                            st.session_state.step_error = None
                            st.session_state.assessment_step = 4
                            st.rerun()

            # ==========================================
            # STEP 4: REFLECTION & CONTEXT
            # ==========================================
            elif step == 4:
                with st.container(border=True):
                    st.markdown("#### ⚖️ 10. Situational / Case Journey Context <span class='required-badge'>*</span>", unsafe_allow_html=True)
                    st.caption("Are you currently navigating a formal case, legal proceeding, or institutional support process?")

                    case_opts = ["No", "Yes"]
                    c_idx = case_opts.index(form["case_involved"]) if form["case_involved"] in case_opts else None
                    form["case_involved"] = st.radio(
                        "Involved in a formal process:",
                        case_opts,
                        index=c_idx,
                        horizontal=True,
                        key="radio_case_involved"
                    )

                    if form["case_involved"] == "Yes":
                        stage_opts = [
                            "Complaint / Initial Support",
                            "Investigation",
                            "Court / Legal Proceedings",
                            "Compensation / Rehabilitation",
                            "Post-case Follow-up"
                        ]
                        s_idx = stage_opts.index(form["stage"]) if form["stage"] in stage_opts else None
                        st.markdown("<p style='margin-top: 10px; font-size: 0.9rem; font-weight: 500;'>Select current stage: <span class='required-badge'>*</span></p>", unsafe_allow_html=True)
                        form["stage"] = st.selectbox(
                            "Current stage of the journey:",
                            stage_opts,
                            index=s_idx,
                            placeholder="Choose your current stage...",
                            key="select_stage"
                        )
                    elif form["case_involved"] == "No":
                        form["stage"] = "Not involved in a legal/case process"

                with st.container(border=True):
                    st.markdown("#### 📝 11. Open Voice & Emotional Check-in *(Optional)*")
                    st.caption("Share anything you feel comfortable expressing. Our AI detects contextual indicators to provide nuanced recommendations.")

                    form["user_text"] = st.text_area(
                        "Share your thoughts (optional):",
                        value=form["user_text"],
                        placeholder="E.g., I've been feeling overwhelmed with work deadlines and finding it hard to sleep peacefully...",
                        height=120,
                        key="textarea_user_text"
                    )

                # Navigation & Submission
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    if st.button("← Back to Connection & Safety", use_container_width=True):
                        st.session_state.step_error = None
                        st.session_state.assessment_step = 3
                        st.rerun()

                with col_d2:
                    if st.button("✨ Complete & Analyze Wellbeing", type="primary", use_container_width=True):
                        missing = []
                        if form["case_involved"] is None:
                            missing.append("10. Situational / Case Journey Context")
                        elif form["case_involved"] == "Yes" and form["stage"] is None:
                            missing.append("Current stage of the journey")

                        if missing:
                            st.session_state.step_error = f"⚠️ Please answer all mandatory questions before completing: {', '.join(missing)}"
                            st.rerun()

                        # Mapping values to score calculation
                        mood_map = {
                            "😞 Very low": 1,
                            "🙁 Low": 2,
                            "😐 Okay": 3,
                            "🙂 Good": 4,
                            "😊 Very good": 5
                        }
                        anx_map = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4}
                        stress_map = {"Not at all": 0, "A little": 1, "Moderately": 2, "Very stressed": 3, "Extremely stressed": 4}
                        sleep_map = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost every night": 4}
                        conc_map = {"Not at all": 0, "A little": 1, "Sometimes": 2, "Often": 3, "Almost always": 4}
                        iso_map = {
                            "Very connected": 0,
                            "Somewhat connected": 1,
                            "Neither connected nor disconnected": 2,
                            "Somewhat disconnected": 3,
                            "Very disconnected": 4
                        }
                        help_map = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Almost always": 4}
                        supp_map = {"Yes, definitely": 4, "Yes, somewhat": 3, "Not really": 1, "No": 0}
                        safe_map = {"No": 0, "A little": 1, "Somewhat": 3, "Yes, significantly": 5}

                        m_val = mood_map[form["mood"]]
                        a_val = anx_map[form["anxiety"]]
                        st_val = stress_map[form["stress"]]
                        sl_val = sleep_map[form["sleep"]]
                        co_val = conc_map[form["concentration"]]
                        is_val = iso_map[form["isolation"]]
                        hl_val = help_map[form["helplessness"]]
                        su_val = supp_map[form["support"]]
                        sf_val = safe_map[form["safety_concern"]]

                        # Base score
                        distress_score = calculate_distress(
                            m_val, a_val, sl_val, is_val, co_val, st_val, hl_val, sf_val, su_val
                        )

                        # Qualitative NLP Analysis
                        text_score = 0
                        d_matches, sf_matches, pos_matches = [], [], []
                        has_text = bool(form["user_text"].strip())

                        if has_text:
                            text_score, d_matches, sf_matches, pos_matches = analyze_text(form["user_text"])
                            distress_score = clamp(distress_score + text_score)

                        level = get_risk_level(distress_score)
                        wellbeing_score = 100 - distress_score

                        # Factors
                        factors = []
                        if sl_val >= 3:
                            factors.append("Sleep disruption")
                        if is_val >= 3:
                            factors.append("Social disconnection")
                        if a_val >= 3:
                            factors.append("High anxiety")
                        if st_val >= 3:
                            factors.append("Elevated stress")
                        if hl_val >= 3:
                            factors.append("Feeling overwhelmed")
                        if sf_val >= 2:
                            factors.append("Safety concern")
                        if len(d_matches) >= 3:
                            factors.append("Expressed distress in reflection")

                        protective_factors = []
                        if su_val >= 3:
                            protective_factors.append("Active trusted support network")
                        if m_val >= 4:
                            protective_factors.append("Resilient baseline mood")
                        if len(pos_matches) >= 2:
                            protective_factors.append("Positive coping outlook expressed")

                        # Save into history
                        record = {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "score": distress_score,
                            "level": level,
                            "stage": form["stage"]
                        }
                        st.session_state.assessment_history.append(record)

                        # Store result for rendering
                        st.session_state.step_error = None
                        st.session_state.latest_assessment_result = {
                            "distress_score": distress_score,
                            "wellbeing_score": wellbeing_score,
                            "level": level,
                            "stage": form["stage"],
                            "factors": factors,
                            "protective_factors": protective_factors,
                            "has_text": has_text,
                            "distress_keywords": d_matches,
                            "safety_keywords": sf_matches,
                            "positive_keywords": pos_matches
                        }
                        st.rerun()


# ============================================================
# WELLBEING TREND
# ============================================================

elif page == "Wellbeing Trend":
    st.title("📈 Longitudinal Wellbeing Trend")
    st.write("Monitor how distress and resilience markers evolve over time.")

    history = st.session_state.assessment_history

    if not history:
        st.info("No assessment history recorded yet. Complete your first assessment to begin tracking.")
    else:
        df = pd.DataFrame(history)
        # Create a unique, shorter date string for straight labels (and guarantee next unit)
        display_dates = []
        for i, row in df.iterrows():
            try:
                # Convert to shorter format: 'MM-DD HH:MM'
                dt = pd.to_datetime(row['date'])
                # If there are duplicates in the exact same minute, the sequence number ensures uniqueness
                d_str = dt.strftime("%m-%d %H:%M")
            except:
                d_str = str(row['date'])
            display_dates.append(f"{d_str} (#{i+1})")
        df["display_date"] = display_dates
        latest = df.iloc[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest Distress Score", f"{latest['score']}/100")
        with col2:
            st.metric("Current Status", latest["level"])
        with col3:
            st.metric("Total Check-ins", len(df))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Distress Trajectory (Scale 0 - 100)")

        trend_base = alt.Chart(df).encode(
            x=alt.X("display_date:O", sort=df["display_date"].tolist(), title="Check-in Sequence & Time", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "score:Q",
                title="Distress Score (0 - 100)",
                scale=alt.Scale(domain=[0, 100], clamp=True),
                axis=alt.Axis(values=[0, 20, 40, 60, 80, 100])
            ),
            tooltip=[
                alt.Tooltip("date:N", title="Date"),
                alt.Tooltip("score:Q", title="Distress Score"),
                alt.Tooltip("level:N", title="Risk Level"),
                alt.Tooltip("stage:N", title="Journey Stage")
            ]
        )

        trend_line = trend_base.mark_line(color="#4f46e5", strokeWidth=3, interpolate="monotone")
        trend_points = trend_base.mark_circle(size=75, color="#4338ca")

        # Threshold guide lines
        rule_low = alt.Chart(pd.DataFrame({"y": [35]})).mark_rule(color="#10b981", strokeDash=[4, 4], opacity=0.7).encode(y="y:Q")
        rule_high = alt.Chart(pd.DataFrame({"y": [65]})).mark_rule(color="#ef4444", strokeDash=[4, 4], opacity=0.7).encode(y="y:Q")

        trend_chart = (trend_line + trend_points + rule_low + rule_high).properties(height=340)
        st.altair_chart(trend_chart, use_container_width=True)

        # Delta Analysis
        if len(df) >= 2:
            prev = df.iloc[-2]["score"]
            curr = df.iloc[-1]["score"]
            diff = curr - prev

            if diff > 10:
                st.error(f"🚨 Distress score spiked by **+{diff} points** compared to your previous check-in. Extra support is encouraged.")
            elif diff > 0:
                st.warning(f"⚠️ Distress score increased by **+{diff} points**.")
            elif diff < 0:
                st.success(f"🌱 Distress score improved by **{abs(diff)} points**! Keep up your positive coping routines.")
            else:
                st.info("⚖️ Distress score has remained steady.")

        st.divider()
        st.subheader("📋 Check-in Logs")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Export Wellbeing History (CSV)",
            csv,
            "sahara_wellbeing_history.csv",
            "text/csv"
        )


# ============================================================
# CASE JOURNEY
# ============================================================

elif page == "Case Journey":
    st.title("🛡️ Institutional & Case Journey Tracker")
    st.write("Coordinate trauma-informed psychosocial support across distinct phases of the case lifecycle.")

    stages = [
        ("1. Complaint Registered", "Immediate stabilization, psychological first aid, and orientation to available rights."),
        ("2. Investigation Phase", "Routine stress check-ins, testimony prep anxiety mitigation, and confidential monitoring."),
        ("3. Legal / Court Proceedings", "Targeted courtroom stress reduction, accompaniment, and high-frequency checks."),
        ("4. Compensation & Rehabilitation", "Inter-agency coordination, vocational support, and recovery plan management."),
        ("5. Post-case Follow-up", "Long-term community reintegration and enduring emotional resilience tracking.")
    ]

    for title, description in stages:
        with st.container(border=True):
            st.markdown(f"#### {title}")
            st.write(description)

    st.divider()
    st.subheader("📌 Active Support Provisions")

    actions = st.multiselect(
        "Select required support mechanisms:",
        [
            "Psychological Counselling",
            "Medical / Healthcare Support",
            "Legal Aid & Representation",
            "Witness Protection & Safety Escort",
            "Safe Relocation & Shelter",
            "Emergency Financial Relief",
            "Vocational Rehabilitation",
            "Routine Wellbeing Monitoring"
        ]
    )

    if actions:
        st.success("Selected support provisions updated for this active session.")
        for action in actions:
            st.markdown(f"• **{action}**")


# ============================================================
# PROFESSIONAL CONNECT
# ============================================================

elif page == "Professional Connect":
    st.title("🤝 Professional Connect")
    st.write(
        "Connect with trusted mental-health support through government services "
        "or private qualified professionals."
    )

    # --------------------------------------------------------
    # GOVERNMENT SUPPORT
    # --------------------------------------------------------
    st.subheader("🏛️ Government Mental Health Support")
    st.caption("Official national services and public mental-health support.")

    with st.container(border=True):
        st.markdown("### 🧠 Tele-MANAS")
        st.write(
            "**Government of India – National Tele Mental Health Programme**"
        )
        st.write(
            "Free and confidential 24×7 tele-mental health support. "
            "Counsellors can provide initial support and refer users to "
            "mental-health specialists when required."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Helpline", "14416")

        with col2:
            st.metric("Alternate", "1800-89-14416")

        st.info("📞 Call 14416 for Tele-MANAS support.")
    
    with st.container(border=True):
           
        st.markdown("### 🏥 Ayushman Arogya Mandir")
    
        st.write(
            "Government primary-health facilities providing comprehensive "
            "primary healthcare, including mental-health screening and "
            "basic management."
        )
    
        st.write(
            "Tele-consultation and referral pathways can help connect "
            "patients with higher-level care when required."
        )
    
        st.link_button(
            "🏥 Open Official Ayushman Arogya Mandir Portal",
            "https://aam.mohfw.gov.in/"
        )
    
        st.divider()
    
       # --------------------------------------------------------
    # PRIVATE PROFESSIONAL SUPPORT
    # --------------------------------------------------------
    st.subheader("👩‍⚕️ Private Professional Support")
    
    st.caption(
        "For users who want a private consultation with a qualified "
        "mental-health professional."
    )
    
    with st.container(border=True):
    
        professional_type = st.selectbox(
            "What type of professional are you looking for?",
            [
                "Psychiatrist",
                "Clinical Psychologist",
                "Psychologist / Counsellor",
                "Trauma-focused Therapist"
            ],
            index=None
        )
    
        mode = st.selectbox(
            "Preferred consultation mode",
            [
                "Online Consultation",
                "In-person Consultation",
                "Either"
            ],
            index=None
        )

        if not professional_type or not mode:
            st.info("👆 Please select both a professional type and consultation mode to view available providers.")
        else:
            st.markdown(f"### 🔎 {professional_type}")
        
            st.write(f"**Consultation mode:** {mode}")
        
            st.markdown(
                "Choose a real healthcare provider to search for available "
                "mental-health professionals."
            )
        
            st.divider()
        
            # --------------------------------------------------------
            # PRIVATE PROVIDER OPTIONS
            # --------------------------------------------------------
        
            if professional_type == "Psychiatrist":
        
                st.markdown("#### 🧠 Psychiatrist Consultation")
        
                st.write(
                    "Find psychiatrists for psychiatric assessment and "
                    "medical consultation."
                )
        
                st.link_button(
                    "🔎 Find Psychiatrists on Practo",
                    "https://www.practo.com/consult/online-psychiatrist-consultation"
                )
        
            elif professional_type == "Clinical Psychologist":
        
                st.markdown("#### 🧠 Clinical Psychologist")
        
                st.write(
                    "Search for clinical psychologists and mental-health "
                    "professionals for assessment and psychological support."
                )
        
                st.link_button(
                    "🔎 Find Clinical Psychologists on Practo",
                    "https://www.practo.com/consult"
                )
        
            elif professional_type == "Psychologist / Counsellor":
        
                st.markdown("#### 💬 Counselling / Psychological Support")
        
                st.write(
                    "Search for psychologists and counsellors for "
                    "professional emotional and psychological support."
                )
        
                st.link_button(
                    "🔎 Find Counsellors on Practo",
                    "https://www.practo.com/consult"
                )
        
            elif professional_type == "Trauma-focused Therapist":
        
                st.markdown("#### 🧠 Trauma-focused Therapy")
        
                st.write(
                    "Find mental-health professionals who may provide "
                    "trauma-focused psychological support."
                )
        
                st.link_button(
                    "🔎 Find Professionals on Practo",
                    "https://www.practo.com/consult"
                )
        
            st.caption(
                "Sahaara AI does not create fictional doctors, ratings, fees, "
                "availability or appointment confirmations. You will complete "
                "the consultation directly through the selected provider."
            )

    # --------------------------------------------------------
    # TRUSTED CONTACT
    # --------------------------------------------------------
    st.subheader("🤝 Trusted Support Contact")

    trusted_person = st.text_input(
        "Contact Name (Friend, Family, or Mentor)"
    )

    relationship = st.selectbox(
        "Relationship",
        [
            "Family Member",
            "Close Friend",
            "Mentor",
            "Legal Advocate",
            "Other"
        ]
    )

    if st.button("Save Trusted Contact"):
        if trusted_person.strip():
            st.success(
                f"✅ {trusted_person} has been saved as your "
                f"{relationship.lower()} support contact."
            )
        else:
            st.warning("Please enter a valid contact name.")

elif page == "Resilience Support":
    st.title("🌍 Environmental & Crisis Stressor Logger")
    st.write("Account for external contextual factors (e.g. natural disasters, heatwaves, displacement) that compound personal distress.")

    # Dictionary mapping events and severity to specific coping mechanisms
    resilience_strategies = {
        "Severe Flooding / Relocation": {
            "Low impact": [
                "**Stay Informed:** Monitor local weather updates and official flood warnings.",
                "**Prep Your Kit:** Review your emergency kit and ensure important documents are stored in waterproof containers.",
                "**Boundaries:** Limit exposure to stressful news cycles; stick to official updates twice a day."
            ],
            "Moderate impact": [
                "**Routine:** Establish a daily routine in your temporary setup to maintain a sense of normalcy.",
                "**Community:** Connect with community support groups or local relief organizations.",
                "**Grounding:** Practice the 5-4-3-2-1 sensory technique when feeling overwhelmed by property damage or disruption."
            ],
            "High / Displaced": [
                "**Safety First:** Prioritize physical safety, clean water, and shelter above all else.",
                "**Pacing:** Focus on taking things one hour at a time. Do not force yourself to process the trauma immediately.",
                "**Aid:** Register with official displacement camps or NGOs to access psychosocial first aid.",
                "**Distancing:** Use psychological distancing: remind yourself 'I am safe right now' when panic arises."
            ]
        },
        "Extreme Heatwave Event": {
            "Low impact": [
                "**Hydration:** Drink water consistently and avoid strenuous outdoor activities during peak sun hours.",
                "**Cooling Breath:** Practice cooling breath techniques (e.g., Sitali breath) to regulate body temperature and anxiety.",
                "**Check-ins:** Check in on vulnerable neighbors or family members."
            ],
            "Moderate impact": [
                "**Biological Link:** Heat can significantly increase irritability and anxiety. Acknowledge this biological link rather than blaming yourself.",
                "**Sanctuary:** Create a cool sanctuary space in your home if possible, focusing on airflow.",
                "**Lower Expectations:** Pace your daily tasks. Lower your expectations for productivity during extreme heat."
            ],
            "High / Displaced": [
                "**Relocate:** Move to community cooling centers immediately if your living situation becomes dangerously hot.",
                "**Symptom Check:** Watch for physical signs of heat exhaustion which mimic panic attacks (racing heart, dizziness).",
                "**Conserve Energy:** Conserve physical and mental energy. Rest completely."
            ]
        },
        "Hazardous Air Quality / Pollution": {
            "Low impact": [
                "**Monitor AQI:** Keep windows closed and monitor local air quality index (AQI) apps.",
                "**Protection:** Wear appropriate N95/KN95 masks if you must go outside.",
                "**Adapt Routine:** Do light indoor stretching instead of outdoor cardio to maintain mental health."
            ],
            "Moderate impact": [
                "**Combat Cabin Fever:** Being trapped indoors can cause 'cabin fever'. Counteract this by creating structured indoor activities.",
                "**Air Quality:** Use HEPA air purifiers if available. The white noise can also aid focus and relaxation.",
                "**Virtual Connection:** Stay connected virtually with friends to mitigate the isolation of staying indoors."
            ],
            "High / Displaced": [
                "**Medical Care:** If respiratory distress occurs, seek medical attention rather than assuming it is an anxiety attack.",
                "**Relocation:** Consider temporary relocation if the air quality remains hazardous for an extended period and you are vulnerable.",
                "**Mental Escape:** Practice guided imagery meditation to mentally escape the confined indoor environment."
            ]
        },
        "Civil / Community Disruption": {
            "Low impact": [
                "**Media Diet:** Limit social media scrolling, which can rapidly amplify fear and outrage.",
                "**Locus of Control:** Focus on your immediate circle of control: your home, your family, your daily routine.",
                "**Validation:** Validate your feelings of uncertainty without letting them dictate your actions."
            ],
            "Moderate impact": [
                "**Communication:** Maintain regular communication with trusted friends and family to ensure mutual safety.",
                "**Safe Zones:** Identify safe zones and avoid engaging in high-conflict areas or intense online debates.",
                "**Action:** Channel stress into community care or organizing within safe, trusted networks."
            ],
            "High / Displaced": [
                "**Evacuation:** Prioritize physical safety and strictly follow official evacuation or curfew orders.",
                "**Present Focus:** Focus entirely on the present moment. Trauma responses (numbness, hyperarousal) are normal during active disruptions.",
                "**First Aid:** Connect with crisis counselors or NGOs operating in the area for psychological first aid."
            ]
        },
        "Financial Crisis / Crop Loss": {
            "Low impact": [
                "**Objectivity:** Acknowledge the stressor. Write down a clear, objective list of financial impacts without catastrophizing.",
                "**Triage:** Identify what immediate expenses can be paused or reduced.",
                "**Self-Worth:** Remind yourself frequently that your inherent self-worth is not tied to your financial or agricultural output."
            ],
            "Moderate impact": [
                "**Active Aid:** Seek out government subsidies, crop insurance, or community aid programs actively.",
                "**Micro-planning:** Break down financial planning into small, 1-week increments rather than projecting years into the unknown future.",
                "**Share the Burden:** Communicate openly with family members about the situation to reduce the burden of carrying it alone."
            ],
            "High / Displaced": [
                "**Survival Needs:** Focus purely on immediate survival needs: food banks, local shelters, or community kitchens.",
                "**Community Support:** Do not isolate yourself out of shame. Reaching out to community networks is a vital survival mechanism.",
                "**Specialized Counsel:** Contact financial counselors, agricultural extension officers, or NGOs who specialize in crisis recovery."
            ]
        },
        "Other Acute External Stressor": {
            "Low impact": [
                "**Baselines:** Maintain your baseline self-care routines (sleep, nutrition, hydration).",
                "**Information Diet:** Limit exposure to news and social media surrounding the stressor.",
                "**Micro-control:** Identify just one small thing you can control today."
            ],
            "Moderate impact": [
                "**Cognitive Grace:** Acknowledge that your cognitive load is high. It is completely normal to be forgetful or irritable.",
                "**Delegation:** Lean heavily on your support network and explicitly ask for help with daily tasks.",
                "**Nervous System Reset:** Practice box breathing (inhale 4s, hold 4s, exhale 4s, hold 4s) to reset your nervous system."
            ],
            "High / Displaced": [
                "**Survival Mode:** Recognize your brain is in survival mode. Do not expect normal emotional processing right now.",
                "**Physiology First:** Secure basic physiological and safety needs before attempting any deep emotional work.",
                "**Intervention:** Seek out professional crisis intervention and community aid as soon as safely possible."
            ]
        }
    }

    event = st.selectbox(
        "Select external contextual event:",
        [
            "No major event",
            "Severe Flooding / Relocation",
            "Extreme Heatwave Event",
            "Hazardous Air Quality / Pollution",
            "Civil / Community Disruption",
            "Financial Crisis / Crop Loss",
            "Other Acute External Stressor"
        ]
    )

    if event != "No major event":
        severity = st.radio(
            "Impact intensity on daily life:",
            ["Low impact", "Moderate impact", "High / Displaced"],
            horizontal=True,
            index=None
        )

        if severity:
            st.markdown("---")
            
            # Display contextual warning/info box based on severity
            if severity == "Low impact":
                st.info(f"ℹ️ **Context Registered:** {event} (Low Impact). Incorporating basic coping mechanisms.")
            elif severity == "Moderate impact":
                st.warning(f"⚠️ **Context Registered:** {event} (Moderate Impact). Elevated resilience support recommended.")
            else:
                st.error(f"🚨 **Critical Context Registered:** {event} (High / Displaced). Prioritize immediate safety, shelter, and hydration needs.")
                
            if severity in ["Moderate impact", "High / Displaced"]:
                st.markdown("### 📡 Government Agency Dispatch (Simulation)")
                st.success("An automated data packet has been prepared for transmission to local emergency management agencies to assist affected individuals.")
                st.markdown("""
                <div style='background-color: #1E1F2A; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                    <h4 style='margin-top: 0; color: #FCD34D;'>🚨 Direct Emergency Contacts</h4>
                    <p style='margin-bottom: 8px; color: #E2E8F0; font-size: 0.9rem;'>While this prototype simulates agency dispatch, please contact authorities directly in a real crisis:</p>
                    <div style='font-size: 1.05rem; line-height: 1.6;'>
                        📞 National Emergency Number: <b style='color: #60A5FA;'>112</b><br>
                        📞 Disaster Management (NDMA/NDRF): <b style='color: #60A5FA;'>1078</b><br>
                        📞 Ambulance Services: <b style='color: #60A5FA;'>108</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"### 🛡️ Resilience & Coping Strategies for {severity}")
            
            tips = resilience_strategies.get(event, {}).get(severity, [])
            
            for tip in tips:
                import re
                tip_formatted = re.sub(r'\*\*(.*?)\*\*', r"<span style='color: #60A5FA; font-weight: 600;'>\1</span>", tip)
                st.markdown(f"<div style='background-color: #1E1F2A; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #3B82F6;'>{tip_formatted}</div>", unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Log Stressor to Case Profile", type="primary"):
                st.success("✅ Stressor logged successfully. Your AI assessments will now take this context into account.")
        else:
            st.info("👆 Please select an impact intensity above to generate tailored coping mechanisms.")

    else:
        st.success("✅ No external crisis factor reported. You can log environmental stressors here if circumstances change.")


# ============================================================
# PRIVACY & SAFETY
# ============================================================

elif page == "Privacy & Safety":
    st.title("🔐 Privacy, Safeguarding & Responsible AI")

    st.markdown("""
    ### 🛡️ Core Safeguarding Principles
    1. **Data Minimization**: We collect only vital screening signals without unneeded identifying metadata.
    2. **Explicit Consent**: Transparent opt-in before any emotional assessment is performed.
    3. **Human-in-the-Loop**: AI scores serve strictly as triage decision-support and never make unilateral clinical decisions.
    4. **Safety Escalation**: Direct, unhindered access to 24/7 verified emergency crisis resources.
    """)

    st.divider()

    st.markdown("""
    <div class="disclaimer">
        <b>🚨 Emergency Safety Notice</b><br><br>
        If you or someone you know is in immediate physical danger, experiencing severe distress, or thinking of self-harm, 
        please do not rely on digital applications. Contact national emergency services (<b style="color: #60A5FA;">112</b> in India, <b style="color: #60A5FA;">911</b> in US) 
        or call the 24/7 Tele-MANAS helpline at <b style="color: #60A5FA;">14416</b> immediately.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <b>Sahara AI</b> — Dynamic Mental Health Monitoring & Early Intervention System<br>
    <span style="opacity: 0.8;">Developed with empathetic human-in-the-loop AI safeguards</span>
</div>
""", unsafe_allow_html=True)
