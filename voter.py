import streamlit as st, mysql.connector, time, io
from PIL import Image

class Voting:
    def __init__(self):
        header_placeholder = st.empty()
        conn = mysql.connector.connect(host='localhost', user='root', password='1234')
        cursor = conn.cursor()
        cursor.execute("USE Student_Election;")
        cursor.execute("SELECT status FROM users WHERE user_id = %s", (st.session_state.user_id,))
        status = cursor.fetchone()[0]

        while True:
            cursor.execute("SELECT status FROM users WHERE user_id = %s", (st.session_state.user_id,))
            status = cursor.fetchone()[0]

            if status != 1:
                header_placeholder.empty()
                with header_placeholder.container():
                    st.header("❌ Voting Is Not Currently Available for this Device")
                time.sleep(2)
                st.rerun() 
                return
            else:
                break

        if st.session_state.pos_index == 0:
            header_placeholder.empty()
            with header_placeholder.container():
                st.header("✅ Voting has been Allowed")
                time.sleep(0.5)
            header_placeholder.empty()
        
        cursor.execute("SELECT DISTINCT Standing_For FROM candidates")
        result = cursor.fetchall()
        positions = []
        for i in result:
            positions.append(i[0])

        if "pos_index" not in st.session_state:
            st.session_state.pos_index = 0

        if st.session_state.pos_index >= len(positions):
            success_placeholder = st.empty()
            success_placeholder.empty()
            cursor.execute("SELECT voter_Adno FROM users WHERE user_id = %s", (st.session_state.user_id,))
            Adno = cursor.fetchone()[0]
            cursor.execute("UPDATE voters SET voting_status=1 WHERE barcode = %s", (Adno,))
            cursor.execute("UPDATE users SET status=0 WHERE user_id = %s", (st.session_state.user_id,))
            conn.commit()
            success_placeholder.success("✅ Your votes have been recorded. Thank you!")
            time.sleep(2)
            st.session_state.pos_index = 0

        current_position = positions[st.session_state.pos_index]
        form_placeholder = st.empty()
        error_placeholder = st.empty()

        with form_placeholder.form(f"form_{st.session_state.user_id}_{current_position}", clear_on_submit=True):
            st.subheader("Position: ", current_position)
            cursor.execute("SELECT Name, picture FROM candidates WHERE Standing_For = %s", (current_position,))
            candidates_data = cursor.fetchall()
            candidates = []
            images_bytes = []
            for candidate_row in candidates_data:
                candidates.append(candidate_row[0])
                images_bytes.append(candidate_row[1])
            cols = st.columns(len(candidates))
            for i in range(len(candidates)):
                if images_bytes[i] is not None:
                    image = Image.open(io.BytesIO(images_bytes[i]))
                    with cols[i]:
                        st.image(image, use_container_width=True)
                        st.caption(candidates[i])

            selected_candidate = st.radio("Select your candidate for "+current_position, candidates, index=None)
            submitted = st.form_submit_button("Submit")

        if submitted:
            if selected_candidate:
                cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE Name = %s AND Standing_For = %s", (selected_candidate, current_position))
                conn.commit()
                st.session_state.pos_index += 1
                form_placeholder.empty()
                st.rerun()
            else:
                with error_placeholder.container():
                    st.error("⚠️ Please select a candidate before submitting.")
