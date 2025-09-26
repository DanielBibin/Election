import streamlit as st, mysql.connector, plotly.express as px

class live_results:
    def __init__(self):
        st.header("Live Voting Results")
        conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Standing_For FROM candidates;")
        result = cursor.fetchall()
        positions = []
        for i in result:
            positions.append(i[0])
        cols = st.columns(2)
        palette = ["#B22222", "#00008B", "#00FFFF", "#DC143C", "#FF0000", "#FF6347"]
        for pos in positions:
            if (positions.index(pos)+1)%2 == 1:
                with cols[0]:
                    cursor.execute("SELECT Name, votes FROM candidates WHERE Standing_For = %s", (pos,))
                    candidates = cursor.fetchall()
                    fig = px.bar(candidates, x = 0, y = 1, color = 0, text = 1, color_discrete_sequence=palette)
                    fig.update_layout(title = "Votes for "+pos, xaxis_title = 'Candidates', yaxis_title = "Vote Count", uniformtext_minsize = 8, uniformtext_mode="hide")
                    
                    st.plotly_chart(fig, use_container_width=True)
            if (positions.index(pos)+1)%2 == 0:
                with cols[1]:
                    cursor.execute("SELECT Name, votes FROM candidates WHERE Standing_For = %s", (pos,))
                    candidates = cursor.fetchall()
                    fig = px.bar(candidates, x = 0, y = 1, color = 0, text = 1, color_discrete_sequence=palette)
                    fig.update_layout(title = "Votes for "+pos, xaxis_title = 'Candidates', yaxis_title = "Vote Count", uniformtext_minsize = 8, uniformtext_mode="hide")
                    
                    st.plotly_chart(fig, use_container_width=True)