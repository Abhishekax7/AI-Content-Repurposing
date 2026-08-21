"""
app.py
------
AI Content Repurposing & Marketing Automation
Main Streamlit entry point. Run with: streamlit run app.py

This file is deliberately thin — it only handles UI and wiring together
the other modules. All real logic (validation, prompts, AI calls, parsing,
logging) lives in its own file.
"""

import streamlit as st
from validators import validate_content, validate_required_fields
from prompts import build_repurposing_prompt
from ai_engine import generate_json_content, AIEngineError
from output_parser import parse_and_validate, OutputParsingError
from logger import log_generation, update_approval_status, get_all_logs

st.set_page_config(
    page_title="AI Content Repurposing & Marketing Automation",
    page_icon="🔁",
    layout="wide",
)

if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_log_id" not in st.session_state:
    st.session_state.current_log_id = None
if "approval_message" not in st.session_state:
    st.session_state.approval_message = None
if  st.session_state.approval_message:
    st.success(st.session_state.approval_message)
    st.session_state.approval_message = None
# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ About")
    st.caption(
        "Paste one long-form piece of content and get back a full set of "
        "ready-to-use marketing assets, generated in a single structured "
        "AI call and logged locally with an approval workflow."
    )
    st.divider()
    st.markdown("### Generation Log")
    logs = get_all_logs()
    st.caption(f"{len(logs)} generation(s) logged so far.")
    if logs:
        with st.expander("View recent log entries"):
            for entry in logs[:10]:
                st.markdown(
                    f"**{entry['brand']}** — {entry['source_type']} "
                    f"— _{entry['approval_status']}_"
                )
                st.caption(entry["timestamp"])
                st.divider()

# ---------- Header ----------
st.title("🔁 AI Content Repurposing & Marketing Automation")
st.markdown(
    "Turn one article, blog post, or brief into a LinkedIn post, video "
    "script, campaign ideas, hooks, CTAs, and email subject lines."
)

# ---------- Input form ----------
with st.form("repurpose_form"):
    content = st.text_area(
        "Paste your long-form content here",
        height=250,
        placeholder="Paste an article, blog post, product brief, or campaign brief (200+ characters)...",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        source_type = st.selectbox(
            "Source type",
            ["Blog post", "Article", "Product brief", "Campaign brief", "Press release"],
        )
        brand = st.text_input("Brand name", placeholder="e.g. Doctors Choice")
    with col2:
        audience = st.text_input("Target audience", placeholder="e.g. small business owners")
        tone = st.selectbox(
            "Tone",
            ["Friendly & warm", "Bold & energetic", "Professional", "Witty & playful", "Luxury & premium"],
        )
    with col3:
        extra = st.text_area("Extra instructions (optional)", height=100, placeholder="Any specific angle or constraint")

    submitted = st.form_submit_button("🔁 Repurpose Content", use_container_width=True)

# ---------- Generate ----------
if submitted:
    content_valid, content_error = validate_content(content)
    fields_valid, fields_error = validate_required_fields(brand, audience)

    if not content_valid:
        st.warning(content_error)
    elif not fields_valid:
        st.warning(fields_error)
    else:
        with st.spinner("Repurposing your content into marketing assets..."):
            try:
                system_prompt, user_prompt = build_repurposing_prompt(
                    content, source_type, brand, audience, tone, extra
                )
                raw_response = generate_json_content(system_prompt, user_prompt)
                parsed = parse_and_validate(raw_response)

                log_id = log_generation(
                    brand=brand,
                    audience=audience,
                    source_type=source_type,
                    outputs=parsed,
                    approval_status="pending",
                )
                st.session_state.current_result = parsed
                st.session_state.current_log_id = log_id

            except AIEngineError as e:
                st.error(f"AI error: {e}")
            except OutputParsingError as e:
                st.error(f"Output error: {e}")

# ---------- Output ----------
if st.session_state.current_result:
    result = st.session_state.current_result
    st.divider()
    st.subheader("Generated Marketing Assets")

    with st.container(border=True):
        st.markdown("#### 📝 Summary")
        st.write(result["summary"])

    with st.container(border=True):
        st.markdown("#### 💼 LinkedIn Post")
        st.write(result["linkedin_post"])

    with st.container(border=True):
        st.markdown("#### 🎬 Short Video / Reel Script")
        script = result["short_video_script"]
        st.markdown(f"**Hook:** {script['hook']}")
        st.markdown(f"**Body:** {script['body']}")
        st.markdown(f"**CTA:** {script['cta']}")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### 💡 Campaign Ideas")
            for idea in result["campaign_ideas"]:
                st.markdown(f"- {idea}")

        with st.container(border=True):
            st.markdown("#### 🎣 Hooks")
            for hook in result["hooks"]:
                st.markdown(f"- {hook}")

    with col_b:
        with st.container(border=True):
            st.markdown("#### 📣 CTA Options")
            for cta in result["cta_options"]:
                st.markdown(f"- {cta}")

        with st.container(border=True):
            st.markdown("#### ✉️ Email Subject Lines")
            for subject in result["email_subject_lines"]:
                st.markdown(f"- {subject}")

    # ---------- Approval workflow ----------
    st.divider()
    st.markdown("#### Review this generation")
    notes = st.text_area("Revision notes (optional)", key="revision_notes")
    col_approve, col_reject = st.columns(2)
    with col_approve:
    if st.button("✅ Approve", use_container_width=True):
        update_approval_status(
            st.session_state.current_log_id,
            "approved",
            notes
        )
        st.session_state.approval_message = "Marked as approved and logged."
        st.rerun()

with col_reject:
    if st.button("❌ Reject", use_container_width=True):
        update_approval_status(
            st.session_state.current_log_id,
            "rejected",
            notes
        )
        st.session_state.approval_message = "Marked as rejected and logged."
        st.rerun()
