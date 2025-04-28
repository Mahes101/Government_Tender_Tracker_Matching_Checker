# Government_Tender_Tracker_Matching_Checker

1. Objective
Develop a web-based application that automatically aggregates tender notices from Central (CPPP, GeM) and State e-procurement portals.
Enable companies to upload or link their capability profiles and receive individualized recommendations when new tenders align with their services.
Provide an intuitive interface using Streamlit for easy interaction and visualization.
Optionally, implement messaging notifications (SMS/Email) via Twilio or Gmail automation for real-time alerts.

2. Problem Statement
Organizations bid on government tenders to secure contracts, but manually monitoring multiple procurement portals and matching complex requirements against internal capabilities is time-consuming and error-prone. There is a need for an automated tool that:
Continuously fetches new tender data from diverse e-procurement sources.
Parses and normalizes key tender criteria (EMD, deadlines, scope of work).
Matches and scores tenders against a company’s profile (financial capacity, services offered).
Presents curated, high-fit tender recommendations through an easy-to-use dashboard.

3. Expected Outcomes
Real-Time Tender Aggregation: Automated ingestion of tender metadata and documents from at least three distinct portals (e.g., CPPP XML, GeM API, one State portal).
Automated Requirement Scanner: Extraction of EMD amounts, bid deadlines, and scope details via pdfplumber and BeautifulSoup.
Company Profile Matching: TF-IDF or embedding-based similarity scoring with adjustable threshold to flag high-potential tenders.
Streamlit Dashboard: Interactive UI allowing users to:
View and search aggregated tenders.
Upload or link their capability profile.
See match scores and tender details.
Optional Notifications:
SMS alerts via Twilio for tenders exceeding the match threshold.
Email alerts using Gmail SMTP automation (students can configure via OAuth2 credentials).
Reference Portal 
https://etenders.gov.in/eprocure/app
https://gem.gov.in/
https://bidplus.gem.gov.in/all-bids
