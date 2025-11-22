import streamlit as st, mysql.connector, time, pandas as pd, plotly.express as px, io, base64
from streamlit_option_menu import option_menu
from fpdf import FPDF

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
            st.session_state.positions.append(newposition)
            st.rerun()
        else:
            st.error("Please Enter The New Position")
            
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

def Voting():
    conn = mysql.connector.connect(host = 'localhost', user = 'root', password = '1234', database = 'student_election')
    cursor = conn.cursor()
    st.subheader("Voting")
    Voting_Form = st.form("Voting Form", True)
    with Voting_Form:
        users = []
        Adno = st.text_input("Click in to this and scan barcode on ID Card")
        cursor.execute("SELECT user_id FROM users;")
        result = cursor.fetchall()
        if result is not None:
            for user in result:
                users.append(user[0])
        user_id = st.selectbox("Enter the user ID of the target PC", users, index = None)
        cols = st.columns(5)
        with cols[2]:
            global submit
            submit = st.form_submit_button()
        if submit:
            if user_id is not None and Adno is not None:
                cursor.execute("SELECT voting_status FROM voters WHERE barcode = %s", (Adno, ))
                result = cursor.fetchone()[0]
                if result != 1:
                    cursor.execute("UPDATE users SET status = 1, voter_adno = %s WHERE user_id = %s", (Adno, user_id))
                    conn.commit()
                    st.success("Successfully gave permission to user ID "+str(user_id))
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("This Student Has Already Voted!")
                    return
            else:
                st.error("Please Fill All Fields!")
                return

def c_management():
    conn = mysql.connector.connect(host='localhost', user='root', passwd='1234', database='student_election')
    cursor = conn.cursor()
    
    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False
    if "position_value" not in st.session_state:
        st.session_state.position_value = None
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "confirm_truncate" not in st.session_state:
        st.session_state.confirm_truncate = False
    if "show_truncate_dialog" not in st.session_state:
        st.session_state.show_truncate_dialog = False
    cursor.execute("SELECT DISTINCT Position FROM candidates;")
    result = cursor.fetchall()
    if "positions" not in st.session_state:
        st.session_state.positions = []
    for pos in result:
        if pos[0] not in st.session_state.positions:
            st.session_state.positions.append(pos[0])

    st.header("Registering A New Candidate")

    positions = st.session_state.positions

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

    if st.session_state.show_modal:
        add_new_position_dialog()

    if (st.session_state.position_value and st.session_state.form_submitted and not st.session_state.show_modal):
        if Adno and Name and Symbol and picture_files:
            cursor.execute("SELECT Adno FROM candidates WHERE Adno = %s", (Adno,))
            exists = cursor.fetchone()
            if exists is None:
                picture_bytes = picture_files.read()
                cursor.execute("INSERT INTO candidates(Adno, Name, Symbol, Position, picture) VALUES (%s, %s, %s, %s, %s);", (Adno, Name, Symbol, st.session_state.position_value, picture_bytes))
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
                
    st.header("Truncating Candidates(For New Election)")
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
        
def v_management():
    conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
    cursor = conn.cursor()
    submit, submit_1, submit_2, submit_3 = 0, 0, 0, 0
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
        submit_1 = st.button("Submit")
    if submit_1:
        if Adno != '':
            cursor.execute("UPDATE voters SET voting_status = 1 WHERE barcode = %s;", (Adno,))
            with success_placeholder_1.container():
                st.success("Voter's Permission Successfully Reinstated")
                time.sleep(1)
            success_placeholder_1=st.empty()
        else:
            st.error("Please Fill All Fields Before Submitting")
                
    st.header("Registering A Voter Individually")
    with st.form(key = "form_individual_register"):
        Adno = st.text_input("Enter The Admission Number of The Student: ")
        Name = st.text_input("Enter The Name of the Student: ")
        with st.columns(5)[2]:
            submit_2 = st.form_submit_button("Submit")
    if submit_2:
        if Adno and Name:
            cursor.execute("SELECT * FROM voters;")
            result = cursor.fetchall()
            Adnos, Names = [], []
            for i in result:
                Adnos.append(i[0])
                Names.append(i[1])
            if Adno not in Adnos:
                cursor.execute("INSERT INTO voters(barcode, Name) VALUES(%s, %s);", (Adno, Name))
                conn.commit()
                success_placeholder_2 = st.empty()
                success_placeholder_2.success("The Voter Has Successfully Registered")
                time.sleep(2)
                success_placeholder_2.empty()
            else:
                st.error("This Voter Has Already Registered By The Name of "+Names[Adnos.index(Adno)])
        else:
            st.error("Please Fill All Fields Before Submitting")
        
    st.header("Deleting A Voter")
    Adno = st.text_input("Enter Admission Number of the Voter to be Deleted:")
    with st.columns(5)[2]:
        submit_3 = st.button("Submit", key = "submit3")
    if submit_3:
        if Adno is not None:
            cursor.execute("DELETE FROM voters WHERE barcode = %s", (Adno,))
            conn.commit()
            success_placeholder_3 = st.empty()
            with success_placeholder_3.container():
                st.success("Successfully Deleted The Voter")
                time.sleep(1.5)
            success_placeholder_3.empty()
        else:
            st.error("Please Fill The Field")
            
