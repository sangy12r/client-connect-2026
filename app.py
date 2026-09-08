import re
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from database import initialize_database, get_connection


initialize_database()

st.set_page_config(
    page_title="Client Connect 2026",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

EVENT_NAME = "Client Connect 2026"
EVENT_SUBTITLE = "Wilhelmsen Port Services, India · Client Networking Evening"
EVENT_DATE = "Friday, 23 October 2026"
EVENT_TIME = "6:00 PM onwards"
EVENT_VENUE = "To be announced"
RSVP_DEADLINE = "Friday, 16 October 2026"

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ============================================================
# CLIENT RSVP PAGE (single common link for every client)
# ============================================================

show_rsvp_page = st.query_params.get("rsvp") is not None

if show_rsvp_page:
    st.markdown(
        """
        <style>
        .rsvp-page { max-width: 850px; margin: 30px auto; }
        .rsvp-header {
            background: linear-gradient(135deg, #063b6f, #0b6aa8);
            padding: 38px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 22px;
        }
        .rsvp-header h1 { margin: 0 0 8px 0; font-size: 2.3rem; }
        .rsvp-header p { margin: 0; font-size: 1rem; }
        .rsvp-card {
            background: white;
            padding: 34px;
            border-radius: 20px;
            border: 1px solid #dfe6ee;
            box-shadow: 0 5px 20px rgba(20, 50, 80, 0.08);
        }
        .event-info {
            background: #f5f8fc;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            line-height: 1.7;
        }
        .rsvp-footer { color: #667085; text-align: center; margin-top: 24px; font-size: .9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="rsvp-page">
            <div class="rsvp-header">
                <h1>{EVENT_NAME}</h1>
                <p>{EVENT_SUBTITLE}</p>
            </div>
            <div class="rsvp-card">
                <p>You're invited to our Client Networking Evening. Please confirm your attendance below.</p>
                <div class="event-info">
                    <strong>Date</strong><br>{EVENT_DATE}<br><br>
                    <strong>Time</strong><br>{EVENT_TIME}<br><br>
                    <strong>Venue</strong><br>{EVENT_VENUE}<br><br>
                    <strong>RSVP by</strong><br>{RSVP_DEADLINE}
                </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("rsvp_saved"):
        st.success("Thank you. Your RSVP has been recorded successfully.")
        st.session_state["rsvp_saved"] = False

    email = st.text_input("Email ID", placeholder="Enter your email ID")
    name = st.text_input("Your Name", placeholder="Enter your name")
    company = st.text_input("Company Name", placeholder="Enter your company name")
    response = st.radio(
        "Will you be attending?",
        ["Yes", "No", "Tentative"],
        horizontal=True,
    )

    st.caption("Only one RSVP is recorded per email ID — submitting again updates your existing response.")

    if st.button("Confirm RSVP", type="primary", use_container_width=True):
        email_clean = email.strip().lower()
        name_clean = name.strip()
        company_clean = company.strip()

        if not email_clean or not EMAIL_PATTERN.match(email_clean):
            st.error("Please enter a valid email ID.")
        elif not name_clean:
            st.error("Please enter your name.")
        elif not company_clean:
            st.error("Please enter your company name.")
        else:
            status_map = {"Yes": "Accepted", "No": "Declined", "Tentative": "Tentative"}
            new_status = status_map[response]
            attendees = 1 if new_status == "Accepted" else 0
            now = datetime.now().isoformat(timespec="seconds")

            connection = get_connection()
            existing = connection.execute(
                "SELECT id FROM clients WHERE email = ?", (email_clean,)
            ).fetchone()

            if existing:
                connection.execute(
                    """
                    UPDATE clients
                    SET company = ?,
                        contact_name = ?,
                        rsvp_status = ?,
                        attendees = ?,
                        rsvp_date = ?,
                        invitation_opened = 1
                    WHERE email = ?
                    """,
                    (company_clean, name_clean, new_status, attendees, now, email_clean),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO clients
                        (company, contact_name, email, rsvp_status, attendees,
                         rsvp_date, invitation_sent, invitation_opened)
                    VALUES (?, ?, ?, ?, ?, ?, 1, 1)
                    """,
                    (company_clean, name_clean, email_clean, new_status, attendees, now),
                )

            connection.commit()
            connection.close()
            st.session_state["rsvp_saved"] = True
            st.rerun()

    st.markdown(
        """
            </div>
            <div class="rsvp-footer">
                For any changes or questions, please contact the event organiser.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# ADMIN STYLE
# ============================================================

st.markdown(
    """
    <style>
    .stApp { background-color: #f5f8fc; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
    #MainMenu, footer { visibility: hidden; }
    .app-header {
        background: linear-gradient(135deg, #063b6f, #0b6aa8);
        padding: 25px 32px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
    }
    .app-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
    .app-header p { margin: 7px 0 0 0; font-size: .95rem; opacity: .9; }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e0e7ef;
        box-shadow: 0 3px 12px rgba(20, 50, 80, .06);
    }
    .metric-title { color: #667085; font-size: .78rem; font-weight: 700; letter-spacing: .05em; }
    .metric-value { color: #063b6f; font-size: 2rem; font-weight: 700; margin-top: 5px; }
    .section-title { color: #063b6f; font-size: 1.2rem; font-weight: 700; margin-top: 20px; margin-bottom: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div class="app-header">
        <h1>{EVENT_NAME}</h1>
        <p>{EVENT_SUBTITLE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## Client Connect")
    st.caption("Event Management")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Clients",
            "Invitations",
            "RSVP Tracker",
            "Follow-ups",
            "Event Check-in",
            "Reports",
        ],
    )

    st.divider()
    st.caption("Event")
    st.write("23 October 2026")
    st.write("6:00 PM onwards")
    st.write("Venue: To be announced")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":
    st.markdown("<div class='section-title'>Event Overview</div>", unsafe_allow_html=True)
    st.write("Welcome, Sangeeta. Here's your current event snapshot.")

    connection = get_connection()
    total_clients = connection.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    accepted = connection.execute("SELECT COUNT(*) FROM clients WHERE rsvp_status = 'Accepted'").fetchone()[0]
    declined = connection.execute("SELECT COUNT(*) FROM clients WHERE rsvp_status = 'Declined'").fetchone()[0]
    tentative = connection.execute("SELECT COUNT(*) FROM clients WHERE rsvp_status = 'Tentative'").fetchone()[0]
    pending = connection.execute("SELECT COUNT(*) FROM clients WHERE rsvp_status = 'Pending'").fetchone()[0]
    expected = connection.execute(
        "SELECT COALESCE(SUM(attendees), 0) FROM clients WHERE rsvp_status = 'Accepted'"
    ).fetchone()[0]
    invitation_sent = connection.execute(
        "SELECT COUNT(*) FROM clients WHERE invitation_sent = 1"
    ).fetchone()[0]
    connection.close()

    columns = st.columns(6)
    for column, (title, value) in zip(
        columns,
        [
            ("INVITED", total_clients),
            ("ACCEPTED", accepted),
            ("DECLINED", declined),
            ("TENTATIVE", tentative),
            ("PENDING", pending),
            ("EXPECTED", expected),
        ],
    ):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("<div class='section-title'>RSVP Progress</div>", unsafe_allow_html=True)
        if total_clients:
            st.progress(accepted / total_clients)
            st.write(f"{accepted} of {total_clients} invited clients have confirmed.")
        else:
            st.info("No clients have been added yet.")

        st.markdown("<div class='section-title'>Invitation Progress</div>", unsafe_allow_html=True)
        if total_clients:
            st.progress(invitation_sent / total_clients)
            st.write(f"{invitation_sent} of {total_clients} clients marked as Invitation Sent.")
        else:
            st.info("No clients have been added yet.")

    with right:
        st.markdown("<div class='section-title'>Event Details</div>", unsafe_allow_html=True)
        st.info(
            f"Date: {EVENT_DATE}\n\n"
            f"Time: {EVENT_TIME}\n\n"
            f"Venue: {EVENT_VENUE}\n\n"
            f"RSVP deadline: {RSVP_DEADLINE}"
        )


# ============================================================
# CLIENTS
# ============================================================

elif page == "Clients":
    st.markdown("<div class='section-title'>Client Database</div>", unsafe_allow_html=True)
    st.write("Manage your invited clients and prepare the master guest list.")

    st.subheader("Import Clients")

    uploaded_file = st.file_uploader(
        "Upload your client Excel or CSV file",
        type=["xlsx", "csv"],
        key="client_import",
    )

    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".csv"):
            uploaded_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file, header=None)
            header_row = None

            for i, row in raw_df.iterrows():
                row_values = [str(value).strip().lower() for value in row.tolist()]
                if "company" in row_values and "contact name" in row_values and "email" in row_values:
                    header_row = i
                    break

            if header_row is None:
                st.error(
                    "I couldn't identify the header row. The file needs Company, Contact Name and Email."
                )
                st.stop()

            uploaded_file.seek(0)
            uploaded_df = pd.read_excel(uploaded_file, header=header_row)

        uploaded_df.columns = uploaded_df.columns.astype(str).str.strip()
        uploaded_df = uploaded_df.dropna(axis=1, how="all")
        uploaded_df = uploaded_df.loc[
            :,
            ~uploaded_df.columns.astype(str).str.lower().str.startswith("unnamed"),
        ]

        column_map = {str(column).strip().lower(): column for column in uploaded_df.columns}
        required_columns = ["company", "contact name", "email"]
        missing_columns = [column for column in required_columns if column not in column_map]

        st.subheader("Preview")
        st.dataframe(uploaded_df.head(10), use_container_width=True, hide_index=True)
        st.write(f"Rows detected: {len(uploaded_df)}")

        if missing_columns:
            st.error("Missing required columns: " + ", ".join(missing_columns))
        else:
            company_column = column_map["company"]
            contact_column = column_map["contact name"]
            email_column = column_map["email"]

            if st.button("Import Clients", type="primary", key="import_clients"):
                connection = get_connection()
                imported = 0
                duplicates = 0
                skipped = 0

                for _, row in uploaded_df.iterrows():
                    company = str(row[company_column]).strip()
                    contact_name = str(row[contact_column]).strip()
                    email = str(row[email_column]).strip()

                    if not company or not contact_name or not email or email.lower() == "nan":
                        skipped += 1
                        continue

                    designation = str(row.get("Designation", "")).strip()
                    mobile = str(row.get("Mobile", "")).strip()
                    category = str(row.get("Category", "")).strip()
                    priority = str(row.get("Priority", "Normal")).strip()

                    try:
                        connection.execute(
                            """
                            INSERT INTO clients
                            (company, contact_name, designation, email, mobile, category, priority)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (company, contact_name, designation, email, mobile, category, priority),
                        )
                        imported += 1
                    except sqlite3.IntegrityError:
                        duplicates += 1

                connection.commit()
                connection.close()

                st.success(f"{imported} clients imported successfully.")
                if duplicates:
                    st.warning(f"{duplicates} duplicate email IDs were skipped.")
                if skipped:
                    st.warning(f"{skipped} incomplete rows were skipped.")
                st.rerun()

    st.divider()
    st.subheader("Current Client List")

    connection = get_connection()
    clients_df = pd.read_sql_query(
        """
        SELECT
            id AS "Client ID",
            company AS "Company",
            contact_name AS "Contact Name",
            designation AS "Designation",
            email AS "Email",
            mobile AS "Mobile",
            category AS "Category",
            priority AS "Priority",
            rsvp_status AS "RSVP Status",
            attendees AS "Attendees",
            invitation_sent AS "Invitation Sent"
        FROM clients
        ORDER BY company, contact_name
        """,
        connection,
    )
    connection.close()

    if clients_df.empty:
        st.info("No clients have been imported yet.")
    else:
        st.write(f"Total clients: {len(clients_df)}")
        search = st.text_input(
            "Search clients",
            placeholder="Company, contact name or email...",
            key="client_search",
        )
        status_filter = st.selectbox(
            "RSVP Status",
            ["All", "Pending", "Accepted", "Declined"],
            key="client_status_filter",
        )

        filtered_df = clients_df.copy()

        if search:
            term = search.lower()
            filtered_df = filtered_df[
                filtered_df["Company"].astype(str).str.lower().str.contains(term, na=False)
                | filtered_df["Contact Name"].astype(str).str.lower().str.contains(term, na=False)
                | filtered_df["Email"].astype(str).str.lower().str.contains(term, na=False)
            ]

        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["RSVP Status"] == status_filter]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Export Client List",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="Client_Connect_2026_Client_List.csv",
            mime="text/csv",
            key="export_clients",
        )


# ============================================================
# INVITATIONS
# ============================================================

elif page == "Invitations":
    st.markdown("<div class='section-title'>Invitation Management</div>", unsafe_allow_html=True)
    st.write("Generate personalised RSVP links and prepare your Outlook invitation list.")

    st.subheader("Event Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Date")
        st.write(EVENT_DATE)
    with col2:
        st.write("Time")
        st.write(EVENT_TIME)
    with col3:
        st.write("Venue")
        st.write(EVENT_VENUE)

    st.divider()
    st.subheader("Shared RSVP Link")
    base_url = st.text_input(
        "Application URL",
        value="http://localhost:8501",
        help="Use localhost while testing. Replace it with the public HTTPS URL after deployment.",
    )

    shared_link = base_url.rstrip("/") + "/?rsvp=1"

    connection = get_connection()
    total_clients = connection.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    responded = connection.execute(
        "SELECT COUNT(*) FROM clients WHERE rsvp_status != 'Pending'"
    ).fetchone()[0]
    sent_count = connection.execute(
        "SELECT COUNT(*) FROM clients WHERE invitation_sent = 1"
    ).fetchone()[0]
    connection.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Clients", total_clients)
    with col2:
        st.metric("RSVP'd So Far", responded)
    with col3:
        st.metric("Marked as Sent", sent_count)

    st.info(
        "This is the same link for every client — paste it into your Outlook invitation "
        "email body and onto the invitation card (as text or a QR code). Each client fills "
        "in their own email, name, company, and attendance status; responses land in the "
        "RSVP Tracker automatically."
    )
    st.code(shared_link, language=None)

    st.divider()
    st.subheader("Mark Invitations as Sent")

    if total_clients == 0:
        st.info("No clients have been imported yet. Go to Clients first.")
    elif st.button("Mark All Clients as Invitation Sent", type="primary", key="mark_all_sent"):
        connection = get_connection()
        connection.execute("UPDATE clients SET invitation_sent = 1")
        connection.commit()
        connection.close()
        st.success("All clients have been marked as Invitation Sent.")
        st.rerun()

    st.divider()
    st.subheader("Client List for Outlook")
    st.info(
        "Export this list to build your BCC list or mail-merge in Outlook. "
        "Every recipient uses the same RSVP link above."
    )

    connection = get_connection()
    contact_df = pd.read_sql_query(
        """
        SELECT
            company AS "Company",
            contact_name AS "Contact Name",
            email AS "Email",
            rsvp_status AS "RSVP Status",
            invitation_sent AS "Invitation Sent"
        FROM clients
        ORDER BY company, contact_name
        """,
        connection,
    )
    connection.close()

    if contact_df.empty:
        st.info("No clients have been imported yet.")
    else:
        st.dataframe(contact_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Export Outlook Invitation List",
            data=contact_df.to_csv(index=False).encode("utf-8"),
            file_name="Client_Connect_2026_Outlook_Invitation_List.csv",
            mime="text/csv",
            key="export_invitation_list",
        )


# ============================================================
# RSVP TRACKER
# ============================================================

elif page == "RSVP Tracker":
    st.markdown("<div class='section-title'>RSVP Tracker</div>", unsafe_allow_html=True)
    st.write("Monitor responses and attendee counts in one place.")

    connection = get_connection()
    tracker_df = pd.read_sql_query(
        """
        SELECT
            id AS "Client ID",
            company AS "Company",
            contact_name AS "Contact Name",
            email AS "Email",
            rsvp_status AS "RSVP Status",
            attendees AS "Attendees",
            guest_name AS "Guest Name",
            rsvp_date AS "RSVP Date"
        FROM clients
        ORDER BY
            CASE rsvp_status
                WHEN 'Pending' THEN 1
                WHEN 'Accepted' THEN 2
                WHEN 'Tentative' THEN 3
                WHEN 'Declined' THEN 4
                ELSE 5
            END,
            company
        """,
        connection,
    )
    connection.close()

    if tracker_df.empty:
        st.info("No clients have been imported yet.")
    else:
        status = st.selectbox("Show", ["All", "Pending", "Accepted", "Tentative", "Declined"], key="tracker_status")
        filtered = tracker_df if status == "All" else tracker_df[tracker_df["RSVP Status"] == status]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button(
            "Export RSVP Tracker",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="Client_Connect_2026_RSVP_Tracker.csv",
            mime="text/csv",
            key="export_rsvp",
        )


# ============================================================
# FOLLOW-UPS
# ============================================================

elif page == "Follow-ups":
    st.markdown("<div class='section-title'>Follow-ups</div>", unsafe_allow_html=True)
    st.write("Identify clients who still need an RSVP follow-up.")

    connection = get_connection()
    pending_df = pd.read_sql_query(
        """
        SELECT
            id AS "Client ID",
            company AS "Company",
            contact_name AS "Contact Name",
            email AS "Email",
            priority AS "Priority",
            invitation_sent AS "Invitation Sent"
        FROM clients
        WHERE rsvp_status = 'Pending'
        ORDER BY
            CASE priority
                WHEN 'VIP' THEN 1
                WHEN 'High' THEN 2
                ELSE 3
            END,
            company
        """,
        connection,
    )
    connection.close()

    st.metric("Pending RSVPs", len(pending_df))

    if pending_df.empty:
        st.success("No pending RSVPs. Excellent.")
    else:
        st.dataframe(pending_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Export Follow-up List",
            data=pending_df.to_csv(index=False).encode("utf-8"),
            file_name="Client_Connect_2026_Follow_Up_List.csv",
            mime="text/csv",
            key="export_followups",
        )


# ============================================================
# EVENT CHECK-IN
# ============================================================

elif page == "Event Check-in":
    st.markdown("<div class='section-title'>Event Check-in</div>", unsafe_allow_html=True)
    st.write("Search accepted clients and record arrivals on event day.")

    connection = get_connection()
    checkin_df = pd.read_sql_query(
        """
        SELECT
            id AS "Client ID",
            company AS "Company",
            contact_name AS "Contact Name",
            email AS "Email",
            attendees AS "Attendees",
            checked_in AS "Checked In",
            check_in_time AS "Check-in Time"
        FROM clients
        WHERE rsvp_status = 'Accepted'
        ORDER BY company, contact_name
        """,
        connection,
    )
    connection.close()

    if checkin_df.empty:
        st.info("No accepted clients are currently available for check-in.")
    else:
        search = st.text_input(
            "Search accepted clients",
            placeholder="Company, contact name or email...",
            key="checkin_search",
        )
        filtered = checkin_df.copy()
        if search:
            term = search.lower()
            filtered = filtered[
                filtered["Company"].astype(str).str.lower().str.contains(term, na=False)
                | filtered["Contact Name"].astype(str).str.lower().str.contains(term, na=False)
                | filtered["Email"].astype(str).str.lower().str.contains(term, na=False)
            ]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.divider()
        selected_id = st.number_input("Client ID to check in", min_value=1, step=1, key="checkin_client_id")

        if st.button("Record Check-in", type="primary", key="record_checkin"):
            connection = get_connection()
            client = connection.execute(
                "SELECT id, contact_name, company, rsvp_status FROM clients WHERE id = ?",
                (int(selected_id),),
            ).fetchone()

            if client is None:
                connection.close()
                st.error("Client ID not found.")
            elif client[3] != "Accepted":
                connection.close()
                st.error("Only accepted clients can be checked in.")
            else:
                connection.execute(
                    "UPDATE clients SET checked_in = 1, check_in_time = ? WHERE id = ?",
                    (datetime.now().isoformat(timespec="seconds"), int(selected_id)),
                )
                connection.commit()
                connection.close()
                st.success(f"{client[1]} from {client[2]} has been checked in.")
                st.rerun()


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":
    st.markdown("<div class='section-title'>Reports</div>", unsafe_allow_html=True)
    st.write("Event summary and exportable management data.")

    connection = get_connection()
    summary = connection.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN rsvp_status = 'Accepted' THEN 1 ELSE 0 END),
            SUM(CASE WHEN rsvp_status = 'Declined' THEN 1 ELSE 0 END),
            SUM(CASE WHEN rsvp_status = 'Tentative' THEN 1 ELSE 0 END),
            SUM(CASE WHEN rsvp_status = 'Pending' THEN 1 ELSE 0 END),
            COALESCE(SUM(CASE WHEN rsvp_status = 'Accepted' THEN attendees ELSE 0 END), 0),
            SUM(CASE WHEN checked_in = 1 THEN 1 ELSE 0 END)
        FROM clients
        """
    ).fetchone()
    connection.close()

    total, accepted, declined, tentative, pending, expected, checked_in = summary

    columns = st.columns(3)
    for column, title, value in zip(
        columns,
        ["Invited", "Expected Attendees", "Checked In"],
        [total or 0, expected or 0, checked_in or 0],
    ):
        with column:
            st.metric(title, value)

    report = pd.DataFrame(
        {
            "Metric": [
                "Invited",
                "Accepted",
                "Declined",
                "Tentative",
                "Pending",
                "Expected Attendees",
                "Checked In",
            ],
            "Count": [
                total or 0,
                accepted or 0,
                declined or 0,
                tentative or 0,
                pending or 0,
                expected or 0,
                checked_in or 0,
            ],
        }
    )

    st.dataframe(report, use_container_width=True, hide_index=True)
    st.download_button(
        "Export Event Summary",
        data=report.to_csv(index=False).encode("utf-8"),
        file_name="Client_Connect_2026_Event_Summary.csv",
        mime="text/csv",
        key="export_report",
    )
