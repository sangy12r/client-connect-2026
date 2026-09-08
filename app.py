import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from database import get_connection, initialize_database, generate_rsvp_token, seed_demo_data

initialize_database()
seed_demo_data()

st.set_page_config(page_title="Client Connect 2026", page_icon="🔗", layout="wide")

EVENT_NAME = "Client Connect 2026"
EVENT_SUBTITLE = "Wilhelmsen Port Services, India · Client Networking Evening"
EVENT_DATE = "Friday, 23 October 2026"
EVENT_TIME = "6:00 PM onwards"
EVENT_VENUE = "To be announced"
RSVP_DEADLINE = "Friday, 16 October 2026"

st.markdown("""
<style>
.stApp{background:#f6f8fb}.block-container{max-width:1280px;padding-top:1.4rem}
#MainMenu,footer{visibility:hidden}
.app-header{background:linear-gradient(135deg,#0b4775,#0b6f9e);color:white;padding:25px 30px;border-radius:16px;margin-bottom:22px}
.app-header h1{margin:0;font-size:2rem}.app-header p{margin:6px 0 0;opacity:.92}
.metric-card{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:17px 18px;min-height:100px}
.metric-label{color:#667085;font-size:.74rem;font-weight:700;letter-spacing:.05em}
.metric-value{color:#0b4775;font-size:1.9rem;font-weight:750;margin-top:5px}
.section-title{color:#0b4775;font-size:1.18rem;font-weight:750;margin:8px 0 12px}
.info-card{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:20px}
.rsvp-wrap{max-width:760px;margin:30px auto}.rsvp-card{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:30px}
.rsvp-banner{background:linear-gradient(135deg,#0b4775,#0b6f9e);color:white;padding:30px;border-radius:18px 18px 0 0;text-align:center}
.rsvp-banner h1{margin:0;font-size:2rem}.rsvp-banner p{margin:7px 0 0;opacity:.92}
.client-name{color:#0b4775;font-size:1.45rem;font-weight:750}.client-company{color:#667085;margin-bottom:18px}
.event-box{background:#f5f8fc;border:1px solid #e5eaf0;border-radius:12px;padding:18px;margin:18px 0}
</style>
""", unsafe_allow_html=True)

rsvp_token = st.query_params.get("rsvp")
if rsvp_token:
    conn = get_connection()
    client = conn.execute("""SELECT id,company,contact_name,rsvp_status,rsvp_date
                             FROM clients WHERE rsvp_token=?""",(rsvp_token,)).fetchone()
    conn.close()
    if client is None:
        st.error("This RSVP link is invalid or no longer available.")
        st.stop()

    st.markdown(f"""<div class="rsvp-wrap">
    <div class="rsvp-banner"><h1>{EVENT_NAME}</h1><p>{EVENT_SUBTITLE}</p></div>
    <div class="rsvp-card">""", unsafe_allow_html=True)
    st.markdown(f'<div class="client-name">Dear {client["contact_name"]},</div><div class="client-company">{client["company"]}</div>', unsafe_allow_html=True)
    st.write("We are pleased to invite you to our Client Networking Evening.")
    st.markdown(f"""<div class="event-box"><b>Date</b><br>{EVENT_DATE}<br><br>
    <b>Time</b><br>{EVENT_TIME}<br><br><b>Venue</b><br>{EVENT_VENUE}<br><br>
    <b>RSVP by</b><br>{RSVP_DEADLINE}</div>""", unsafe_allow_html=True)
    st.markdown("### Will you be joining us?")
    current = client["rsvp_status"] or "Pending"
    if current == "Accepted": st.success("Your attendance is currently confirmed.")
    elif current == "Declined": st.warning("Your current response is marked as Declined.")
    default = 0 if current == "Accepted" else 1 if current == "Declined" else 0
    response = st.radio("Please select your response",["Accept","Decline"],index=default,horizontal=True)
    if st.button("Confirm RSVP",type="primary",use_container_width=True):
        conn=get_connection()
        conn.execute("UPDATE clients SET rsvp_status=?,rsvp_date=?,invitation_opened=1 WHERE id=?",
                     ("Accepted" if response=="Accept" else "Declined",datetime.now().isoformat(timespec="seconds"),client["id"]))
        conn.commit(); conn.close()
        st.success("Thank you. Your RSVP has been recorded successfully.")
    st.markdown("</div></div>",unsafe_allow_html=True)
    st.stop()

