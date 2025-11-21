import streamlit as st, voting, candidate, voters, results, report
from streamlit_option_menu import option_menu

def Admin_Powers():
    st.header("Admin Panel")
    placeholder = st.empty()
    with st.sidebar:
        selected = option_menu("Main Menu", ["🗳️ Voting", "🧾 Candidate Management", "🆔 Voter Management", "📊 Live Results", "📑 Report Generation"], default_index=0)
        
    placeholder.empty()
    with placeholder.container():
        if selected == '🗳️ Voting':
            voting.Voting()
        elif selected == '🧾 Candidate Management':
            candidate.c_management()
        elif selected == '🆔 Voter Management':
            voters.v_management()
        elif selected == '📊 Live Results':
            results.live_results()
        elif selected == '📑 Report Generation':
            report.report_gen()