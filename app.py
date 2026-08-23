import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION & GLOBAL CSS
# ============================================================

st.set_page_config(
    page_title="Sahaara AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme matching the design
st.markdown("""
<style>
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
    st.session_state.nav_page = "🏠 Home"
if "latest_assessment_result" not in st.session_state:
    st.session_state.latest_assessment_result = None
if "assessment_step" not in st.session_state:
    st.session_state.assessment_step = 1
if "step_error" not in st.session_state:
    st.session_state.step_error = None
if "assessment_form" not in st.session_state:
    st.session_state.assessment_form = {
        "consent": False,
        "sleep": None, "appetite": None, "energy": None,
        "mood": None, "anxiety": None, "focus": None,
        "isolation": None, "support": None, "hope": None
    }

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 30px;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E2E8F0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 12px;">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span style="font-size: 22px; font-weight: bold; color: #fff;">Sahaara AI</span>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🧠 AI Assessment",
            "📈 Wellbeing Trend",
            "🛣️ Case Journey",
            "👥 Professional Connect",
            "🗂️ Counsellor Dashboard",
            "🛡️ Resilience Support",
            "🔒 Privacy & Safety"
        ],
        label_visibility="collapsed",
        key="nav_page"
    )
    
    st.markdown("""
        <div class="sidebar-disclaimer">
            Prototype only – AI output should always be reviewed by an appropriately qualified human professional.
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# HOME PAGE (REDESIGN)
# ============================================================
if page == "🏠 Home":
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
    st.markdown("""
        <div style="background-color: #12131A; padding: 20px; border-radius: 12px; border: 1px solid #1E1F2A; text-align: center;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; position: relative;">
                <div style="position: absolute; top: 20px; left: 10%; right: 10%; height: 2px; background-color: #2762A8; z-index: 1;"></div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">👤</div>
                    <div style="font-size: 12px; color: #CBD5E1;">User<br>Check-in</div>
                </div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">🧠</div>
                    <div style="font-size: 12px; color: #CBD5E1;">AI-assisted<br>Assessment</div>
                </div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">🎯</div>
                    <div style="font-size: 12px; color: #CBD5E1;">Dynamic<br>Distress Score</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 40px; position: relative;">
                <div style="position: absolute; top: 20px; left: 25%; right: 25%; height: 2px; background-color: #2762A8; z-index: 1;"></div>
                <div style="z-index: 2; width: 33%;"></div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">📈</div>
                    <div style="font-size: 12px; color: #CBD5E1;">Trend<br>Detection</div>
                </div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">⚠️</div>
                    <div style="font-size: 12px; color: #CBD5E1;">Early<br>Warning</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-around; align-items: center; position: relative;">
                <div style="position: absolute; top: 20px; left: 25%; right: 25%; height: 2px; background-color: #2762A8; z-index: 1;"></div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">👥</div>
                    <div style="font-size: 12px; color: #CBD5E1;">Human<br>Professional<br>Review</div>
                </div>
                <div style="z-index: 2; width: 33%;">
                    <div style="font-size: 24px; margin-bottom: 8px;">📞</div>
                    <div style="font-size: 12px; color: #CBD5E1;">Support &<br>Follow-up</div>
                </div>
                <div style="z-index: 2; width: 33%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
elif page == "🧠 AI Assessment":

    # --- RESULT VIEW IF ALREADY ANALYZED ---
    if st.session_state.latest_assessment_result is not None:
        res = st.session_state.latest_assessment_result

        # Top Header
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <h1 style="margin: 0; color: #1e293b;">📊 Assessment Insights & Care Plan</h1>
                <p style="color: #64748b; margin: 4px 0 0 0;">Comprehensive wellbeing evaluation generated by Sahaara AI</p>
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
            st.metric("Journey Context", res['stage'] if len(res['stage']) < 22 else res['stage'][:20] + "...")

        # Visual Progress Bar
        st.caption("Distress Spectrum Indicator:")
        st.progress(res['distress_score'] / 100)

        st.divider()

        # Identified Factors & Qualitative Analysis
        col_f1, col_f2 = st.columns([1, 1])

        with col_f1:
            st.markdown("### 🔎 Key Focus Factors")
            if res["factors"]:
                factor_html = "".join([f'<span class="factor-tag">⚠️ {f}</span>' for f in res["factors"]])
                st.markdown(f"<div style='margin-bottom: 15px;'>{factor_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown('<span class="factor-tag-green">✅ No acute distress factors identified</span>', unsafe_allow_html=True)

            if res.get("protective_factors"):
                st.markdown("#### 🛡️ Protective Factors Present")
                prot_html = "".join([f'<span class="factor-tag-green">🛡️ {pf}</span>' for pf in res["protective_factors"]])
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
                    📞 Tele-MANAS (Govt of India): <b>14416</b> / <b>1800-891-4416</b> (24x7 Free)<br>
                    📞 Vandrevala Foundation: <b>+91 9999 666 555</b><br>
                    📞 KIRAN Mental Health Helpline: <b>1800-599-0019</b>
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
                    "Welcome to Sahaara AI. This multi-factor tool evaluates self-reported emotional wellbeing, "
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
                    <h3 style="margin: 8px 0 0 0; color: #1e293b;">{step_names[step-1]}</h3>
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

elif page == "📈 Wellbeing Trend":
    st.title("📈 Longitudinal Wellbeing Trend")
    st.write("Monitor how distress and resilience markers evolve over time.")

    history = st.session_state.assessment_history

    if not history:
        st.info("No assessment history recorded yet. Complete your first assessment to begin tracking.")
    else:
        df = pd.DataFrame(history)
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
            x=alt.X("date:N", title="Check-in Date & Time", axis=alt.Axis(labelAngle=-25)),
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
            "sahaara_wellbeing_history.csv",
            "text/csv"
        )


# ============================================================
# CASE JOURNEY
# ============================================================

elif page == "🛣️ Case Journey":
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

elif page == "👥 Professional Connect":
    st.title("👩‍⚕️ Professional Care Network")
    st.info("Verified specialist directory for confidential mental health and trauma support.")

    providers = [
        ("Dr. Asha Mehta", "Senior Consultant Psychiatrist", "Online Tele-consult", "Available Today", "⭐⭐⭐⭐⭐"),
        ("Dr. Rahul Sharma", "Clinical Psychologist (Trauma Specialist)", "Online / In-person", "Next Available: Tomorrow", "⭐⭐⭐⭐⭐"),
        ("Dr. Neha Verma", "Licensed Psychotherapist & Counsellor", "Online Video Session", "Available Today", "⭐⭐⭐⭐½")
    ]

    for name, role, mode, availability, rating in providers:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.subheader(f"👩‍⚕️ {name}")
                st.write(f"**Specialty:** {role}")
                st.caption(f"Rating: {rating} • Verified Medical License")

            with col2:
                st.write(f"**Mode:** {mode}")
                st.write(f"**Status:** `{availability}`")

            with col3:
                if st.button("Request Consultation", key=name, type="primary"):
                    st.success(f"Appointment request submitted to {name}. Their care coordinator will contact you promptly.")

    st.divider()

    st.subheader("🤝 Designate a Trusted Support Contact")
    trusted_person = st.text_input("Contact Name (Friend, Family, or Mentor)")
    relationship = st.selectbox("Relationship", ["Family Member", "Close Friend", "Legal Advocate", "Other"])

    if st.button("Save Trusted Contact"):
        if trusted_person.strip():
            st.success(f"✅ {trusted_person} has been registered as your {relationship.lower()} emergency support contact.")
        else:
            st.warning("Please enter a valid contact name.")


# ============================================================
# COUNSELLOR DASHBOARD
# ============================================================

elif page == "🗂️ Counsellor Dashboard":
    st.title("📊 Authorized Clinical Review Dashboard")
    st.caption("Confidential decision-support overview for designated mental health officers and caseworkers.")

    history = st.session_state.assessment_history

    if not history:
        st.info("No assessment records found in the current session. Complete an assessment to generate analytics.")
    else:
        df = pd.DataFrame(history)
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        df = df.dropna(subset=["score"])

        latest_score = int(df.iloc[-1]["score"])
        high_count = len(df[df["level"] == "HIGH"])
        moderate_count = len(df[df["level"] == "MODERATE"])
        low_count = len(df[df["level"] == "LOW"])

        # Top Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Assessments", len(df))
        with col2:
            st.metric("🔴 High Priority", high_count)
        with col3:
            st.metric("🟡 Moderate Watch", moderate_count)
        with col4:
            st.metric("Latest Score", f"{latest_score}/100")

        st.divider()

        # Score Trend
        st.subheader("📈 Case Distress Trajectory (Scale 0 - 100)")
        df["Check-in"] = range(1, len(df) + 1)

        counsellor_base = alt.Chart(df).encode(
            x=alt.X("Check-in:O", title="Check-in Number"),
            y=alt.Y(
                "score:Q",
                title="Distress Score (0 - 100)",
                scale=alt.Scale(domain=[0, 100], clamp=True),
                axis=alt.Axis(values=[0, 20, 40, 60, 80, 100])
            ),
            tooltip=[
                alt.Tooltip("Check-in:O", title="Check-in #"),
                alt.Tooltip("date:N", title="Date"),
                alt.Tooltip("score:Q", title="Distress Score"),
                alt.Tooltip("level:N", title="Risk Level")
            ]
        )

        c_line = counsellor_base.mark_line(color="#dc2626", strokeWidth=3, interpolate="monotone")
        c_points = counsellor_base.mark_circle(size=75, color="#b91c1c")

        c_rule_low = alt.Chart(pd.DataFrame({"y": [35]})).mark_rule(color="#10b981", strokeDash=[4, 4], opacity=0.7).encode(y="y:Q")
        c_rule_high = alt.Chart(pd.DataFrame({"y": [65]})).mark_rule(color="#ef4444", strokeDash=[4, 4], opacity=0.7).encode(y="y:Q")

        c_chart = (c_line + c_points + c_rule_low + c_rule_high).properties(height=340)
        st.altair_chart(c_chart, use_container_width=True)

        # Current Status Callout
        latest_level = df.iloc[-1]["level"]
        st.subheader("🚦 Triage Recommendation")
        if latest_level == "HIGH":
            st.error("🔴 **HIGH DISTRESS PRIORITY** — Recommend immediate clinical outreach and safety review.")
        elif latest_level == "MODERATE":
            st.warning("🟡 **MODERATE CONCERN** — Schedule follow-up check-in within 48-72 hours.")
        else:
            st.success("🟢 **LOW CONCERN** — Continue periodic monitoring as part of routine care.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Detailed Triage Log")
        st.dataframe(
            df[["Check-in", "date", "score", "level", "stage"]],
            use_container_width=True
        )


# ============================================================
# RESILIENCE SUPPORT
# ============================================================

elif page == "🛡️ Resilience Support":
    st.title("🌍 Environmental & Crisis Stressor Logger")
    st.write("Account for external contextual factors (e.g. natural disasters, heatwaves, displacement) that compound personal distress.")

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

    severity = st.radio(
        "Impact intensity on daily life:",
        ["Low impact", "Moderate impact", "High / Displaced"],
        horizontal=True
    )

    if st.button("Evaluate Contextual Impact", type="primary"):
        if event == "No major event":
            st.success("✅ No external crisis factor reported.")
        else:
            st.warning(f"⚠️ Context registered: **{event}** ({severity})")
            if "High" in severity:
                st.error("🚨 Critical environmental stress factor. Prioritize immediate shelter, hydration, and safety needs before psychosocial check-ins.")
            else:
                st.info("ℹ️ External stress registered. Incorporate coping and community relief resources.")


# ============================================================
# PRIVACY & SAFETY
# ============================================================

elif page == "🔒 Privacy & Safety":
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
        please do not rely on digital applications. Contact national emergency services (<b>112</b> in India, <b>911</b> in US) 
        or call the 24/7 Tele-MANAS helpline at <b>14416</b> immediately.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <b>Sahaara AI</b> — Dynamic Mental Health Monitoring & Early Intervention System<br>
    <span style="opacity: 0.8;">Developed with empathetic human-in-the-loop AI safeguards</span>
</div>
""", unsafe_allow_html=True)
