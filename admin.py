import streamlit as st, voting, candidate, voters, results, report
from streamlit_option_menu import option_menu

class Admin_Powers:
    def __init__(self):
        st.header("Admin Panel")
        
        with st.sidebar:
            selected = option_menu("Main Menu", ["🗳️ Voting", "🧾 Candidate Management", "🆔 Voter Management", "📊 Live Results", "📑 Report Generation"], default_index=0)
            
        if selected == '🗳️ Voting':
            voter = voting.Voting()
        elif selected == '🧾 Candidate Management':
            voter = candidate.c_management()
        elif selected == '🆔 Voter Management':
            voter = voters.v_management()
        elif selected == '📊 Live Results':
            voter = results.live_results()
        elif selected == '📑 Report Generation':
            voter = report.report_gen()