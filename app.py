# Import necessary libraries
import streamlit as st
import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from twilio.rest import Client
import smtplib

st.set_page_config(
    page_title="Tender Aggergation Streamlit App",
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
st.sidebar.write("Upload your company profile in PDF format or enter it manually.")
st.sidebar.write("This will help us match you with relevant tenders.")

def getting_company_profile():
    
    # Create Tabs for Options
    tab1, tab2 = st.tabs(["Upload PDF", "Enter Manually"])
    text = ""  # Placeholder for company profile text

    # Tab 1: Handle PDF Upload
    with tab1:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file is not None:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()  # Extract text from each page
            st.write("### Extracted Text from PDF:")
            st.write(text)  # Display extracted text

    # Tab 2: Handle Manual Entry
    with tab2:
        text = st.text_area("Enter company profile data here:")
        if text.strip() != "":
            st.write("### Entered Company Profile Data:")
            st.write(text)  # Display entered text
                
    return text            
#capability_profile = st.sidebar.text_area("Enter your company's capability details:")

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

def fetch_tenders_from_state():
    
    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get('https://etenders.gov.in/eprocure/app?page=FrontEndListTendersbyDate&service=page')

    # Interact with dropdown menu or select element
    #dropdown = driver.find_element('xpath', 'your_dropdown_xpath')
    #dropdown.click()

    # Choose an option  
    option = driver.find_element('xpath','/html/body/div/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[8]/td/table/tbody/tr/td/div/ul/li[3]/a')
    option.click()

    # Extract the updated HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Locate the table (adjust selectors based on the actual HTML structure)
    table = soup.find('table', attrs={'class': 'list_table', 'id': 'table'})  # Locate the table with the correct tag and class
        
    # Extract table headers
    #headers = [header.text.strip() for header in table.find('tr', class_='list_header')]


    # Locate and scrape the table
    #table = soup.find('table', id='your_table_id')
    data = []
    if table is None:
        print("No table found in the HTML content.")
        return []  # or handle accordingly

    for row in table.find_all('tr'):
        columns = row.find_all('td')
        data.append([col.text.strip() for col in columns])

    # Close the driver
    driver.quit()
    return data

def match_tenders(tenders, profile):
    vectorizer = TfidfVectorizer()
    tenders.loc[tenders['Title'].notna(), 'Title'] = tenders['Title'].dropna().astype(str)
    tender_texts = tenders['Title'] + " " + tenders['scope_days'].astype(str)
    # Replace NaN values with an empty string
    tender_texts = tender_texts.fillna('')
    # Create TF-IDF vectors for the profile and tenders

    profile_vector = vectorizer.fit_transform([profile])
    tender_vectors = vectorizer.transform(tender_texts)
    scores = cosine_similarity(profile_vector, tender_vectors).flatten()
    tenders['Match Score'] = scores
    return tenders.sort_values(by='Match Score', ascending=False)


# Optional: SMS Notifications via Twilio
def send_sms(tenders):
    sender_number = st.sidebar.text_input("Sender Number", "+919789547698")
    account_sid = 'ACbbf0841bda20a2b267bea1a86fb58cff'
    auth_token = '84f3310c8e9c817a4e6e15b0c9812568'
    client = Client(account_sid, auth_token)
    if not tenders.empty:
        for _, tender in tenders.iterrows():
            message = f"Subject: New Matched Tender\n\nNew tender found: {tender['Title']}"
            client.messages.create(
            messaging_service_sid='MG55554f1bd534423eae9beef1782d5101',
            body=message,
            to=sender_number
            )
    else:
        st.sidebar.write("No tenders to send.")

# Optional: Email Notifications via Gmail SMTP
def send_email(tenders):
    sender_email = "thigazh66@gmail.com"
    receiver_email = st.sidebar.text_input("Receiver Email", "umaselvaraj257@gmail.com")
    password = "lrpe edle jkrf jbgi"
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

# Main App Functionality     
           
text = getting_company_profile()
st.sidebar.write("Fetching tenders...")
# Fetch tenders from the website
tenders_df = fetch_tenders()
new_columns = ['Bid_Closing_Date','Tender Opening Date',
       'e-Published Date','Title','Organisation Name',
       'Corrigendum', 'GeM Availability Report Id', 'Download']
#tenders_df.columns = new_columns
tenders_df1 = tenders_df.drop(columns=['Corrigendum', 'GeM Availability Report Id', 'Download'], axis=1)
tenders_df2 = fetch_tenders_from_state()
# Example of converting a list of lists into a DataFrame
tenders_df2 = pd.DataFrame(tenders_df2, columns=['S.No','e-Published Date','Bid_Closing_Date','Tender Opening Date',
       'Title','Organisation Name'])
# Delete the first column
tenders_df2.drop(tenders_df2.index[0], inplace=True)

if tenders_df2.shape[1] > 0:
    tenders_df2 = tenders_df2.drop(tenders_df2.columns[0], axis=1)
tenders_df2.reset_index(drop=True, inplace=True)   
 
# Rename columns to match tenders_df1
tenders_df = pd.concat([tenders_df1, tenders_df2], ignore_index=True)
st.sidebar.write("Tenders fetched successfully!")

# Fetch tenders from the website
st.header("Aggregated Tenders")
#tenders_df = fetch_tenders()
st.write(tenders_df)


# Step 1: Convert object-type columns to datetime

tenders_df["Tender Opening Date"] = pd.to_datetime(tenders_df["Tender Opening Date"], dayfirst=True, errors='coerce')
tenders_df["Bid_Closing_Date"] = pd.to_datetime(tenders_df["Bid_Closing_Date"])

# Step 2: Calculate the scope (duration in days)
tenders_df["scope_days"] = (tenders_df["Bid_Closing_Date"] - tenders_df["Tender Opening Date"])

# Matching tenders to company profile

if text:
    matched_tenders = match_tenders(tenders_df, text)
    st.header("Matched Tenders")
    st.write(matched_tenders)

if st.sidebar.button("Send SMS Alerts"):
    send_sms(matched_tenders)
    st.sidebar.write("SMS alerts sent!")
        
if st.sidebar.button("Send Email Alerts"):
    if text:
        send_email(matched_tenders)
        