import streamlit as st, pandas as pd, mysql.connector, time

class register_v:
    def __init__(self):
        conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
        cursor = conn.cursor()
        submit, submit_1, submit_3 = 0, 0, 0
        success_placeholder, info_placeholder = st.empty(), st.empty()
        st.header('Register Voter')
        csv_file = st.file_uploader("Please Enter The CSV File of The Voter's List ([Name, Adno])", type = ["csv"])
        with st.columns(5)[2]:
            submit = st.button("Submit", key = "submit")
        if submit:
            if csv_file is not None:
                with info_placeholder.container():
                    st.info("Please Wait While The File Is Being Processed")
                voters = pd.read_csv(csv_file)
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
                info_placeholder.empty()
                with success_placeholder.container():
                    st.success('File Successfully Processed')
                    time.sleep(1.5)
                success_placeholder.empty()
                st.rerun()
            else:
                st.error("Please Enter The CSV File Before Submitting")
        success_placeholder_1 = st.empty()      
          
        st.header("Reinstate Voter Permission")
        Adno = st.text_input("Enter The Admission Number of the Voter whose Permission is to be Reinstated")
        with st.columns(5)[2]:
            submit_1 = st.button("Submit", key = 'submit1')
        if submit_1:
            if Adno != '':
                cursor.execute("UPDATE voters SET voting_status = 1 WHERE barcode = %s;", (Adno,))
                with success_placeholder_1.container():
                    st.success("Voter's Permission Successfully Reinstated")
                    time.sleep(1)
                success_placeholder_1=st.empty()
            else:
                st.error("Please Fill All Fields Before Submitting")
                    
        success_placeholder_2 = st.empty()
        st.header("Deleting A Voter")
        Adno = st.text_input("Enter Admission Number of the Voter to be Deleted:")
        with st.columns(5)[2]:
            submit_3 = st.button("Submit", key = "submit3")
        if submit_3:
            if Adno is not None:
                cursor.execute("DELETE FROM voters WHERE barcode = %s", (Adno,))
                conn.commit()
                with success_placeholder_2.container():
                    st.success("Successfully Deleted The Voter")
                    time.sleep(1.5)
                success_placeholder_2.empty()
            else:
                st.error("Please Fill The Field")