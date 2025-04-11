import streamlit as st
from geopy.distance import geodesic
import datetime
import time
import random
import urllib.parse
import qrcode
from io import BytesIO
import json
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
import hashlib
from PIL import Image
import io
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
import pytz
import smtplib
from email.mime.text import MIMEText
import threading
import queue

# Hospitals data (unchanged)
hospitals = [
    {
        "name": "Apollo Speciality Hospitals",
        "address": "16/111/1133, Muttukur Road, Pinakini Nagar, Nellore, Andhra Pradesh 524004",
        "coordinates": (14.4420, 79.9850),
        "phone": "0861-2345700",
        "beds": 200,
        "specialties": ["Cardiology", "Neurology"],
        "doctors": {"Cardiology": ["Dr. John Smith", "Dr. Priya Sharma"],
                    "Neurology": ["Dr. Anil Kumar", "Dr. Sarah Lee"]},
        "rating": 4.5,
        "wait_time": 15,
        "emergency_services": True,
        "reviews": 120,
        "availability": "24/7"
    },
    {
        "name": "Narayana Medical College Hospital",
        "address": "Chinthareddypalem, Nellore, Andhra Pradesh 524003",
        "coordinates": (14.4560, 79.9730),
        "phone": "0861-2317963",
        "beds": 500,
        "specialties": ["Pediatrics", "Oncology"],
        "doctors": {"Pediatrics": ["Dr. Ravi Patel", "Dr. Meena Gupta"],
                    "Oncology": ["Dr. Sanjay Rao", "Dr. Linda Chen"]},
        "rating": 4.7,
        "wait_time": 20,
        "emergency_services": True,
        "reviews": 200,
        "availability": "24/7"
    },
    {
        "name": "Simhapuri Hospitals",
        "address": "NH-5, Chinthareddypalem Crossroad, Nellore, Andhra Pradesh 524002",
        "coordinates": (14.4570, 79.9720),
        "phone": "0861-2339090",
        "beds": 150,
        "specialties": ["Orthopedics", "Gastroenterology"],
        "doctors": {"Orthopedics": ["Dr. Vikram Singh", "Dr. Emily Brown"],
                    "Gastroenterology": ["Dr. Arjun Reddy", "Dr. Clara Jones"]},
        "rating": 4.2,
        "wait_time": 10,
        "emergency_services": False,
        "reviews": 80,
        "availability": "9 AM - 9 PM"
    },
    {
        "name": "KIMS Nellore",
        "address": "Ambedkar Nagar, Nellore, Andhra Pradesh 524003",
        "coordinates": (14.4490, 79.9870),
        "phone": "0861-2315835",
        "beds": 250,
        "specialties": ["Urology", "Nephrology"],
        "doctors": {"Urology": ["Dr. Mohan Das", "Dr. Lisa White"], "Nephrology": ["Dr. Rajesh Nair", "Dr. David Kim"]},
        "rating": 4.4,
        "wait_time": 25,
        "emergency_services": True,
        "reviews": 150,
        "availability": "24/7"
    },
    {
        "name": "Government General Hospital",
        "address": "Pogathota, Nellore, Andhra Pradesh 524001",
        "coordinates": (14.4410, 79.9790),
        "phone": "0861-2327100",
        "beds": 700,
        "specialties": ["General Medicine", "Surgery"],
        "doctors": {"General Medicine": ["Dr. Suresh Babu", "Dr. Mary Thomas"],
                    "Surgery": ["Dr. Krishna Murthy", "Dr. James Wilson"]},
        "rating": 3.8,
        "wait_time": 30,
        "emergency_services": True,
        "reviews": 300,
        "availability": "24/7"
    }
]

nellore_center = (14.4426, 79.9865)
base_css = """
    <style>
    .ios-button {background-color: #007AFF; color: white; padding: 10px 20px; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; width: 100%; max-width: 200px; margin: 5px 0; transition: background-color 0.3s, transform 0.2s;}
    .ios-button:hover {background-color: #005BB5; transform: scale(1.05);}
    .ios-button:active {background-color: #003087; transform: scale(0.95);}
    .call-button {background-color: #34C759;}
    .call-button:hover {background-color: #28A745;}
    .call-button:active {background-color: #1E7E34;}
    .favorite-button {background-color: #FF9500;}
    .favorite-button:hover {background-color: #E87B00;}
    .favorite-button:active {background-color: #CC6B00;}
    .whatsapp-button {background-color: #25D366;}
    .whatsapp-button:hover {background-color: #20B85A;}
    .whatsapp-button:active {background-color: #1A9D4E;}
    @keyframes fadeIn {from {opacity: 0;} to {opacity: 1;}}
    .fade-in {animation: fadeIn 0.5s ease-in;}
    .metric-card {background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center;}
    .dark-mode .metric-card {background-color: #333333;}
    .stChat {background-color: #f9f9f9; padding: 10px; border-radius: 10px; margin: 5px 0;}
    .dark-mode .stChat {background-color: #2A2A2A;}
    .highlight {background-color: #FFFF99; padding: 2px;}
    </style>
"""
dark_mode_css = """
    <style>
    html, body, [data-testid="stApp"] {background-color: #1A1A1A !important; color: white !important;}
    [data-testid="stHeader"] {background-color: #1A1A1A !important;}
    [data-testid="stSidebar"] {background-color: #2A2A2A !important;}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {background-color: #333333 !important; color: white !important;}
    [data-testid="stExpander"] {background-color: #2A2A2A !important;}
    </style>
"""


# Helper functions
def get_simulated_weather():
    conditions = ["Sunny ☀️", "Cloudy ☁️", "Rainy 🌧️", "Windy 🌬️"]
    temp = random.randint(25, 35)
    return f"{random.choice(conditions)}, {temp}°C"


def get_whatsapp_share_url(lat, lon):
    message = f"My location: https://www.google.com/maps?q={lat},{lon}"
    return f"https://wa.me/?text={urllib.parse.quote(message)}"


def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# Email Queue System
email_queue = queue.Queue()


def send_email_alert(to_email, subject, body, language="English"):
    sender = st.session_state.email_credentials.get("sender", "")
    password = st.session_state.email_credentials.get("password", "")

    if not sender or not password:
        st.error("❌ Email sender credentials not set. Please configure in Settings.")
        email_queue.put((to_email, subject, body, language))  # Queue for retry
        return False

    # Multi-language support
    if language == "Telugu":
        translations = {
            "Dear": "ప్రియమైన",
            "Your appointment has been successfully booked!": "మీ అపాయింట్‌మెంట్ విజయవంతంగా బుక్ చేయబడింది!",
            "Details": "వివరాలు",
            "Hospital": "ఆసుపత్రి",
            "Date": "తేదీ",
            "Time": "సమయం",
            "Doctor": "డాక్టర్",
            "Specialty": "ప్రత్యేకత",
            "Notes": "నోట్స్",
            "Payment Amount": "చెల్లింపు మొత్తం",
            "Payment Method": "చెల్లింపు పద్ధతి",
            "Payment Status": "చెల్లింపు స్థితి",
            "Thank you for using Nellore Hospital Hub!": "నెల్లూరు హాస్పిటల్ హబ్‌ని ఉపయోగించినందుకు ధన్యవాదాలు!",
            "Appointment Cancellation": "అపాయింట్‌మెంట్ రద్దు",
            "Your appointment has been cancelled.": "మీ అపాయింట్‌మెంట్ రద్దు చేయబడింది।"
        }
        for eng, tel in translations.items():
            body = body.replace(eng, tel)

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            st.session_state.history_log.append(
                f"Email sent to {to_email} at {datetime.datetime.now().strftime('%H:%M:%S, %d %B %Y')}")
            return True
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Authentication failed. Verify your sender email and App Password in Settings.")
        email_queue.put((to_email, subject, body, language))  # Queue for retry
        return False
    except smtplib.SMTPRecipientsRefused:
        st.error(f"❌ Recipient email refused: {to_email}. Check if the email address is valid.")
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP error: {str(e)}. Check your internet or Gmail settings.")
        email_queue.put((to_email, subject, body, language))  # Queue for retry
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}. Please try again.")
        email_queue.put((to_email, subject, body, language))  # Queue for retry
        return False