def live_results():
    st.header("Live Voting Results")
    conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Position FROM candidates;")
    result = cursor.fetchall()
    positions = []
    for i in result:
        positions.append(i[0])
    cols = st.columns(2)
    palette = ["#B22222", "#00008B", "#00FFFF", "#DE143C", "#FF0000", "#EC4426"]
    for pos in positions:
        if (positions.index(pos)+1)%2 == 1:
            with cols[0]:
                cursor.execute("SELECT Name, votes FROM candidates WHERE Position = %s", (pos,))
                candidates = cursor.fetchall()
                fig = px.bar(candidates, x = 0, y = 1, color = 0, text = 1, color_discrete_sequence=palette)
                fig.update_layout(title = "Votes for "+pos, xaxis_title = 'Candidates', yaxis_title = "Vote Count", uniformtext_minsize = 8, uniformtext_mode="hide")
                st.plotly_chart(fig, use_container_width = True)
        if (positions.index(pos)+1)%2 == 0:
            with cols[1]:
                cursor.execute("SELECT Name, votes FROM candidates WHERE Position = %s", (pos,))
                candidates = cursor.fetchall()
                fig = px.bar(candidates, x = 0, y = 1, color = 0, text = 1, color_discrete_sequence=palette)
                fig.update_layout(title = "Votes for "+pos, xaxis_title = 'Candidates', yaxis_title = "Vote Count", uniformtext_minsize = 8, uniformtext_mode="hide")
                st.plotly_chart(fig, use_container_width = True)
    time.sleep(2)
    st.rerun()
    
