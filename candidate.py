import streamlit as st, mysql.connector, time

class c_management:
    def __init__(self):
        if "show_modal" not in st.session_state:
            st.session_state.show_modal = False
        if "position_value" not in st.session_state:
            st.session_state.position_value = None
        if "form_submitted" not in st.session_state:
            st.session_state.form_submitted = False

        st.header("Registering A New Candidate")

        conn = mysql.connector.connect(host='localhost', user='root', passwd='1234', database='student_election')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Standing_For FROM candidates;")
        result = cursor.fetchall()

        positions = []
        if result is not None:
            for pos in result:
                positions.append(pos[0])

        form = st.form("Registering Candidate", clear_on_submit=True)
        with form:
            Adno = st.text_input("Please Enter The Candidate's Admission Number:")
            Name = st.text_input("Please Enter The Candidate's Name:")
            Symbol = st.text_input("Please Enter The Symbol Of The Candidate:")
            position = st.selectbox("Please Select The Candidate's Position:", positions + ["Add New Position(A Pop Up will be displayed later)"], index=None)
            picture_files = st.file_uploader("Please Input An Image Of The Candidate:", type=["jpg", "jpeg", "png", "webp"])
            with st.columns(5)[2]:
                submit = st.form_submit_button("Submit")

        if submit:
            st.session_state.form_submitted = True
            if position == "Add New Position(A Pop Up will be displayed later)":
                st.session_state.show_modal = True
            else:
                st.session_state.position_value = position

        @st.dialog("Enter New Position")
        def add_new_position_dialog():
            newposition = st.text_input("Enter The New Position", key="new_pos_input")
            col1, col2, col3 = st.columns(3)
            with col2:
                modal_submit = st.button("Submit")
            if modal_submit:
                if newposition.strip():
                    st.session_state.position_value = newposition
                    st.session_state.show_modal = False
                    st.rerun()
                else:
                    st.error("Please Enter The New Position")

        if st.session_state.show_modal:
            add_new_position_dialog()

        if (st.session_state.position_value and st.session_state.form_submitted and not st.session_state.show_modal):
            if Adno and Name and Symbol and picture_files:
                cursor.execute("SELECT Adno FROM candidates WHERE Adno = %s", (Adno,))
                exists = cursor.fetchone()
                if exists is None:
                    picture_bytes = picture_files.read()
                    cursor.execute("INSERT INTO candidates(Adno, Name, Symbol, Standing_For, picture) VALUES (%s, %s, %s, %s, %s);", (Adno, Name, Symbol, st.session_state.position_value, picture_bytes))
                    conn.commit()
                    success_placeholder = st.empty()
                    success_placeholder.success("Successfully Entered The Candidate")
                    time.sleep(2)
                    success_placeholder.empty()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("This Candidate's Record Already Exists!")
            else:
                st.error("Please Fill All The Fields")
                
        st.header("Deleting A Candidate")
        Adno = st.text_input("Enter Admission Number of Candidate to be Deleted: ")
        with st.columns(5)[2]:
            submit1 = st.button("Submit", key = 'submit1')
        if submit1:
            if Adno:
                cursor.execute("SELECT Adno FROM candidates;")
                result = cursor.fetchall()
                Adnos = []
                for i in result:
                    Adnos.append(i[0])
                if Adno in Adnos:
                    cursor.execute("DELETE FROM candidates WHERE Adno = %s;", (Adno, ))
                    conn.commit()
                    success_placeholder_1 = st.empty()
                    success_placeholder_1.success("Candidate Successfully Deleted")
                    time.sleep(2)
                    success_placeholder_1.empty()
                else:
                    st.error("This Candidate Does Not Exist")
            else:
                st.error("Please Fill All Fields Before Submitting")
                
        @st.dialog("Truncate")
        def sure_to_truncate():
            st.write("Are You Sure To Truncate Candidates? (This Will Delete Data Of All Candidates And Their Votes For The Last Election Conducted)") 
            c1, c2, c3, c4, c5 = st.columns(5)
            with c2:
                Yes = st.button("Yes", key = "yes")
            with c4:
                No = st.button("No", key = "no")
            if Yes:
                st.session_state.confirm_truncate = True
                st.session_state.show_truncate_dialog = False
                st.rerun()
            if No:
                st.session_state.confirm_truncate = False
                st.session_state.show_truncate_dialog = False
                st.rerun()
                
        st.header("Truncating Candidates(For New Election)")
        if "confirm_truncate" not in st.session_state:
            st.session_state.confirm_truncate = False
        if "show_truncate_dialog" not in st.session_state:
            st.session_state.show_truncate_dialog = False
        with st.columns(5)[2]:
            truncate = st.button("Truncate", key = 'truncate')
        if truncate:
            st.session_state.show_truncate_dialog = True
        if st.session_state.show_truncate_dialog:
            sure_to_truncate()
        if st.session_state.confirm_truncate:
            cursor.execute("TRUNCATE candidates;")
            conn.commit()
            success_placeholder_2 = st.empty()
            success_placeholder_2.success("Candidates Successfully Truncated")
            time.sleep(2)
            success_placeholder_2.empty()
            st.session_state.confirm_truncate = False
            st.rerun()