def retry_queued_emails():
    while not email_queue.empty():
        to_email, subject, body, language = email_queue.get()
        st.warning(f"Retrying email to {to_email}...")
        success = send_email_alert(to_email, subject, body, language)
        if success:
            st.info(f"📧 Queued email sent to {to_email}!")
        else:
            st.error(f"⚠️ Retry failed for {to_email}. Remains in queue.")
        time.sleep(1)  # Avoid overwhelming the server


def test_email_credentials():
    sender = st.session_state.email_credentials.get("sender", "")
    test_email = st.session_state.email_address or sender
    if not test_email:
        st.error("❌ No email address provided for testing.")
        return
    with st.spinner("Testing email credentials..."):
        success = send_email_alert(test_email, "Test Email from Nellore Hospital Hub",
                                   "This is a test email to verify your sender credentials.")
        if success:
            st.success(f"✅ Test email sent to {test_email}! Check your inbox.")
        else:
            st.error("❌ Test failed. Check your sender credentials.")


def simulate_payment(amount, method):
    with st.spinner(f"Processing payment of ₹{amount} via {method}..."):
        time.sleep(2)
    return True


def get_chatbot_response(message, hospitals):
    message = message.lower().strip()
    responses = {
        "hi": "Hello! How can I assist you today?",
        "emergency": "For emergencies, call 108 or use the SOS button on the Home tab.",
        "hospitals": "Here are the hospitals in Nellore:\n" + "\n".join(
            [f"- {h['name']} (Rating: {h['rating']}, Wait: {h['wait_time']} min, Availability: {h['availability']})" for
             h in hospitals]),
        "weather": f"Current simulated weather in Nellore: {get_simulated_weather()}",
        "nearest": f"The nearest hospital is {min(hospitals, key=lambda h: geodesic(st.session_state.user_location, h['coordinates']).km)['name']} ({geodesic(st.session_state.user_location, min(hospitals, key=lambda h: geodesic(st.session_state.user_location, h['coordinates']).km)['coordinates']).km:.2f} km).",
        "help": "I can help with: 'hi', 'emergency', 'hospitals', 'weather', 'nearest', 'beds', 'specialty <name>', 'wait time <hospital>', 'emergency services', 'reviews <hospital>', 'availability <hospital>', 'distance <hospital>'"
    }
    if message in responses:
        return responses[message]
    elif "beds" in message:
        return f"Total available beds: {sum(h['beds'] for h in hospitals if st.session_state.hospital_status[h['name']])}"
    elif "specialty" in message:
        specialty = message.replace("specialty", "").strip()
        matching = [h['name'] for h in hospitals if specialty in h['specialties']]
        return f"Hospitals with {specialty}: {', '.join(matching) if matching else 'None found'}" if specialty else "Please specify a specialty (e.g., 'specialty Cardiology')."
    elif "wait time" in message:
        hospital_name = message.replace("wait time", "").strip()
        for h in hospitals:
            if hospital_name.lower() in h['name'].lower():
                return f"Estimated wait time at {h['name']}: {h['wait_time']} minutes"
        return "Hospital not found."
    elif "emergency services" in message:
        emergency_hospitals = [h['name'] for h in hospitals if h['emergency_services']]
        return f"Hospitals with emergency services: {', '.join(emergency_hospitals)}"
    elif "reviews" in message:
        hospital_name = message.replace("reviews", "").strip()
        for h in hospitals:
            if hospital_name.lower() in h['name'].lower():
                return f"{h['name']} has {h['reviews']} reviews."
        return "Hospital not found."
    elif "availability" in message:
        hospital_name = message.replace("availability", "").strip()
        for h in hospitals:
            if hospital_name.lower() in h['name'].lower():
                return f"{h['name']} is available: {h['availability']}"
        return "Hospital not found."
    elif "distance" in message:
        hospital_name = message.replace("distance", "").strip()
        for h in hospitals:
            if hospital_name.lower() in h['name'].lower():
                return f"Distance to {h['name']}: {geodesic(st.session_state.user_location, h['coordinates']).km:.2f} km"
        return "Hospital not found."
    else:
        return "Sorry, I didn’t understand. Type 'help' for commands!"


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Image.Image):
            return "Image data (not serialized)"
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        return json.JSONEncoder.default(self, obj)


