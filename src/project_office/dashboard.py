import streamlit as st

from project_office.engine import demo_office

st.set_page_config(page_title="Agentic AI Project Office", layout="wide")
if "office" not in st.session_state:
    st.session_state.office = demo_office()
office = st.session_state.office
report = office.executive_report()
st.title("Agentic AI Project Office")
st.caption("Agents recommend. Humans approve. Every transition is auditable.")
c1, c2 = st.columns(2)
c1.metric("Portfolio initiatives", report["portfolio_size"])
c2.metric("Audit chain", "VALID" if report["audit_chain_valid"] else "BROKEN")
st.dataframe(report["ranked_priorities"], use_container_width=True)
initiative_id = st.selectbox("Initiative", list(office.initiatives))
if st.button("Run analysis agents"):
    st.json(office.analyze(initiative_id))
st.subheader("Management brief")
st.write(office.executive_report()["management_message"])
st.subheader("Audit events")
st.dataframe(office.audit, use_container_width=True)