def report_gen():
    st.header("Report Generation")
    conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
    cursor = conn.cursor()
    info_placeholder = st.empty()
    with info_placeholder.container():
        st.info("Please Wait. Generating Report...")
    cursor.execute("SELECT DISTINCT Position FROM candidates;")
    result = cursor.fetchall()
    all_candidates = []
    positions = []
    for i in result:
        positions.append(i[0])
    for pos in positions:
        cursor.execute("SELECT Name, Votes FROM candidates WHERE Position = %s", (pos,))
        candidates = cursor.fetchall()
        if candidates:
            votes = []
            for i in candidates:
                if i[1] not in votes:
                    votes.append(i[1])
            votes.sort(reverse = True)
            for name, vote in candidates:
                result = votes.index(vote)+1
                all_candidates.append([name, pos, vote, result])
        
    cursor.execute("SELECT COUNT(*) FROM voters WHERE voting_status = 1;")
    voted_voters = cursor.fetchall()[0][0]
    if voted_voters!=0:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("ArialUnicode", "", "C:\\Windows\\Fonts\\arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "B", "C:\\Windows\\Fonts\\arialbd.ttf", uni=True)
        pdf.add_font("Emoji", "", "C:\\Windows\\Fonts\\seguiemj.ttf", uni=True)
        pdf.set_font("ArialUnicode", "B", 18)
        pdf.cell(w = 200, h = 12, txt = "School Election - "+str(time.localtime()[0])+" - Result", ln = True, align = 'C')
        pdf.ln(10)
        pdf.cell(w = 0, h = 12, txt = "1. Election Overview", ln = True, align = 'L')
        pdf.set_font("ArialUnicode", "", 18)
        pdf_positions = "Positions: "
        for pos in positions:
            pdf_positions = pdf_positions + pos + ", "
        pdf_positions = pdf_positions[:-2]
        pdf.cell(w = 0, h = 8, txt = "•"+pdf_positions, ln = True, align = "L")
        cursor.execute("SELECT COUNT(*) FROM voters;")
        total_voters = cursor.fetchall()[0][0]
        voted_percent = round((voted_voters/total_voters)*100, 1)
        pdf.cell(w = 0, h = 8, txt = "•Total Eligible Voters: "+str(total_voters), ln = True, align = "L")
        pdf.cell(w = 0, h = 8, txt = "•Total Votes Casted: "+str(voted_voters), ln = True, align = "L")
        pdf.cell(w = 0, h = 8, txt = "•Voter Turnout: "+str(voted_percent), ln = True, align = "L")
        pdf.ln(5)
        pdf.set_font("ArialUnicode", "B", 18)
        pdf.cell(w = 0, h = 12, txt = "2. Results By Position", ln = True, align = 'L')
        pdf.set_font("ArialUnicode", "", 18)
        for pos in positions:
            pdf.cell(w = 0, h = 12, txt = pos, ln = True, align = 'L')
            pos_candidates = []
            for cand in all_candidates:
                if cand[1] == pos:
                    pos_candidates.append(cand)
            pos_candidates.sort(key=lambda x: x[3])
            total_votes_pos = 0
            for i in pos_candidates:
                total_votes_pos += i[2]
            for i in pos_candidates:
                if i[3] == 1:
                    pdf.cell(w = pdf.get_string_width("•"+str(i[0])+" - "+str(i[2])+"("+str(round((i[2]/total_votes_pos)*100, 1))+')'), h = 8, txt = "•"+str(i[0])+" - "+str(i[2])+"("+str(round((i[2]/total_votes_pos)*100, 1))+')', ln = False, align = "L")
                    pdf.set_font("Emoji", "", 18)
                    pdf.cell(w = pdf.get_string_width("   ✅"), h = 8, txt = "   ✅", ln = False, align="L")
                    pdf.set_font("ArialUnicode", "", 18)
                    pdf.cell(w = 0, h = 8, txt = 'Winner', ln = True, align = "L")
                else:
                    pdf.cell(w = 0, h = 8, txt = "•"+str(i[0])+" - "+str(i[2])+"("+str(round((i[2]/total_votes_pos)*100, 1))+")", ln = True, align = "L")
            pdf.ln(3)
        pdf.ln(5)
        pdf.set_font("ArialUnicode", "B", 18)
        pdf.cell(w = 0, h = 12, txt = "3. Summary", ln = True, align = 'L')
        pdf.set_font("ArialUnicode", "", 18)
        for pos in positions:
            text = "•"+pos+" - "
            pos_candidates = []
            for cand in all_candidates:
                if cand[1] == pos:
                    pos_candidates.append(cand)
            for i in pos_candidates:
                if i[3] == 1:
                    text = text + i[0]
                    break
            pdf.cell(w = 0, h = 8, txt = text, ln = True, align = "L")
        
        pdf_bytes = pdf.output(dest='S')
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        pdf_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        info_placeholder.empty()
        
        report_name = "Election Report - "+str(time.localtime()[0])
        st.download_button(label = "Download Report As A PDF", data = buffer, file_name = report_name+".pdf", mime="application/pdf")
            
        st.markdown('<iframe src="data:application/pdf;base64,' + pdf_base64 + '" width="700" height="900" type="application/pdf" title="' + report_name + '"></iframe>', unsafe_allow_html=True)
    else:
        info_placeholder.empty()
        st.error("No Votes Have Been Casted Yet")

def Admin_Powers():
    st.header("Admin Panel")
    main_placeholder = st.empty()
    with st.sidebar:
        selected = option_menu("Main Menu", ["🗳️ Voting", "🧾 Candidate Management", "🆔 Voter Management", "📊 Live Results", "📑 Report Generation"], default_index=0)
        
    main_placeholder.empty()
    with main_placeholder.container():
        if selected == '🗳️ Voting':
            Voting()
        elif selected == '🧾 Candidate Management':
            c_management()
        elif selected == '🆔 Voter Management':
            v_management()
        elif selected == '📊 Live Results':
            live_results()
        elif selected == '📑 Report Generation':
            report_gen()