st.markdown(f'<div class="app-header"><h1>{EVENT_NAME}</h1><p>{EVENT_SUBTITLE}</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## Client Connect")
    st.caption("Event Management")
    page=st.radio("Navigation",["Dashboard","Clients","Invitations","RSVP Tracker","Follow-ups","Event Check-in","Reports"])
    st.divider(); st.caption("EVENT")
    st.write("23 October 2026"); st.write("6:00 PM onwards"); st.write("Venue: To be announced")
    st.caption("DEMO ENVIRONMENT"); st.write("Dummy client data only")

def scalar(sql):
    c=get_connection(); v=c.execute(sql).fetchone()[0]; c.close(); return v

if page=="Dashboard":
    st.markdown('<div class="section-title">Event Overview</div>',unsafe_allow_html=True)
    st.write("A single view of client invitations, RSVP status, follow-ups and event attendance.")
    total=scalar("SELECT COUNT(*) FROM clients"); sent=scalar("SELECT COUNT(*) FROM clients WHERE invitation_sent=1")
    accepted=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Accepted'")
    declined=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Declined'")
    pending=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Pending'")
    checked=scalar("SELECT COUNT(*) FROM clients WHERE checked_in=1")
    for col,(label,val) in zip(st.columns(6),[("CLIENTS",total),("SENT",sent),("ACCEPTED",accepted),("DECLINED",declined),("PENDING",pending),("CHECKED IN",checked)]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>',unsafe_allow_html=True)
    st.divider(); left,right=st.columns([1.15,1])
    with left:
        st.markdown('<div class="section-title">RSVP Progress</div>',unsafe_allow_html=True)
        st.progress(accepted/total if total else 0); st.write(f"{accepted} of {total} invited clients have confirmed.")
        st.dataframe(pd.DataFrame({"Status":["Accepted","Pending","Declined"],"Clients":[accepted,pending,declined]}),use_container_width=True,hide_index=True)
    with right:
        st.markdown('<div class="section-title">Event Details</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="info-card"><b>Date</b><br>{EVENT_DATE}<br><br><b>Time</b><br>{EVENT_TIME}<br><br><b>Venue</b><br>{EVENT_VENUE}<br><br><b>RSVP Deadline</b><br>{RSVP_DEADLINE}</div>',unsafe_allow_html=True)

elif page=="Clients":
    st.markdown('<div class="section-title">Client Database</div>',unsafe_allow_html=True)
    st.write("Maintain the invitation master list and review current RSVP status.")
    uploaded=st.file_uploader("Upload client Excel or CSV",type=["xlsx","csv"])
    if uploaded:
        if uploaded.name.lower().endswith(".csv"): df=pd.read_csv(uploaded)
        else:
            raw=pd.read_excel(uploaded,header=None); header=None
            for i,row in raw.iterrows():
                vals=[str(v).strip().lower() for v in row.tolist()]
                if "company" in vals and "contact name" in vals and "email" in vals: header=i; break
            if header is None: st.error("Required columns: Company, Contact Name and Email."); st.stop()
            uploaded.seek(0); df=pd.read_excel(uploaded,header=header)
        st.dataframe(df.head(10),use_container_width=True,hide_index=True)
        if st.button("Import Clients",type="primary"):
            cols={str(c).lower().strip():c for c in df.columns}; missing=[x for x in ["company","contact name","email"] if x not in cols]
            if missing: st.error("Missing: "+", ".join(missing))
            else:
                c=get_connection(); imported=0
                for _,r in df.iterrows():
                    try:
                        company=str(r[cols["company"]]).strip(); contact=str(r[cols["contact name"]]).strip(); email=str(r[cols["email"]]).strip()
                        if company and contact and email and email.lower()!="nan":
                            c.execute("INSERT INTO clients(company,contact_name,email,rsvp_token) VALUES(?,?,?,?)",(company,contact,email,generate_rsvp_token())); imported+=1
                    except sqlite3.IntegrityError: pass
                c.commit(); c.close(); st.success(f"{imported} clients imported."); st.rerun()
    c=get_connection(); df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Contact Name",designation AS "Designation",email AS "Email",rsvp_status AS "RSVP Status",invitation_sent AS "Invitation Sent",checked_in AS "Checked In" FROM clients ORDER BY company,contact_name',c); c.close()
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.success("No pending RSVPs.")
    st.download_button("Export Client List",df.to_csv(index=False).encode(),"Client_Connect_2026_Client_List.csv","text/csv")

elif page=="Invitations":
    st.markdown('<div class="section-title">Invitation Management</div>',unsafe_allow_html=True)
    st.write("Generate unique RSVP links for use in individual Outlook invitations.")
    public_url=st.text_input("Public Application URL",value="https://client-connect-2026.streamlit.app").strip().rstrip("/")
    c=get_connection(); df=pd.read_sql_query('SELECT id AS "Client ID",company AS "Company",contact_name AS "Contact Name",email AS "Email",rsvp_status AS "RSVP Status",invitation_sent AS "Invitation Sent",rsvp_token AS "RSVP Token" FROM clients ORDER BY company,contact_name',c); c.close()
    if not df.empty:
        df["RSVP Link"]=public_url+"/?rsvp="+df["RSVP Token"].astype(str)
        display=df[["Company","Contact Name","Email","RSVP Link","RSVP Status","Invitation Sent"]]
        st.dataframe(display,use_container_width=True,hide_index=True)
        st.download_button("Export Outlook Invitation List",display.to_csv(index=False).encode(),"Client_Connect_2026_Outlook_Invitation_List.csv","text/csv")
        if st.button("Mark All as Invitation Sent",type="primary"):
            c=get_connection(); c.execute("UPDATE clients SET invitation_sent=1 WHERE rsvp_token IS NOT NULL"); c.commit(); c.close(); st.success("Invitation status updated."); st.rerun()

elif page=="RSVP Tracker":
    st.markdown('<div class="section-title">RSVP Tracker</div>',unsafe_allow_html=True)
    status=st.selectbox("Show",["All","Pending","Accepted","Declined"])
    c=get_connection(); df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Contact Name",email AS "Email",rsvp_status AS "RSVP Status",rsvp_date AS "RSVP Date" FROM clients ORDER BY company,contact_name',c); c.close()
    if status!="All": df=df[df["RSVP Status"]==status]
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Export RSVP Tracker",df.to_csv(index=False).encode(),"Client_Connect_2026_RSVP_Tracker.csv","text/csv")

elif page=="Follow-ups":
    st.markdown('<div class="section-title">Follow-ups</div>',unsafe_allow_html=True)
    c=get_connection(); df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Contact Name",email AS "Email",priority AS "Priority",invitation_sent AS "Invitation Sent" FROM clients WHERE rsvp_status="Pending" ORDER BY company',c); c.close()
    st.metric("Pending RSVPs",len(df))
    st.dataframe(df,use_container_width=True,hide_index=True) if not df.empty else st.success("No pending RSVPs.")
    if not df.empty: st.download_button("Export Follow-up List",df.to_csv(index=False).encode(),"Client_Connect_2026_Follow_Up_List.csv","text/csv")

elif page=="Event Check-in":
    st.markdown('<div class="section-title">Event Check-in</div>',unsafe_allow_html=True)
    c=get_connection(); df=pd.read_sql_query('SELECT id AS "Client ID",company AS "Company",contact_name AS "Contact Name",email AS "Email",checked_in AS "Checked In",check_in_time AS "Check-in Time" FROM clients WHERE rsvp_status="Accepted" ORDER BY company',c); c.close()
    st.dataframe(df,use_container_width=True,hide_index=True)
    if not df.empty:
        selected=st.selectbox("Select client",df["Client ID"].tolist(),format_func=lambda x:f'{x} · {df.loc[df["Client ID"]==x,"Company"].iloc[0]} · {df.loc[df["Client ID"]==x,"Contact Name"].iloc[0]}')
        if st.button("Record Check-in",type="primary"):
            c=get_connection(); c.execute("UPDATE clients SET checked_in=1,check_in_time=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),int(selected))); c.commit(); c.close(); st.success("Check-in recorded."); st.rerun()

else:
    st.markdown('<div class="section-title">Reports</div>',unsafe_allow_html=True)
    total=scalar("SELECT COUNT(*) FROM clients"); sent=scalar("SELECT COUNT(*) FROM clients WHERE invitation_sent=1"); accepted=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Accepted'"); declined=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Declined'"); pending=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Pending'"); checked=scalar("SELECT COUNT(*) FROM clients WHERE checked_in=1")
    report=pd.DataFrame({"Measure":["Total Clients","Invitations Sent","Accepted","Declined","Pending","Checked In"],"Value":[total,sent,accepted,declined,pending,checked]})
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.download_button("Export Management Summary",report.to_csv(index=False).encode(),"Client_Connect_2026_Management_Summary.csv","text/csv")
