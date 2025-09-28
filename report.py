import streamlit as st, mysql.connector, io, base64, time
from fpdf import FPDF

class report_gen:
    def __init__(self):
        st.header("Report Generation")
        conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '1234', database = 'student_election')
        cursor = conn.cursor()
        info_placeholder = st.empty()
        with info_placeholder.container():
            st.info("Please Wait. Generating Report...")
        cursor.execute("SELECT DISTINCT Standing_For FROM candidates;")
        result = cursor.fetchall()
        all_candidates = []
        positions = []
        for i in result:
            positions.append(i[0])
        for pos in positions:
            cursor.execute("SELECT Name, Votes FROM candidates WHERE Standing_For = %s", (pos,))
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
        
        
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("ArialUnicode", "", "C:\\Windows\\Fonts\\arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "B", "C:\\Windows\\Fonts\\arialbd.ttf", uni=True)
        pdf.add_font("Emoji", "", "C:\\Windows\\Fonts\\seguiemj.ttf", uni=True)
        pdf.set_font("ArialUnicode", "B", 18)
        pdf.cell(w = 200, h = 12, txt = "School Election Result", ln = True, align = 'C')
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
        cursor.execute("SELECT COUNT(*) FROM voters WHERE voting_status = 1;")
        voted_voters = cursor.fetchall()[0][0]
        voted_percent = round((voted_voters/total_voters)*100, 1)
        pdf.cell(w = 0, h = 8, txt = "•Total Eligible Voters: "+str(total_voters), ln = True, align = "L")
        pdf.cell(w = 0, h = 8, txt = "•Total Votes Casted: "+str(voted_voters), ln = True, align = "L")
        pdf.cell(w = 0, h = 8, txt = "•Voter Turnout: "+str(voted_percent), ln = True, align = "L")
        pdf.ln(5)
        pdf.set_font("ArialUnicode", "B", 18)
        pdf.cell(w = 0, h = 12, txt = "2. Results By Position", ln = True, align = 'L')
        pdf.set_font("ArialUnicode", "", 18)
        print(all_candidates)
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