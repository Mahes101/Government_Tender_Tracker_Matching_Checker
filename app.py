# Import necessary libraries
import streamlit as st
import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from twilio.rest import Client
import smtplib

st.set_page_config(
    page_title="Custom Streamlit App",
    page_icon="🎨",
    layout="wide",  # Options: "centered" or "wide"
    initial_sidebar_state="expanded",  # Options: "expanded" or "collapsed"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
        color: #31333F;
        font-family: 'Arial', sans-serif;
    }
    .stSidebar {
        background-color: #88C9AB;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit app title
st.title("Tender Aggregation and Recommendation System")

# Section for capability profile upload
st.sidebar.header("Upload Capability Profile")
capability_profile = st.sidebar.text_area("Enter your company's capability details:")

# Helper function to fetch tenders from portals
def fetch_tenders():
    # URL of the website
    url = "https://gem.gov.in/cppp"  

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the table (adjust selectors based on the actual HTML structure)
        table = soup.find('table', class_='table')  # Locate the table with the correct tag and class
        
        # Extract table headers
        headers = [header.text.strip() for header in table.find('thead').find_all('th')]
        
        # Extract table rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            if len(cells) == len(headers):  # Ensure the row matches the headers
                row_data = {headers[i]: cells[i].text.strip() for i in range(len(headers))}
                rows.append(row_data)
        
        # Print the list of dictionaries
        print(rows)
    else:
        print("Failed to fetch the webpage. Please check the URL or your internet connection.")

    
    # Convert the list of dictionaries to a DataFrame
    return pd.DataFrame(rows)

# Fetch tenders
st.header("Aggregated Tenders")
tenders_df = fetch_tenders()
st.write(tenders_df)

# Matching tenders to company profile
def match_tenders(tenders, profile):
    vectorizer = TfidfVectorizer()
    tender_texts = tenders['Title'] + " " + tenders['Scope']
    profile_vector = vectorizer.fit_transform([profile])
    tender_vectors = vectorizer.transform(tender_texts)
    scores = cosine_similarity(profile_vector, tender_vectors).flatten()
    tenders['Match Score'] = scores
    return tenders.sort_values(by='Match Score', ascending=False)

if capability_profile:
    matched_tenders = match_tenders(tenders_df, capability_profile)
    st.header("Matched Tenders")
    st.write(matched_tenders)

# Optional: SMS Notifications via Twilio
def send_sms(tenders):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)
    if not tenders.empty:
        for _, tender in tenders.iterrows():
            message = f"Subject: New Matched Tender\n\nNew tender found: {tender['Title']}"
            client.messages.create(
                body=message,
                from_='+1234567890',  # Your Twilio number
                to='+0987654321'  # Recipient's number
            )
    else:
        st.sidebar.write("No tenders to send.")

if st.sidebar.button("Send SMS Alerts"):
    send_sms(matched_tenders)

# Optional: Email Notifications via Gmail SMTP
def send_email(tenders):
    sender_email = st.sidebar.text_input("Sender Email", "your_email@gmail.com")
    receiver_email = st.sidebar.text_input("Receiver Email", "receiver_email@gmail.com")
    password = st.sidebar.text_input("Password", type="password")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        if not tenders.empty:
            for _, tender in tenders.iterrows():
                message = f"Subject: New Matched Tender\n\nNew tender found: {tender['Title']}"
                server.sendmail(sender_email, receiver_email, message)
                st.sidebar.write("Email alerts sent!")
            server.quit()
        else:
            st.sidebar.write("No tenders to send.")
        
        
if st.sidebar.button("Send Email Alerts"):
    if capability_profile:
        send_email(matched_tenders)
        