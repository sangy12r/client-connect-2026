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
.small-note{color:#667085;font-size:.88rem}
</style>
""", unsafe_allow_html=True)

# ---------- Common public RSVP ----------
if not st.query_params.get("admin") and not st.query_params.get("rsvp"):
    st.markdown(f"""<div class="rsvp-wrap">
    <div class="rsvp-banner"><h1>{EVENT_NAME}</h1><p>{EVENT_SUBTITLE}</p></div>
    <div class="rsvp-card">""", unsafe_allow_html=True)

    st.markdown("### You are invited")
    st.write("We are pleased to invite you to our Client Networking Evening.")

    st.markdown(f"""<div class="event-box">
    <b>Date</b><br>{EVENT_DATE}<br><br>
    <b>Time</b><br>{EVENT_TIME}<br><br>
    <b>Venue</b><br>{EVENT_VENUE}<br><br>
    <b>RSVP by</b><br>{RSVP_DEADLINE}
    </div>""", unsafe_allow_html=True)

    st.markdown("### RSVP")
    email = st.text_input("Email ID", placeholder="Enter your email ID")
    company = st.text_input("Company Name", placeholder="Enter your company name")
    name = st.text_input("Your Name", placeholder="Enter your name")

    response = st.radio(
        "Your response",
        ["Accept", "Tentative", "Decline"],
        horizontal=True
    )

    if st.button("Confirm RSVP", type="primary", use_container_width=True):
        email_clean = email.strip().lower()
        company_clean = company.strip()
        name_clean = name.strip()

        if not email_clean or not company_clean or not name_clean:
            st.error("Please enter your Email ID, Company Name and Name.")
        else:
            conn = get_connection()
            existing = conn.execute(
                "SELECT id, company, contact_name, rsvp_status FROM clients WHERE lower(email)=?",
                (email_clean,)
            ).fetchone()

            if existing:
                # Keep the original client record and update the submitted name/company
                # only when the email matches an invited client.
                conn.execute("""
                    UPDATE clients
                    SET company=?, contact_name=?, rsvp_status=?, rsvp_date=?,
                        invitation_opened=1, response_source='Online'
                    WHERE id=?
                """, (
                    company_clean, name_clean, response,
                    datetime.now().isoformat(timespec="seconds"), existing["id"]
                ))
                conn.commit()
                conn.close()
                st.success("Thank you. Your RSVP has been recorded successfully.")
            else:
                # Allow a personal/non-company email to register, while retaining it
                # as a new RSVP record for manual review.
                conn.execute("""
                    INSERT INTO clients
                    (company, contact_name, email, rsvp_status, rsvp_date,
                     invitation_sent, invitation_opened, response_source, rsvp_token, token_created_at)
                    VALUES (?, ?, ?, ?, ?, 1, 1, 'Online - New Email', ?, ?)
                """, (
                    company_clean, name_clean, email_clean, response,
                    datetime.now().isoformat(timespec="seconds"),
                    generate_rsvp_token(), datetime.now().isoformat(timespec="seconds")
                ))
                conn.commit()
                conn.close()
                st.success("Thank you. Your RSVP has been recorded successfully.")

    st.markdown('<div class="small-note">Only one RSVP is recorded per email ID.</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ---------- Admin application ----------
st.markdown(f'<div class="app-header"><h1>{EVENT_NAME}</h1><p>{EVENT_SUBTITLE}</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Client Connect")
    st.caption("Event Management")
    page=st.radio("Navigation",["Dashboard","Clients","Invitations","RSVP Tracker","Manual RSVP","Follow-ups","Event Check-in","Reports"])
    st.divider()
    st.caption("EVENT")
    st.write("23 October 2026")
    st.write("6:00 PM onwards")
    st.write("Venue: To be announced")
    st.caption("DEMO ENVIRONMENT")
    st.write("Dummy client data only")

def scalar(sql):
    c=get_connection()
    v=c.execute(sql).fetchone()[0]
    c.close()
    return v

if page=="Dashboard":
    st.markdown('<div class="section-title">Event Overview</div>',unsafe_allow_html=True)
    st.write("A single view of client invitations, RSVP status, follow-ups and event attendance.")
    total=scalar("SELECT COUNT(*) FROM clients")
    sent=scalar("SELECT COUNT(*) FROM clients WHERE invitation_sent=1")
    accepted=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Accepted'")
    tentative=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Tentative'")
    declined=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Declined'")
    pending=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Pending'")
    checked=scalar("SELECT COUNT(*) FROM clients WHERE checked_in=1")
    for col,(label,val) in zip(st.columns(7),[("CLIENTS",total),("SENT",sent),("ACCEPTED",accepted),("TENTATIVE",tentative),("DECLINED",declined),("PENDING",pending),("CHECKED IN",checked)]):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>',unsafe_allow_html=True)
    st.divider()
    left,right=st.columns([1.15,1])
    with left:
        st.markdown('<div class="section-title">RSVP Progress</div>',unsafe_allow_html=True)
        st.progress((accepted+tentative)/total if total else 0)
        st.write(f"{accepted + tentative} of {total} invited clients have responded positively or tentatively.")
        st.dataframe(pd.DataFrame({"Status":["Accepted","Tentative","Pending","Declined"],"Clients":[accepted,tentative,pending,declined]}),use_container_width=True,hide_index=True)
    with right:
        st.markdown('<div class="section-title">Event Details</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="info-card"><b>Date</b><br>{EVENT_DATE}<br><br><b>Time</b><br>{EVENT_TIME}<br><br><b>Venue</b><br>{EVENT_VENUE}<br><br><b>RSVP Deadline</b><br>{RSVP_DEADLINE}</div>',unsafe_allow_html=True)

elif page=="Clients":
    st.markdown('<div class="section-title">Client Database</div>',unsafe_allow_html=True)
    st.write("Upload the invitation master list or review current client records.")
    uploaded=st.file_uploader("Upload client Excel or CSV",type=["xlsx","csv"])
    if uploaded:
        if uploaded.name.lower().endswith(".csv"):
            df=pd.read_csv(uploaded)
        else:
            raw=pd.read_excel(uploaded,header=None)
            header=None
            for i,row in raw.iterrows():
                vals=[str(v).strip().lower() for v in row.tolist()]
                if "company" in vals and "contact name" in vals and "email" in vals:
                    header=i
                    break
            if header is None:
                st.error("Required columns: Company, Contact Name and Email.")
                st.stop()
            uploaded.seek(0)
            df=pd.read_excel(uploaded,header=header)
        st.dataframe(df.head(10),use_container_width=True,hide_index=True)
        if st.button("Import Clients",type="primary"):
            cols={str(c).lower().strip():c for c in df.columns}
            missing=[x for x in ["company","contact name","email"] if x not in cols]
            if missing:
                st.error("Missing: "+", ".join(missing))
            else:
                c=get_connection()
                imported=0
                for _,r in df.iterrows():
                    try:
                        company=str(r[cols["company"]]).strip()
                        contact=str(r[cols["contact name"]]).strip()
                        email=str(r[cols["email"]]).strip().lower()
                        if company and contact and email and email!="nan":
                            c.execute("INSERT INTO clients(company,contact_name,email,rsvp_token,response_source) VALUES(?,?,?,?,?)",
                                      (company,contact,email,generate_rsvp_token(),"Imported"))
                            imported+=1
                    except sqlite3.IntegrityError:
                        pass
                c.commit()
                c.close()
                st.success(f"{imported} clients imported.")
                st.rerun()

    c=get_connection()
    df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Contact Name",designation AS "Designation",email AS "Email",rsvp_status AS "RSVP Status",response_source AS "Response Source",invitation_sent AS "Invitation Sent",checked_in AS "Checked In" FROM clients ORDER BY company,contact_name',c)
    c.close()
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Export Client List",df.to_csv(index=False).encode(),"Client_Connect_2026_Client_List.csv","text/csv")

elif page=="Invitations":
    st.markdown('<div class="section-title">Invitation Management</div>',unsafe_allow_html=True)
    st.write("Use one common RSVP link in your Outlook invitation.")
    public_url=st.text_input("Public Application URL",value="https://client-connect-2026.streamlit.app").strip().rstrip("/")
    common_link=public_url
    st.success("Common RSVP link ready")
    st.code(common_link)
    st.caption("Share this same link with all invited clients. Their email ID, company name, name and RSVP response will be captured by the application.")
    st.markdown("### Suggested email wording")
    st.text_area("Invitation text", value=f"""Dear Client,

We are pleased to invite you to {EVENT_NAME}.

Date: {EVENT_DATE}
Time: {EVENT_TIME}
Venue: {EVENT_VENUE}

Please confirm your attendance using the link below:
{common_link}

Regards,
Wilhelmsen Port Services""", height=220)
    c=get_connection()
    sent_count=c.execute("SELECT COUNT(*) FROM clients WHERE invitation_sent=1").fetchone()[0]
    c.close()
    st.metric("Invitation records",sent_count)
    if st.button("Mark All Invitations as Sent",type="primary"):
        c=get_connection()
        c.execute("UPDATE clients SET invitation_sent=1")
        c.commit()
        c.close()
        st.success("Invitation status updated.")
        st.rerun()

elif page=="RSVP Tracker":
    st.markdown('<div class="section-title">RSVP Tracker</div>',unsafe_allow_html=True)
    status=st.selectbox("Show",["All","Pending","Accepted","Tentative","Declined"])
    c=get_connection()
    df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Name",email AS "Email",rsvp_status AS "RSVP Status",response_source AS "Response Source",rsvp_date AS "RSVP Date" FROM clients ORDER BY company,contact_name',c)
    c.close()
    if status!="All":
        df=df[df["RSVP Status"]==status]
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Export RSVP Tracker",df.to_csv(index=False).encode(),"Client_Connect_2026_RSVP_Tracker.csv","text/csv")

elif page=="Manual RSVP":
    st.markdown('<div class="section-title">Manual RSVP Entry</div>',unsafe_allow_html=True)
    st.write("Use this when a client confirms by phone, WhatsApp or email and asks you to record the RSVP.")
    with st.form("manual_rsvp_form"):
        email=st.text_input("Email ID")
        company=st.text_input("Company Name")
        name=st.text_input("Client Name")
        response=st.selectbox("Response",["Accepted","Tentative","Declined"])
        submitted=st.form_submit_button("Save RSVP",type="primary")
    if submitted:
        email_clean=email.strip().lower()
        if not email_clean or not company.strip() or not name.strip():
            st.error("Please complete Email ID, Company Name and Client Name.")
        else:
            c=get_connection()
            existing=c.execute("SELECT id FROM clients WHERE lower(email)=?",(email_clean,)).fetchone()
            now=datetime.now().isoformat(timespec="seconds")
            if existing:
                c.execute("""UPDATE clients SET company=?,contact_name=?,rsvp_status=?,rsvp_date=?,invitation_opened=1,response_source='Manual' WHERE id=?""",
                          (company.strip(),name.strip(),response,now,existing["id"]))
            else:
                c.execute("""INSERT INTO clients(company,contact_name,email,rsvp_status,rsvp_date,invitation_sent,invitation_opened,response_source,rsvp_token,token_created_at)
                             VALUES(?,?,?,?,?,1,1,'Manual',?,?)""",
                          (company.strip(),name.strip(),email_clean,response,now,generate_rsvp_token(),now))
            c.commit()
            c.close()
            st.success("Manual RSVP saved successfully.")
            st.rerun()

elif page=="Follow-ups":
    st.markdown('<div class="section-title">Follow-ups</div>',unsafe_allow_html=True)
    c=get_connection()
    df=pd.read_sql_query('SELECT company AS "Company",contact_name AS "Contact Name",email AS "Email",priority AS "Priority",invitation_sent AS "Invitation Sent" FROM clients WHERE rsvp_status="Pending" ORDER BY company',c)
    c.close()
    st.metric("Pending RSVPs",len(df))
    if not df.empty:
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("Export Follow-up List",df.to_csv(index=False).encode(),"Client_Connect_2026_Follow_Up_List.csv","text/csv")
    else:
        st.success("No pending RSVPs.")

elif page=="Event Check-in":
    st.markdown('<div class="section-title">Event Check-in</div>',unsafe_allow_html=True)
    c=get_connection()
    df=pd.read_sql_query('SELECT id AS "Client ID",company AS "Company",contact_name AS "Contact Name",email AS "Email",checked_in AS "Checked In",check_in_time AS "Check-in Time" FROM clients WHERE rsvp_status="Accepted" ORDER BY company',c)
    c.close()
    st.dataframe(df,use_container_width=True,hide_index=True)
    if not df.empty:
        selected=st.selectbox("Select client",df["Client ID"].tolist(),format_func=lambda x:f'{x} · {df.loc[df["Client ID"]==x,"Company"].iloc[0]} · {df.loc[df["Client ID"]==x,"Contact Name"].iloc[0]}')
        if st.button("Record Check-in",type="primary"):
            c=get_connection()
            c.execute("UPDATE clients SET checked_in=1,check_in_time=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),int(selected)))
            c.commit()
            c.close()
            st.success("Check-in recorded.")
            st.rerun()

else:
    st.markdown('<div class="section-title">Reports</div>',unsafe_allow_html=True)
    total=scalar("SELECT COUNT(*) FROM clients")
    sent=scalar("SELECT COUNT(*) FROM clients WHERE invitation_sent=1")
    accepted=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Accepted'")
    tentative=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Tentative'")
    declined=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Declined'")
    pending=scalar("SELECT COUNT(*) FROM clients WHERE rsvp_status='Pending'")
    checked=scalar("SELECT COUNT(*) FROM clients WHERE checked_in=1")
    report=pd.DataFrame({"Measure":["Total Clients","Invitations Sent","Accepted","Tentative","Declined","Pending","Checked In"],"Value":[total,sent,accepted,tentative,declined,pending,checked]})
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.download_button("Export Management Summary",report.to_csv(index=False).encode(),"Client_Connect_2026_Management_Summary.csv","text/csv")
