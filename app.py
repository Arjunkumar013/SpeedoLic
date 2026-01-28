import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile
import os
import torch
import logging
# try:
#     from database import db_manager
#     print("✅ Using MongoDB database")
# except Exception as e:
#     print(f"❌ MongoDB failed, using simple database: {e}")
from simple_database import db_manager
print("✅ Using simple JSON database")
from anpr_processor import ANPRProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Apply PyTorch patch before any model loading
original_torch_load = torch.load

def patched_torch_load(f, *args, **kwargs):
    # If weights_only is not specified and this looks like a YOLO model, set weights_only=False
    if 'weights_only' not in kwargs and isinstance(f, str) and f.endswith('.pt'):
        kwargs['weights_only'] = False
    return original_torch_load(f, *args, **kwargs)

# Apply the patch
torch.load = patched_torch_load

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Initialize ANPR processor
@st.cache_resource
def load_anpr_processor():
    return ANPRProcessor()

anpr_processor = load_anpr_processor()

def login_page():
    st.title("🚗 SpeedoLic - Vehicle Complaint System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username and password:
                user = db_manager.authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user['username']
                    st.session_state.user_type = user['user_type']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
        
        st.markdown("---")
        st.subheader("Register New User")
        
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        user_type = st.selectbox("User Type", ["viewer", "uploader"], 
                                help="Viewer: Can search complaints by number plate\nUploader: Can upload images and register complaints")
        
        if st.button("Register"):
            if new_username and new_password:
                if db_manager.create_user(new_username, new_password, user_type):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
            else:
                st.error("Please enter both username and password")

def viewer_dashboard():
    st.title(f"👋 Welcome, {st.session_state.username} (Viewer)")
    st.markdown("---")
    
    st.subheader("🔍 Search Vehicle Complaints")
    
    number_plate = st.text_input("Enter Vehicle Number Plate", 
                                help="Enter the vehicle number plate to view complaints")
    
    if st.button("Search Complaints"):
        if number_plate:
            vehicle_data = db_manager.get_vehicle_complaints(number_plate)
            
            if vehicle_data:
                st.success(f"Found vehicle: {vehicle_data['number_plate']}")
                
                # Display complaints
                if vehicle_data.get('complaints'):
                    complaints_df = pd.DataFrame(vehicle_data['complaints'])
                    complaints_df['timestamp'] = pd.to_datetime(complaints_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    complaints_df = complaints_df.rename(columns={
                        'complaint': 'Complaint',
                        'timestamp': 'Date & Time'
                    })
                    
                    st.subheader(f"Complaints ({len(complaints_df)})")
                    st.dataframe(complaints_df, use_container_width=True)
                else:
                    st.info("No complaints found for this vehicle")
            else:
                st.info("No vehicle found with this number plate")
        else:
            st.warning("Please enter a number plate")

def register_complaint_with_feedback(number_plate, complaint_text):
    """Helper function to register complaint and show feedback"""
    if db_manager.add_vehicle_complaint(number_plate, complaint_text):
        st.success("Complaint registered successfully!")
        logger.debug("Complaint registered successfully!")
        
        # Show all complaints for this number plate
        st.markdown("---")
        st.subheader(f"All Complaints for {number_plate}")
        
        vehicle_data = db_manager.get_vehicle_complaints(number_plate)
        if vehicle_data and vehicle_data.get('complaints'):
            complaints_df = pd.DataFrame(vehicle_data['complaints'])
            complaints_df['timestamp'] = pd.to_datetime(complaints_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            complaints_df = complaints_df.rename(columns={
                'complaint': 'Complaint',
                'timestamp': 'Date & Time'
            })
            st.dataframe(complaints_df, use_container_width=True)
        else:
            st.info("No other complaints found for this vehicle")
        
        return True
    else:
        st.error("Failed to register complaint")
        logger.error("Failed to register complaint in database")
        return False

def uploader_dashboard():
    st.title(f"👋 Welcome, {st.session_state.username} (Uploader)")
    st.markdown("---")
    
    # Two tabs: Upload Image and Manual Entry
    tab1, tab2 = st.tabs(["📷 Upload Vehicle Image", "✏️ Manual Complaint Entry"])
    
    logger.debug("Uploader dashboard: Creating tabs")
    
    with tab1:
        logger.debug("Uploader dashboard: Entering tab1 (Upload Vehicle Image)")
        st.subheader("Upload Vehicle Image for ANPR")
        
        uploaded_file = st.file_uploader("Choose a vehicle image", 
                                       type=['jpg', 'jpeg', 'png', 'bmp'])
        
        if uploaded_file is not None:
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Process Image & Extract Number Plate"):
                with st.spinner("Processing image..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        # Process with ANPR
                        result = anpr_processor.process_image(tmp_file_path)
                        
                        if result['success']:
                            # Display results
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.image(anpr_processor.convert_cv2_to_pil(result['bbox_image']), 
                                        caption="Image with Bounding Box", use_column_width=True)
                            
                            with col2:
                                st.image(anpr_processor.convert_cv2_to_pil(result['cropped_plate']), 
                                        caption="Cropped Number Plate", use_column_width=True)
                            
                            st.success(f"Extracted Number Plate: **{result['number_plate']}**")
                            
                            # Check if OCR is available
                            if result['number_plate'] == "OCR_UNAVAILABLE":
                                st.warning("⚠️ OCR is currently unavailable due to network issues. You can manually enter the number plate below.")
                                # Store that we have a cropped plate but no OCR
                                st.session_state.has_cropped_plate = True
                                st.session_state.cropped_plate_image = result['cropped_plate']
                                st.session_state.extracted_plate = None
                            else:
                                # Store extracted number plate in session state
                                st.session_state.extracted_plate = result['number_plate']
                                st.session_state.has_cropped_plate = True
                            
                            # Show success message for OCR processing
                            if st.session_state.extracted_plate and st.session_state.extracted_plate != "OCR_UNAVAILABLE":
                                st.success(f"✅ **Number Plate Detected:** {st.session_state.extracted_plate}")
                                st.info("👇 Please use the manual entry section below to register your complaint")
                            elif st.session_state.get('has_cropped_plate', False):
                                st.info("📷 Image processed successfully. Please use the manual entry section below to enter the number plate and register your complaint")
                        else:
                            st.error(f"Failed to process image: {result['error']}")
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)
        
        # Manual entry section
        st.markdown("---")
        st.subheader("Manual Number Plate Entry")
        
        # Auto-fill number plate from OCR if available
        if st.session_state.get('extracted_plate') and st.session_state.extracted_plate != "OCR_UNAVAILABLE":
            default_plate = st.session_state.extracted_plate
            st.info(f"📍 **Number Plate (from OCR):** {default_plate}")
            manual_plate = st.text_input("Or edit number plate manually", value=default_plate)
        else:
            manual_plate = st.text_input("Enter number plate manually")
        
        manual_complaint = st.text_area("Manual Complaint Details", key="manual_complaint", 
                                       help="Enter complaint details for manual number plate entry")
        
        if st.button("Register Manual Complaint", key="register_manual"):
            if manual_plate and manual_complaint:
                if register_complaint_with_feedback(manual_plate, manual_complaint):
                    # Add a button to start over
                    if st.button("Start New Upload", key="start_over_manual"):
                        st.session_state.extracted_plate = None
                        st.session_state.has_cropped_plate = False
                        st.rerun()
            else:
                st.error("Please enter both number plate and complaint")
    
    with tab2:
        logger.debug("Uploader dashboard: Entering tab2 (Manual Complaint Entry)")
        st.subheader("Direct Complaint Registration")
        
        direct_plate = st.text_input("Vehicle Number Plate")
        direct_complaint = st.text_area("Direct Complaint Details", key="direct_complaint", 
                                       help="Enter complaint details for direct registration")
        
        if st.button("Register Complaint", key="register_direct"):
            if direct_plate and direct_complaint:
                register_complaint_with_feedback(direct_plate, direct_complaint)
            else:
                st.error("Please enter both number plate and complaint")

def admin_dashboard():
    st.title(f"👋 Welcome, {st.session_state.username} (Admin)")
    st.markdown("---")
    
    # Two tabs: Users and Vehicles
    tab1, tab2 = st.tabs(["👥 Users", "🚗 Vehicles"])
    
    with tab1:
        st.subheader("All Registered Users")
        
        users = db_manager.get_all_users()
        
        if users:
            users_df = pd.DataFrame(users)
            users_df = users_df.rename(columns={
                'username': 'Username',
                'user_type': 'User Type',
                'created_at': 'Registration Date'
            })
            users_df['Registration Date'] = pd.to_datetime(users_df['Registration Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(users_df, use_container_width=True)
        else:
            st.info("No users registered yet")
    
    with tab2:
        st.subheader("All Vehicles with Complaints")
        
        vehicles = db_manager.get_all_vehicles()
        
        if vehicles:
            # Create a summary table
            vehicle_summary = []
            for vehicle in vehicles:
                complaint_count = len(vehicle.get('complaints', []))
                vehicle_summary.append({
                    'Number Plate': vehicle['number_plate'],
                    'Total Complaints': complaint_count,
                    'First Complaint': vehicle.get('created_at', 'N/A')
                })
            
            summary_df = pd.DataFrame(vehicle_summary)
            if 'First Complaint' in summary_df.columns:
                summary_df['First Complaint'] = pd.to_datetime(summary_df['First Complaint']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(summary_df, use_container_width=True)
            
            # Detailed view for selected vehicle
            st.markdown("---")
            st.subheader("Detailed Complaint View")
            
            if vehicles:
                selected_plate = st.selectbox("Select Vehicle for Details", 
                                            [v['number_plate'] for v in vehicles])
                
                if selected_plate:
                    selected_vehicle = next(v for v in vehicles if v['number_plate'] == selected_plate)
                    
                    if selected_vehicle.get('complaints'):
                        complaints_df = pd.DataFrame(selected_vehicle['complaints'])
                        complaints_df['timestamp'] = pd.to_datetime(complaints_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        complaints_df = complaints_df.rename(columns={
                            'complaint': 'Complaint',
                            'timestamp': 'Date & Time'
                        })
                        
                        st.dataframe(complaints_df, use_container_width=True)
                    else:
                        st.info("No complaints for this vehicle")
        else:
            st.info("No vehicles registered yet")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_type = None
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar with user info and logout
        with st.sidebar:
            st.title("🚗 SpeedoLic")
            st.markdown(f"**Logged in as:** {st.session_state.username}")
            st.markdown(f"**User Type:** {st.session_state.user_type.capitalize()}")
            st.markdown("---")
            
            if st.button("🚪 Logout"):
                logout()
        
        # Main content based on user type
        if st.session_state.user_type == 'viewer':
            viewer_dashboard()
        elif st.session_state.user_type == 'uploader':
            uploader_dashboard()
        elif st.session_state.user_type == 'admin':
            admin_dashboard()

if __name__ == "__main__":
    main()
