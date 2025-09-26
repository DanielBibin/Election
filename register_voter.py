import streamlit as st, pandas as pd, mysql.connector

class register_v:
    def __init__(self):
        submit = 0
        st.header('Register Voter')
        csv_file = st.file_uploader("Please Enter The CSV File of The Voter's List ([Name, Adno])", type = ["csv"])
        with st.columns(5)[2]:
            submit = st.button("Submit")
        if submit:
            if csv_file is not None:
                voters = pd.read_csv(csv_file)
                conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
                cursor = conn.cursor()
                cursor.execute("SELECT barcode FROM voters;")
                result = cursor.fetchall()
                Adno = []
                for i in result:
                    Adno.append(i[0])
                for row_no, voter in voters.iterrows():
                    if tuple(voter)[1] == 'Name':
                        break
                    if tuple(voter)[1] not in Adno:
                        cursor.execute("INSERT INTO voters(Name, barcode) VALUES(%s, %s)", tuple(voter))
                conn.commit()
            else:
                st.error("Please Enter The CSV File Before Submitting")