def main():
    # Session state initialization (updated with new keys)
    for key, default in [("dark_mode", False), ("favorites", set()),
                         ("hospital_status", {h["name"]: True for h in hospitals}),
                         ("user_name", ""), ("emergency_contact", ""), ("notifications", True),
                         ("selected_specialty", "All"),
                         ("chat_history", []), ("search_history", []), ("theme_color", "#007AFF"), ("font_size", 16),
                         ("alert_threshold", 5), ("user_location", nellore_center), ("notes", ""), ("history_log", []),
                         ("show_tooltips", True), ("auto_refresh", False), ("email_alerts", False),
                         ("email_address", ""),
                         ("voice_mode", False), ("hospital_notes", {h["name"]: "" for h in hospitals}),
                         ("alert_sound", False),
                         ("custom_alert_message", "Low beds detected!"), ("data_export_format", "JSON"),
                         ("password", ""),
                         ("logged_in", False), ("highlight_favorites", False), ("show_map", False),
                         ("wait_time_alert", 20),
                         ("review_filter", 0), ("distance_filter", 10.0),
                         ("rating_history", {h["name"]: [h["rating"]] for h in hospitals}),
                         ("custom_css", ""), ("emergency_priority", False), ("offline_mode", False),
                         ("profile_pic", None),
                         ("notification_delay", 2), ("backup_data", ""), ("weather_alerts", False),
                         ("language", "English"),
                         ("timezone", "Asia/Kolkata"), ("hospital_reviews", {h["name"]: [] for h in hospitals}),
                         ("map_zoom", 12),
                         ("weather_api_key", ""), ("email_credentials", {"sender": "", "password": ""}),
                         ("appointment_bookings", []),
                         ("news_feed", []), ("accessibility_mode", False), ("color_blind_mode", False),
                         ("hospital_images", {h["name"]: None for h in hospitals}),
                         ("search_suggestions", True), ("multi_user", False),
                         ("user_roles", {"admin": set(), "user": set()}),
                         ("data_refresh_interval", 300), ("chatbot_memory", 5), ("alert_history", []),
                         ("user_preferences", {}),
                         ("live_tracking", False), ("emergency_contacts_list", []),
                         ("hospital_ratings_comments", {h["name"]: [] for h in hospitals}),
                         ("appointment_reminders", True), ("email_retry_thread", None)]:
        if key not in st.session_state:
            st.session_state[key] = default

    st.set_page_config(page_title="Nellore Hospital Hub", layout="wide", initial_sidebar_state="expanded")

    # Login system (unchanged)
    if not st.session_state.logged_in:
        st.title("🔒 Login to Nellore Hospital Hub")
        username = st.text_input("Username", value=st.session_state.user_name)
        password_input = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            hashed_input = hashlib.sha256(password_input.encode()).hexdigest()
            if st.session_state.password == "" or hashed_input == st.session_state.password:
                st.session_state.logged_in = True
                st.session_state.user_name = username
                if "admin" in st.session_state.user_roles and username in st.session_state.user_roles["admin"]:
                    st.session_state.user_preferences["role"] = "admin"
                else:
                    st.session_state.user_roles["user"].add(username)
                    st.session_state.user_preferences["role"] = "user"
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Incorrect password!")
        return

    # Sidebar controls (updated with email test button)
    st.sidebar.header("Settings")
    st.session_state.dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.notifications = st.sidebar.checkbox("🔔 Notifications", value=st.session_state.notifications)
    st.session_state.selected_specialty = st.sidebar.selectbox("🏥 Specialty Filter", ["All"] + sorted(
        set(s for h in hospitals for s in h["specialties"])),
                                                               index=0 if st.session_state.selected_specialty == "All" else 1)
    st.session_state.theme_color = st.sidebar.color_picker("🎨 Theme Color", value=st.session_state.theme_color)
    st.session_state.font_size = st.sidebar.slider("🔤 Font Size", 12, 24, st.session_state.font_size)
    st.session_state.alert_threshold = st.sidebar.slider("🚨 Low Bed Alert Threshold", 0, 50,
                                                         st.session_state.alert_threshold)
    st.session_state.wait_time_alert = st.sidebar.slider("⏳ Wait Time Alert (min)", 5, 60,
                                                         st.session_state.wait_time_alert)
    st.session_state.distance_filter = st.sidebar.slider("📏 Max Distance (km)", 1.0, 20.0,
                                                         st.session_state.distance_filter)
    st.session_state.review_filter = st.sidebar.slider("📝 Min Reviews", 0, 500, st.session_state.review_filter)
    st.session_state.show_tooltips = st.sidebar.checkbox("ℹ️ Show Tooltips", value=st.session_state.show_tooltips)
    st.session_state.auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh", value=st.session_state.auto_refresh)
    st.session_state.email_alerts = st.sidebar.checkbox("📧 Email Alerts", value=st.session_state.email_alerts)
    st.sidebar.subheader("Email Settings")
    st.session_state.email_address = st.sidebar.text_input("Your Email (Optional)",
                                                           value=st.session_state.email_address,
                                                           placeholder="Enter your email")
    st.session_state.email_credentials["sender"] = st.sidebar.text_input("Sender Email",
                                                                         value=st.session_state.email_credentials[
                                                                             "sender"],
                                                                         placeholder="your_email@gmail.com")
    st.session_state.email_credentials["password"] = st.sidebar.text_input("Sender Password", type="password",
                                                                           value=st.session_state.email_credentials[
                                                                               "password"],
                                                                           placeholder="App-specific password")
    if st.sidebar.button("Test Email Credentials"):
        test_email_credentials()
    if st.sidebar.button("Retry Queued Emails") and not email_queue.empty():
        if not st.session_state.email_retry_thread or not st.session_state.email_retry_thread.is_alive():
            st.session_state.email_retry_thread = threading.Thread(target=retry_queued_emails)
            st.session_state.email_retry_thread.start()
    st.session_state.voice_mode = st.sidebar.checkbox("🎙️ Voice Mode", value=st.session_state.voice_mode)
    st.session_state.alert_sound = st.sidebar.checkbox("🔊 Alert Sound", value=st.session_state.alert_sound)
    st.session_state.custom_alert_message = st.sidebar.text_input("Custom Alert Message",
                                                                  value=st.session_state.custom_alert_message)
    st.session_state.highlight_favorites = st.sidebar.checkbox("🌟 Highlight Favorites",
                                                               value=st.session_state.highlight_favorites)
    st.session_state.show_map = st.sidebar.checkbox("🗺️ Show Mini Map", value=st.session_state.show_map)
    st.session_state.emergency_priority = st.sidebar.checkbox("🚑 Prioritize Emergency Services",
                                                              value=st.session_state.emergency_priority)
    st.session_state.offline_mode = st.sidebar.checkbox("📴 Offline Mode", value=st.session_state.offline_mode)
    st.session_state.weather_alerts = st.sidebar.checkbox("🌧️ Weather Alerts", value=st.session_state.weather_alerts)
    st.session_state.notification_delay = st.sidebar.slider("⏲️ Notification Delay (sec)", 1, 10,
                                                            st.session_state.notification_delay)
    st.session_state.language = st.sidebar.selectbox("🌐 Language", ["English", "Telugu"],
                                                     index=0 if st.session_state.language == "English" else 1)
    st.session_state.timezone = st.sidebar.selectbox("⏰ Timezone", ["Asia/Kolkata", "UTC"],
                                                     index=0 if st.session_state.timezone == "Asia/Kolkata" else 1)
    st.session_state.map_zoom = st.sidebar.slider("🔍 Map Zoom", 10, 15, st.session_state.map_zoom)
    st.session_state.weather_api_key = st.sidebar.text_input("🌤️ Weather API Key",
                                                             value=st.session_state.weather_api_key,
                                                             placeholder="OpenWeatherMap API Key")
    st.session_state.accessibility_mode = st.sidebar.checkbox("♿ Accessibility Mode",
                                                              value=st.session_state.accessibility_mode)
    st.session_state.color_blind_mode = st.sidebar.checkbox("🎨 Color Blind Mode",
                                                            value=st.session_state.color_blind_mode)
    st.session_state.search_suggestions = st.sidebar.checkbox("🔍 Search Suggestions",
                                                              value=st.session_state.search_suggestions)
    st.session_state.data_refresh_interval = st.sidebar.slider("🔄 Data Refresh Interval (sec)", 60, 600,
                                                               st.session_state.data_refresh_interval)
    st.session_state.chatbot_memory = st.sidebar.slider("💬 Chatbot Memory (messages)", 1, 10,
                                                        st.session_state.chatbot_memory)
    st.session_state.appointment_reminders = st.sidebar.checkbox("📅 Appointment Reminders",
                                                                 value=st.session_state.appointment_reminders)

    # Dynamic CSS (unchanged)
    final_css = base_css
    if st.session_state.color_blind_mode:
        final_css = base_css.replace("#007AFF", "#FF6F61")
    dynamic_css = f"<style>.ios-button {{background-color: {st.session_state.theme_color};}} body {{font-size: {st.session_state.font_size}px;}} {st.session_state.custom_css}</style>"
    st.markdown(final_css, unsafe_allow_html=True)
    st.markdown(dynamic_css, unsafe_allow_html=True)
    if st.session_state.dark_mode:
        st.markdown(dark_mode_css, unsafe_allow_html=True)

    st.title("🏥 Nellore District Hospital Hub")

    # Quick stats (unchanged)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Hospitals", len(hospitals))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Available Beds", sum(h["beds"] for h in hospitals if st.session_state.hospital_status[h["name"]]))
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Favorites", len(st.session_state.favorites))
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Rating", round(sum(h["rating"] for h in hospitals) / len(hospitals), 1))
        st.markdown('</div>', unsafe_allow_html=True)

    # Alerts (unchanged)
    tz = pytz.timezone(st.session_state.timezone)
    current_time = datetime.datetime.now(tz).strftime("%H:%M:%S, %d %B %Y")
    current_datetime = datetime.datetime.now(tz)
    low_bed_hospitals = [h for h in hospitals if
                         h["beds"] < st.session_state.alert_threshold and st.session_state.hospital_status[h["name"]]]
    high_wait_hospitals = [h for h in hospitals if
                           h["wait_time"] > st.session_state.wait_time_alert and st.session_state.hospital_status[
                               h["name"]]]
    if low_bed_hospitals and st.session_state.notifications:
        alert_msg = f"🚨 {st.session_state.custom_alert_message}: {', '.join(h['name'] for h in low_bed_hospitals)} have fewer than {st.session_state.alert_threshold} beds!"
        st.warning(alert_msg)
        st.session_state.alert_history.append(f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}: {alert_msg}")
        if st.session_state.alert_sound:
            html(
                '<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>',
                height=0)
        if st.session_state.email_alerts and st.session_state.email_address:
            send_email_alert(st.session_state.email_address, "Low Bed Alert", alert_msg, st.session_state.language)
    if high_wait_hospitals and st.session_state.notifications:
        alert_msg = f"⏳ High wait time alert: {', '.join(h['name'] for h in high_wait_hospitals)} exceed {st.session_state.wait_time_alert} minutes!"
        st.warning(alert_msg)
        st.session_state.alert_history.append(f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}: {alert_msg}")
        if st.session_state.alert_sound:
            html(
                '<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>',
                height=0)
    if st.session_state.weather_alerts and "Rainy" in get_simulated_weather() and st.session_state.notifications:
        alert_msg = "🌧️ Weather alert: Rainy conditions in Nellore!"
        st.warning(alert_msg)
        st.session_state.alert_history.append(f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}: {alert_msg}")
    if st.session_state.appointment_reminders and st.session_state.notifications:
        for booking in st.session_state.appointment_bookings:
            appt_datetime = datetime.datetime.strptime(f"{booking['date']} {booking['time']}",
                                                       "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            time_diff = (appt_datetime - current_datetime).total_seconds() / 3600
            if 0 < time_diff <= 24 and booking.get("status", "Pending") == "Confirmed":
                payment_status = "Paid" if booking.get("payment_status", False) else "Unpaid (Cash on Arrival)" if \
                booking["payment_method"] == "Cash on Arrival" else "Unpaid"
                alert_msg = f"📅 Reminder: Appointment with {booking['doctor']} at {booking['hospital']} on {booking['date']} at {booking['time']} is in {time_diff:.1f} hours! Payment: {payment_status}"
                st.info(alert_msg)
                st.session_state.alert_history.append(f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}: {alert_msg}")
                if st.session_state.email_alerts and st.session_state.email_address:
                    send_email_alert(st.session_state.email_address, "Appointment Reminder", alert_msg,
                                     st.session_state.language)

    tabs = st.tabs(["🏠 Home", "🏥 Hospitals", "👤 Profile", "💬 Chat", "📊 Analytics", "⚙️ Advanced", "📰 News"])

    with tabs[0]:  # Home Tab (unchanged)
        st.subheader("⏰ Time & Date")
        time_placeholder = st.empty()
        time_placeholder.write(f"**Time**: {current_time} ⏳")
        st.subheader("🌤️ Weather in Nellore")
        weather = get_simulated_weather()
        st.write(f"**Conditions**: {weather}")
        st.subheader("🚨 Emergency Assistance")
        if st.button("Emergency SOS 🚑", key="sos_button",
                     help="Simulate an emergency call" if st.session_state.show_tooltips else None):
            with st.spinner("📞 Initiating call..."):
                time.sleep(1)
            st.markdown('<div class="ios-button fade-in">Calling 108...</div>', unsafe_allow_html=True)
            st.success("✅ Simulated call to 108 initiated!")
            st.session_state.history_log.append(f"Emergency SOS called at {current_time}")
            if st.session_state.notifications:
                time.sleep(st.session_state.notification_delay)
                st.toast("🚨 Emergency SOS activated!", icon="⚠️")
            if st.session_state.email_alerts and st.session_state.email_address:
                success = send_email_alert(st.session_state.email_address, "Emergency SOS", "SOS activated!",
                                           st.session_state.language)
                st.info(
                    f"📧 {'Simulated email' if not success else 'Email'} alert sent to {st.session_state.email_address}")
        st.subheader("ℹ️ Quick Tips")
        tips = ["Keep emergency numbers handy", "Stay hydrated", "Know your nearest hospital"]
        for tip in tips:
            st.write(f"- {tip}")
        st.subheader("📅 Last Updated")
        st.write(f"Data last updated: {datetime.datetime.now(tz).strftime('%d %B %Y, %H:%M:%S')}")
        st.subheader("📍 Live Location Tracking")
        if st.session_state.live_tracking:
            st.write("Tracking enabled (simulated). Update your location in Profile.")

    with tabs[1]:  # Hospitals Tab (updated with status and cancellation email)
        st.subheader("🏥 Hospitals in Nellore District")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search_query = st.text_input("🔍 Search Hospitals", placeholder="Enter hospital name", key="hospital_search",
                                         help="Search by hospital name" if st.session_state.show_tooltips else None)
            if st.session_state.search_suggestions and search_query:
                suggestions = [h["name"] for h in hospitals if search_query.lower() in h["name"].lower()]
                if suggestions:
                    st.write("Suggestions:", ", ".join(suggestions[:3]))
            if search_query and search_query not in st.session_state.search_history:
                st.session_state.search_history.append(search_query)
        with col2:
            sort_by_distance = st.checkbox("📏 Sort by Distance",
                                           help="Sort by proximity" if st.session_state.show_tooltips else None)
        with col3:
            sort_by_rating = st.checkbox("⭐ Sort by Rating",
                                         help="Sort by user rating" if st.session_state.show_tooltips else None)

        filtered_hospitals = [h for h in hospitals if
                              (search_query.lower() in h["name"].lower() or not search_query) and
                              (st.session_state.selected_specialty == "All" or st.session_state.selected_specialty in h[
                                  "specialties"]) and
                              geodesic(st.session_state.user_location,
                                       h["coordinates"]).km <= st.session_state.distance_filter and
                              h["reviews"] >= st.session_state.review_filter]
        if st.session_state.emergency_priority:
            filtered_hospitals = [h for h in filtered_hospitals if h["emergency_services"]]
        if sort_by_distance:
            filtered_hospitals.sort(key=lambda h: geodesic(st.session_state.user_location, h["coordinates"]).km)
        elif sort_by_rating:
            filtered_hospitals.sort(key=lambda h: h["rating"], reverse=True)

        if st.session_state.show_map:
            m = folium.Map(location=nellore_center, zoom_start=st.session_state.map_zoom)
            for h in filtered_hospitals:
                folium.Marker(h["coordinates"], popup=h["name"]).add_to(m)
            folium.Marker(st.session_state.user_location, popup="You", icon=folium.Icon(color="red")).add_to(m)
            st_folium(m, width=700, height=400)

        for hospital in filtered_hospitals:
            title = f"**{hospital['name']}** {'🟢 Open' if st.session_state.hospital_status[hospital['name']] else '🔴 Closed'}"
            if hospital["name"] in st.session_state.favorites and st.session_state.highlight_favorites:
                title = f'<span class="highlight">{title}</span>'
            with st.expander(title, expanded=False):
                distance_km = geodesic(st.session_state.user_location, hospital["coordinates"]).km
                st.write(f"**Address**: {hospital['address']} 📍")
                st.write(f"**Phone**: {hospital['phone']} 📞")
                st.write(f"**Distance**: {distance_km:.2f} km 🚶")
                st.write(f"**Beds**: {hospital['beds']}")
                st.write(f"**Specialties**: {', '.join(hospital['specialties'])}")
                st.write(f"**Rating**: {hospital['rating']} / 5 ⭐")
                st.write(f"**Wait Time**: {hospital['wait_time']} minutes")
                st.write(f"**Emergency Services**: {'Yes' if hospital['emergency_services'] else 'No'} 🚑")
                st.write(f"**Reviews**: {hospital['reviews']}")
                st.write(f"**Availability**: {hospital['availability']}")
                st.session_state.hospital_status[hospital["name"]] = st.checkbox("Open Now",
                                                                                 value=st.session_state.hospital_status[
                                                                                     hospital["name"]],
                                                                                 key=f"status_{hospital['name']}",
                                                                                 help="Toggle hospital status" if st.session_state.show_tooltips else None)
                st.session_state.hospital_notes[hospital["name"]] = st.text_area(f"Notes for {hospital['name']}",
                                                                                 value=st.session_state.hospital_notes[
                                                                                     hospital["name"]], height=100,
                                                                                 help="Add notes for this hospital" if st.session_state.show_tooltips else None)

                new_rating = st.slider(f"Update Rating for {hospital['name']}", 0.0, 5.0, hospital["rating"], step=0.1,
                                       key=f"rating_{hospital['name']}")
                if new_rating != hospital["rating"]:
                    hospital["rating"] = new_rating
                    st.session_state.rating_history[hospital["name"]].append(new_rating)
                    st.session_state.history_log.append(
                        f"Updated rating for {hospital['name']} to {new_rating} at {current_time}")

                review_comment = st.text_input(f"Add Review for {hospital['name']}", key=f"review_{hospital['name']}")
                if st.button(f"Submit Review", key=f"submit_review_{hospital['name']}") and review_comment:
                    st.session_state.hospital_reviews[hospital["name"]].append(
                        {"user": st.session_state.user_name, "comment": review_comment, "time": current_time})
                    st.session_state.hospital_ratings_comments[hospital["name"]].append(review_comment)
                    hospital["reviews"] += 1
                    st.success("✅ Review submitted!")

                if st.session_state.hospital_reviews[hospital["name"]]:
                    st.write("**Recent Reviews**:")
                    for rev in st.session_state.hospital_reviews[hospital["name"]][-3:]:
                        st.write(f"- {rev['user']}: {rev['comment']} ({rev['time']})")

                lat, lon = hospital["coordinates"]
                google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(
                    f'<a href="{google_maps_url}" target="_blank" class="ios-button fade-in">Get Directions 🗺️</a>',
                    unsafe_allow_html=True)

                hospital_image = st.file_uploader(f"Upload Image for {hospital['name']}", type=["jpg", "png"],
                                                  key=f"image_{hospital['name']}")
                if hospital_image:
                    st.session_state.hospital_images[hospital["name"]] = Image.open(hospital_image)
                if st.session_state.hospital_images[hospital["name"]]:
                    st.image(st.session_state.hospital_images[hospital["name"]], caption=f"{hospital['name']} Image",
                             width=200)

                # Appointment Booking with Status
                st.subheader(f"📅 Book Appointment at {hospital['name']}")
                with st.form(f"appointment_{hospital['name']}", clear_on_submit=True):
                    appt_date = st.date_input("Appointment Date", key=f"date_{hospital['name']}")
                    appt_time = st.time_input("Appointment Time", key=f"time_{hospital['name']}")
                    appt_specialty = st.selectbox("Specialty", hospital["specialties"],
                                                  key=f"specialty_{hospital['name']}")
                    appt_doctor = st.selectbox("Doctor", hospital["doctors"][appt_specialty],
                                               key=f"doctor_{hospital['name']}")
                    appt_notes = st.text_area("Appointment Notes", placeholder="e.g., Reason for visit",
                                              key=f"notes_{hospital['name']}")
                    appointment_cost = 500
                    st.write(f"**Appointment Cost**: ₹{appointment_cost}")
                    payment_method = st.selectbox("Payment Method", ["UPI", "Credit/Debit Card", "Cash on Arrival"],
                                                  key=f"payment_{hospital['name']}")
                    appt_email = st.text_input("Your Email for Confirmation (Required)",
                                               value=st.session_state.email_address, key=f"email_{hospital['name']}")
                    submit_appt = st.form_submit_button("Book Appointment")
                    if submit_appt:
                        if not appt_email:
                            st.error("❌ Please provide an email address for confirmation!")
                        else:
                            appt_datetime = datetime.datetime.combine(appt_date, appt_time).replace(tzinfo=tz)
                            if hospital["availability"] != "24/7" and (appt_time.hour < 9 or appt_time.hour >= 21):
                                st.warning(
                                    f"⚠️ {hospital['name']} is only available from 9 AM to 9 PM. Please adjust time.")
                            else:
                                booking = {
                                    "hospital": hospital["name"],
                                    "date": str(appt_date),
                                    "time": str(appt_time),
                                    "specialty": appt_specialty,
                                    "doctor": appt_doctor,
                                    "notes": appt_notes,
                                    "user": st.session_state.user_name,
                                    "confirmed": False,
                                    "payment_amount": appointment_cost,
                                    "payment_method": payment_method,
                                    "payment_status": False,
                                    "email": appt_email,
                                    "status": "Pending"  # New status field
                                }
                                if payment_method != "Cash on Arrival":
                                    if st.checkbox("Confirm Payment", key=f"pay_{hospital['name']}"):
                                        payment_success = simulate_payment(appointment_cost, payment_method)
                                        if payment_success:
                                            booking["payment_status"] = True
                                            st.success(
                                                f"✅ Payment of ₹{appointment_cost} via {payment_method} completed!")
                                        else:
                                            st.error("❌ Payment failed. Please try again.")
                                            return
                                if st.checkbox("Confirm Booking", key=f"confirm_{hospital['name']}"):
                                    booking["confirmed"] = True
                                    booking["status"] = "Confirmed"
                                    st.session_state.appointment_bookings.append(booking)
                                    payment_status = "Paid" if booking[
                                        "payment_status"] else "Unpaid (Cash on Arrival)" if payment_method == "Cash on Arrival" else "Unpaid"
                                    st.success(
                                        f"✅ Appointment booked with {appt_doctor} at {hospital['name']} on {appt_date} at {appt_time} for {appt_specialty}! Payment: {payment_status}")
                                    st.session_state.history_log.append(
                                        f"Booked appointment with {appt_doctor} at {hospital['name']} for {appt_specialty} on {appt_date} at {appt_time}, Payment: {payment_status}")

                                    # Send Confirmation Email
                                    email_body = (
                                        f"Dear {st.session_state.user_name},\n\n"
                                        f"Your appointment has been successfully booked!\n\n"
                                        f"Details:\n"
                                        f"- Hospital: {hospital['name']}\n"
                                        f"- Date: {appt_date}\n"
                                        f"- Time: {appt_time}\n"
                                        f"- Doctor: {appt_doctor}\n"
                                        f"- Specialty: {appt_specialty}\n"
                                        f"- Notes: {appt_notes or 'None'}\n"
                                        f"- Payment Amount: ₹{appointment_cost}\n"
                                        f"- Payment Method: {payment_method}\n"
                                        f"- Payment Status: {payment_status}\n\n"
                                        f"Thank you for using Nellore Hospital Hub!"
                                    )
                                    with st.spinner("Sending confirmation email..."):
                                        email_success = send_email_alert(appt_email, "Appointment Confirmation",
                                                                         email_body, st.session_state.language)
                                        if email_success:
                                            st.info(f"📧 Confirmation email sent to {appt_email}!")
                                        else:
                                            st.warning(f"⚠️ Failed to send email to {appt_email}. Queued for retry.")

                if st.button(f"Call {hospital['name']} 📲", key=f"call_{hospital['name']}",
                             help="Simulate a call" if st.session_state.show_tooltips else None):
                    with st.spinner("📞 Connecting..."):
                        time.sleep(1)
                    st.markdown(f'<div class="ios-button call-button fade-in">Calling {hospital["phone"]}...</div>',
                                unsafe_allow_html=True)
                    st.info(f"ℹ️ Simulated call to {hospital["phone"]} initiated!")
                    st.session_state.history_log.append(f"Called {hospital['name']} at {current_time}")
                    if st.session_state.notifications:
                        time.sleep(st.session_state.notification_delay)
                        st.toast(f"📞 Calling {hospital['name']}!", icon="📱")

                is_favorite = hospital["name"] in st.session_state.favorites
                if st.button(f"{'Remove from' if is_favorite else 'Add to'} Favorites {'❤️' if is_favorite else '🤍'}",
                             key=f"favorite_{hospital['name']}",
                             help="Toggle favorite" if st.session_state.show_tooltips else None):
                    if is_favorite:
                        st.session_state.favorites.remove(hospital["name"])
                        st.success(f"❌ Removed {hospital['name']} from favorites!")
                    else:
                        st.session_state.favorites.add(hospital["name"])
                        st.success(f"✅ Added {hospital['name']} to favorites!")
                    st.session_state.history_log.append(
                        f"{'Removed' if is_favorite else 'Added'} {hospital['name']} to favorites at {current_time}")
                    if st.session_state.notifications:
                        time.sleep(st.session_state.notification_delay)
                        st.toast(f"❤️ Favorite updated: {hospital['name']}", icon="⭐")

        if st.session_state.favorites:
            st.subheader("❤️ Favorites")
            for fav in st.session_state.favorites:
                st.write(f"- {fav}")

        if st.session_state.search_history:
            st.subheader("🔍 Recent Searches")
            for search in st.session_state.search_history[-5:]:
                st.write(f"- {search}")

        st.subheader("📤 Export Hospital Data")
        export_format = st.selectbox("Export Format", ["JSON", "CSV"],
                                     index=0 if st.session_state.data_export_format == "JSON" else 1)
        if export_format == "JSON":
            hospital_data = json.dumps(filtered_hospitals, indent=2)
            mime = "application/json"
            file_name = "hospitals.json"
        else:
            hospital_data = pd.DataFrame(filtered_hospitals).to_csv(index=False)
            mime = "text/csv"
            file_name = "hospitals.csv"
        st.download_button("Download Hospital Data", data=hospital_data, file_name=file_name, mime=mime)

    with tabs[2]:  # Profile Tab (updated with dashboard and cancellation email)
        st.subheader("👤 User Profile")
        with st.form("profile_form"):
            st.session_state.user_name = st.text_input("Your Name", value=st.session_state.user_name,
                                                       placeholder="Enter your name",
                                                       help="Your display name" if st.session_state.show_tooltips else None)
            st.session_state.emergency_contact = st.text_input("Emergency Contact",
                                                               value=st.session_state.emergency_contact,
                                                               placeholder="Enter phone number",
                                                               help="Contact for emergencies" if st.session_state.show_tooltips else None)
            st.session_state.notes = st.text_area("Personal Notes", value=st.session_state.notes,
                                                  placeholder="Add any notes here",
                                                  help="Store personal reminders" if st.session_state.show_tooltips else None)
            profile_pic_file = st.file_uploader("Upload Profile Picture", type=["jpg", "png"],
                                                help="Add a profile image" if st.session_state.show_tooltips else None)
            if profile_pic_file:
                st.session_state.profile_pic = Image.open(profile_pic_file)
            new_password = st.text_input("Set/Change Password", type="password",
                                         placeholder="Leave blank to keep current",
                                         help="Set a login password" if st.session_state.show_tooltips else None)
            emergency_contacts_input = st.text_area("Emergency Contacts List (one per line)",
                                                    value="\n".join(st.session_state.emergency_contacts_list),
                                                    help="Add multiple contacts" if st.session_state.show_tooltips else None)
            if st.form_submit_button("Save Profile"):
                if new_password:
                    st.session_state.password = hashlib.sha256(new_password.encode()).hexdigest()
                st.session_state.emergency_contacts_list = [line.strip() for line in
                                                            emergency_contacts_input.split("\n") if line.strip()]
                st.success("✅ Profile saved!")
                st.session_state.history_log.append(f"Profile saved at {current_time}")
                if st.session_state.notifications:
                    time.sleep(st.session_state.notification_delay)
                    st.toast("👤 Profile updated!", icon="✅")

        if st.session_state.user_name and st.session_state.emergency_contact:
            st.write(f"**Welcome, {st.session_state.user_name}!** 🎉")
            st.write(f"**Primary Emergency Contact**: {st.session_state.emergency_contact} 📞")
            if st.session_state.emergency_contacts_list:
                st.write("**Additional Emergency Contacts**:")
                for contact in st.session_state.emergency_contacts_list:
                    st.write(f"- {contact}")
            if st.session_state.notes:
                st.write(f"**Notes**: {st.session_state.notes}")
            if st.session_state.profile_pic:
                st.image(st.session_state.profile_pic, caption="Profile Picture", width=200)

        # User Dashboard
        st.subheader("📈 Your Dashboard")
        appt_stats = {
            "Total Appointments": len(st.session_state.appointment_bookings),
            "Confirmed": len([b for b in st.session_state.appointment_bookings if b.get("status") == "Confirmed"]),
            "Pending": len([b for b in st.session_state.appointment_bookings if b.get("status") == "Pending"]),
            "Cancelled": len([b for b in st.session_state.appointment_bookings if b.get("status") == "Cancelled"])
        }
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Appointments", appt_stats["Total Appointments"])
        with col2:
            st.metric("Confirmed", appt_stats["Confirmed"])
        with col3:
            st.metric("Pending", appt_stats["Pending"])
        with col4:
            st.metric("Cancelled", appt_stats["Cancelled"])

        st.subheader("🛠️ Emergency Preparedness")
        checklist = "- Water (1L/person/day for 3 days) 💧\n- Non-perishable food (3-day supply) 🍞\n- First aid kit 🩺\n- Flashlight with batteries 🔦\n- Emergency contacts 📞\n- Blankets/clothing 🧥"
        st.download_button(label="Download Checklist 📥", data=checklist, file_name="emergency_checklist.txt",
                           mime="text/plain",
                           help="Download preparedness checklist" if st.session_state.show_tooltips else None)

        st.subheader("💬 Feedback")
        with st.form("feedback_form"):
            feedback = st.text_area("Tell us how we can improve! 😊", height=100,
                                    help="Share your suggestions" if st.session_state.show_tooltips else None)
            if st.form_submit_button("Submit Feedback ✉️") and feedback:
                st.success("🎉 Thank you for your feedback!")
                st.session_state.history_log.append(f"Feedback submitted at {current_time}")
                if st.session_state.notifications:
                    time.sleep(st.session_state.notification_delay)
                    st.toast("💬 Feedback submitted!", icon="📝")

        st.subheader("📍 Share Your Location")
        lat, lon = st.session_state.user_location
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=lat, step=0.001, format="%.4f",
                                  help="Adjust your latitude" if st.session_state.show_tooltips else None)
        with col2:
            lon = st.number_input("Longitude", value=lon, step=0.001, format="%.4f",
                                  help="Adjust your longitude" if st.session_state.show_tooltips else None)
        st.session_state.user_location = (lat, lon)
        if st.button("Share Location 🌍", key="share_location",
                     help="Share your custom location" if st.session_state.show_tooltips else None):
            with st.spinner("🌐 Preparing to share..."):
                time.sleep(1)
            whatsapp_url = get_whatsapp_share_url(lat, lon)
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" class="ios-button whatsapp-button fade-in">Share on WhatsApp 📲</a>',
                unsafe_allow_html=True)
            qr_code = generate_qr_code(whatsapp_url)
            st.image(qr_code, caption="Scan to share", width=200)
            st.success("✅ Simulated: Location shared!")
            st.session_state.history_log.append(f"Location shared at {current_time}")
            if st.session_state.notifications:
                time.sleep(st.session_state.notification_delay)
                st.toast("📍 Location shared!", icon="🌐")

        st.subheader("💾 Export Profile")
        profile_data = {"name": st.session_state.user_name, "emergency_contact": st.session_state.emergency_contact,
                        "favorites": list(st.session_state.favorites), "notes": st.session_state.notes,
                        "emergency_contacts_list": st.session_state.emergency_contacts_list}
        st.download_button("Download Profile Data", data=json.dumps(profile_data, indent=2), file_name="profile.json",
                           mime="application/json",
                           help="Export your profile as JSON" if st.session_state.show_tooltips else None)

        st.subheader("📜 Activity Log")
        if st.session_state.history_log:
            for entry in st.session_state.history_log[-5:]:
                st.write(f"- {entry}")
        if st.button("Clear Log", help="Reset activity log" if st.session_state.show_tooltips else None):
            st.session_state.history_log = []
            st.rerun()

        st.subheader("📅 My Appointments")
        if st.session_state.appointment_bookings:
            sorted_bookings = sorted(st.session_state.appointment_bookings, key=lambda x: f"{x['date']} {x['time']}")
            for i, booking in enumerate(sorted_bookings):
                appt_datetime = datetime.datetime.strptime(f"{booking['date']} {booking['time']}",
                                                           "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
                status = booking.get("status", "Pending")
                status_icon = {"Pending": "🟡", "Confirmed": "🟢", "Cancelled": "🔴"}[status]
                payment_status = "Paid" if booking["payment_status"] else "Unpaid (Cash on Arrival)" if booking[
                                                                                                            "payment_method"] == "Cash on Arrival" else "Unpaid"
                with st.expander(
                        f"{status_icon} {status} - {booking['hospital']} with {booking['doctor']} on {booking['date']} at {booking['time']} (Payment: {payment_status})"):
                    st.write(f"**Specialty**: {booking['specialty']}")
                    st.write(f"**Doctor**: {booking['doctor']}")
                    st.write(f"**Notes**: {booking['notes']}")
                    st.write(f"**Confirmed**: {'Yes' if booking['confirmed'] else 'No'}")
                    st.write(f"**Payment Amount**: ₹{booking['payment_amount']}")
                    st.write(f"**Payment Method**: {booking['payment_method']}")
                    st.write(f"**Payment Status**: {payment_status}")
                    st.write(f"**Email**: {booking['email']}")
                    if appt_datetime > current_datetime and status != "Cancelled":
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Cancel", key=f"cancel_{i}"):
                                booking["status"] = "Cancelled"
                                st.session_state.appointment_bookings[i] = booking  # Update status
                                st.success(
                                    f"❌ Appointment at {booking['hospital']} with {booking['doctor']} cancelled!")
                                st.session_state.history_log.append(
                                    f"Cancelled appointment at {booking['hospital']} with {booking['doctor']} on {booking['date']} at {booking['time']}")
                                # Send Cancellation Email
                                cancel_body = (
                                    f"Dear {st.session_state.user_name},\n\n"
                                    f"Your appointment has been cancelled.\n\n"
                                    f"Details:\n"
                                    f"- Hospital: {booking['hospital']}\n"
                                    f"- Date: {booking['date']}\n"
                                    f"- Time: {booking['time']}\n"
                                    f"- Doctor: {booking['doctor']}\n"
                                    f"- Specialty: {booking['specialty']}\n\n"
                                    f"Thank you for using Nellore Hospital Hub!"
                                )
                                with st.spinner("Sending cancellation email..."):
                                    email_success = send_email_alert(booking["email"], "Appointment Cancellation",
                                                                     cancel_body, st.session_state.language)
                                    if email_success:
                                        st.info(f"📧 Cancellation email sent to {booking['email']}!")
                                    else:
                                        st.warning(
                                            f"⚠️ Failed to send cancellation email to {booking['email']}. Queued for retry.")
                                st.rerun()
                        with col2:
                            if st.button("Edit", key=f"edit_{i}"):
                                with st.form(f"edit_form_{i}", clear_on_submit=True):
                                    new_date = st.date_input("New Date",
                                                             value=datetime.datetime.strptime(booking["date"],
                                                                                              "%Y-%m-%d").date())
                                    new_time = st.time_input("New Time",
                                                             value=datetime.datetime.strptime(booking["time"],
                                                                                              "%H:%M:%S").time())
                                    new_specialty = st.selectbox("New Specialty",
                                                                 [h["specialties"] for h in hospitals if
                                                                  h["name"] == booking["hospital"]][0], index=
                                                                 [h["specialties"] for h in hospitals if
                                                                  h["name"] == booking["hospital"]][0].index(
                                                                     booking["specialty"]))
                                    new_doctor = st.selectbox("New Doctor",
                                                              [h["doctors"][new_specialty] for h in hospitals if
                                                               h["name"] == booking["hospital"]][0], index=
                                                              [h["doctors"][new_specialty] for h in hospitals if
                                                               h["name"] == booking["hospital"]][0].index(
                                                                  booking["doctor"]))
                                    new_notes = st.text_area("New Notes", value=booking["notes"])
                                    if st.form_submit_button("Save Changes"):
                                        booking["date"] = str(new_date)
                                        booking["time"] = str(new_time)
                                        booking["specialty"] = new_specialty
                                        booking["doctor"] = new_doctor
                                        booking["notes"] = new_notes
                                        st.success(
                                            f"✅ Appointment at {booking['hospital']} with {booking['doctor']} updated!")
                                        st.session_state.history_log.append(
                                            f"Edited appointment at {booking['hospital']} with {booking['doctor']} to {new_date} at {new_time}")
                                        st.rerun()
                        with col3:
                            if not booking["payment_status"] and booking["payment_method"] != "Cash on Arrival":
                                if st.button("Pay Now", key=f"pay_now_{i}"):
                                    payment_success = simulate_payment(booking["payment_amount"],
                                                                       booking["payment_method"])
                                    if payment_success:
                                        booking["payment_status"] = True
                                        st.success(
                                            f"✅ Payment of ₹{booking['payment_amount']} via {booking['payment_method']} completed!")
                                        st.session_state.history_log.append(
                                            f"Paid ₹{booking['payment_amount']} for appointment at {booking['hospital']} with {booking['doctor']} on {booking['date']} at {booking['time']}")
                                        st.rerun()
                                    else:
                                        st.error("❌ Payment failed. Please try again.")
        else:
            st.write("No appointments scheduled yet.")

    with tabs[3]:  # Chat Tab (unchanged)
        st.subheader("💬 Chatbot Assistant")
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history[-st.session_state.chatbot_memory:]:
                st.markdown(f'<div class="stChat"><b>You:</b> {chat["user"]}<br><b>Bot:</b> {chat["bot"]}</div>',
                            unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            chat_input = st.text_input("Ask me anything!", key="chat_input_new",
                                       help="Chat with the assistant" if st.session_state.show_tooltips else None)
            submit_chat = st.form_submit_button("Send")
            if submit_chat and chat_input:
                response = get_chatbot_response(chat_input, hospitals)
                st.session_state.chat_history.append({"user": chat_input, "bot": response})
                st.session_state.history_log.append(f"Chatted at {current_time}: {chat_input}")
                if st.session_state.voice_mode:
                    html(f'<script>speechSynthesis.speak(new SpeechSynthesisUtterance("{response}"));</script>',
                         height=0)
                st.rerun()

    with tabs[4]:  # Analytics Tab (unchanged)
        st.subheader("📊 Hospital Analytics")
        df = pd.DataFrame(hospitals)
        chart_type = st.selectbox("Chart Type", ["Bar", "Scatter", "Heatmap"], index=0)
        if chart_type == "Bar":
            fig = px.bar(df, x="name", y="beds", color="rating", title="Hospital Beds and Ratings",
                         labels={"name": "Hospital", "beds": "Number of Beds", "rating": "Rating"})
        elif chart_type == "Scatter":
            fig = px.scatter(df, x="wait_time", y="beds", size="rating", color="name", title="Wait Time vs Beds",
                             labels={"wait_time": "Wait Time (min)", "beds": "Number of Beds"})
        else:
            fig, ax = plt.subplots()
            sns.heatmap(df[["beds", "wait_time", "rating", "reviews"]].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
            fig = None
        if chart_type != "Heatmap" and fig is not None:
            st.plotly_chart(fig)
        st.subheader("📈 Rating History")
        hospital_name = st.selectbox("Select Hospital", [h["name"] for h in hospitals])
        if st.session_state.rating_history[hospital_name]:
            fig, ax = plt.subplots()
            ax.plot(st.session_state.rating_history[hospital_name], marker="o")
            ax.set_title(f"Rating History for {hospital_name}")
            ax.set_xlabel("Update Number")
            ax.set_ylabel("Rating")
            st.pyplot(fig)
        st.subheader("📝 Review Analytics")
        if st.session_state.hospital_ratings_comments[hospital_name]:
            st.write(f"Recent Comments for {hospital_name}:")
            for comment in st.session_state.hospital_ratings_comments[hospital_name][-3:]:
                st.write(f"- {comment}")

    with tabs[5]:  # Advanced Tab (unchanged)
        st.subheader("⚙️ Advanced Settings")
        st.session_state.custom_css = st.text_area("Custom CSS", value=st.session_state.custom_css, height=100,
                                                   help="Add custom CSS styles" if st.session_state.show_tooltips else None)
        if st.button("Apply Custom CSS"):
            st.rerun()

        st.subheader("💾 Backup Data")
        state_dict = {k: v for k, v in st.session_state.items() if k != "backup_data"}
        backup_data = json.dumps(state_dict, cls=SetEncoder, indent=2)
        st.download_button("Download Backup", data=backup_data, file_name="backup.json", mime="application/json")
        backup_file = st.file_uploader("Restore Backup", type=["json"])
        if backup_file:
            restored_data = json.load(backup_file)
            if "appointment_bookings" in restored_data:
                for booking in restored_data["appointment_bookings"]:
                    booking["date"] = booking["date"]
                    booking["time"] = booking["time"]
            if "favorites" in restored_data:
                restored_data["favorites"] = set(restored_data["favorites"])
            if "user_roles" in restored_data:
                restored_data["user_roles"]["admin"] = set(restored_data["user_roles"]["admin"])
                restored_data["user_roles"]["user"] = set(restored_data["user_roles"]["user"])
            st.session_state.update(restored_data)
            st.session_state.backup_data = backup_data
            st.success("✅ Backup restored!")
            st.rerun()

        st.subheader("🔑 Logout")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        st.subheader("🔔 Alert History")
        if st.session_state.alert_history:
            for alert in st.session_state.alert_history[-5:]:
                st.write(f"- {alert}")

    with tabs[6]:  # News Tab (unchanged)
        st.subheader("📰 Health News")
        if not st.session_state.news_feed:
            st.session_state.news_feed = ["Simulated News: New hospital wing opened in Nellore!",
                                          "Simulated News: Health camp scheduled next week."]
        for news in st.session_state.news_feed:
            st.write(f"- {news}")
        new_news = st.text_input("Add News (Admin Only)",
                                 disabled=st.session_state.user_preferences.get("role") != "admin")
        if st.button("Submit News") and new_news and st.session_state.user_preferences.get("role") == "admin":
            st.session_state.news_feed.append(f"{current_time}: {new_news}")
            st.success("✅ News added!")

    if st.session_state.auto_refresh and not st.session_state.offline_mode:
        time.sleep(st.session_state.data_refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
