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

# Configure page with modern styling
st.set_page_config(
    page_title="SpeedoLic - Vehicle Complaint System",
    page_icon="",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    .sidebar-info {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
    }
    .dataframe-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

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
    # Modern header
    st.markdown('<div class="main-header">SpeedoLic</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">Vehicle Complaint Management System</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Login</div>', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        with col_login2:
            if st.button("Login", use_container_width=True):
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Registration Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Register New User</div>', unsafe_allow_html=True)
        
        new_username = st.text_input("New Username", placeholder="Choose a username")
        new_password = st.text_input("New Password", type="password", placeholder="Choose a password")
        user_type = st.selectbox("User Type", ["viewer", "uploader"], 
                                help="Viewer: Can search complaints by number plate\nUploader: Can upload images and register complaints")
        
        col_reg1, col_reg2, col_reg3 = st.columns([1, 2, 1])
        with col_reg2:
            if st.button("Register", use_container_width=True):
                if new_username and new_password:
                    if db_manager.create_user(new_username, new_password, user_type):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please enter both username and password")
        
        st.markdown('</div>', unsafe_allow_html=True)

def viewer_dashboard():
    # Modern header with user info
    st.markdown(f'<div class="main-header">Welcome, {st.session_state.username}</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">Viewer Dashboard - Search Vehicle Complaints</p>', unsafe_allow_html=True)
    
    # Search section in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Search Vehicle Complaints</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        number_plate = st.text_input("Vehicle Number Plate", 
                                    placeholder="Enter vehicle number plate (e.g., ABC123)",
                                    help="Enter the vehicle number plate to view all associated complaints")
        
        if st.button("Search Complaints", use_container_width=True):
            if number_plate:
                with st.spinner("Searching for vehicle complaints..."):
                    vehicle_data = db_manager.get_vehicle_complaints(number_plate)
                
                if vehicle_data:
                    st.markdown(f'<div class="success-message">Found vehicle: {vehicle_data["number_plate"]}</div>', unsafe_allow_html=True)
                    
                    # Display complaints in a styled container
                    if vehicle_data.get('complaints'):
                        complaints_df = pd.DataFrame(vehicle_data['complaints'])
                        complaints_df['timestamp'] = pd.to_datetime(complaints_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        complaints_df = complaints_df.rename(columns={
                            'complaint': 'Complaint',
                            'timestamp': 'Date & Time'
                        })
                        
                        st.markdown('<div class="section-header">Complaint History</div>', unsafe_allow_html=True)
                        st.markdown(f'<p style="color: #6b7280; margin-bottom: 1rem;">Total complaints: {len(complaints_df)}</p>', unsafe_allow_html=True)
                        
                        # Style the dataframe
                        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                        st.dataframe(complaints_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No complaints found for this vehicle")
                else:
                    st.info("No vehicle found with this number plate")
            else:
                st.warning("Please enter a number plate")
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    # Modern header with user info
    st.markdown(f'<div class="main-header">Welcome, {st.session_state.username}</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">Uploader Dashboard - Register Vehicle Complaints</p>', unsafe_allow_html=True)
    
    logger.debug("Uploader dashboard: Creating tabs")
    
    # Modern tabs
    tab1, tab2 = st.tabs(["Upload & Process", "Direct Entry"])
    
    with tab1:
        logger.debug("Uploader dashboard: Entering tab1 (Upload Vehicle Image)")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Upload Vehicle Image for ANPR</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a vehicle image", 
                                       type=['jpg', 'jpeg', 'png', 'bmp'],
                                       help="Upload an image containing a vehicle number plate")
        
        if uploaded_file is not None:
            # Display uploaded image in a styled container
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Process Image & Extract Number Plate", use_container_width=True):
                    with st.spinner("Processing image with AI..."):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            # Process with ANPR
                            result = anpr_processor.process_image(tmp_file_path)
                            
                            if result['success']:
                                st.markdown('<div class="success-message">Image processed successfully!</div>', unsafe_allow_html=True)
                                
                                # Display results in columns
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                                    st.image(anpr_processor.convert_cv2_to_pil(result['bbox_image']), 
                                            caption="Image with Detection", use_column_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                                    st.image(anpr_processor.convert_cv2_to_pil(result['cropped_plate']), 
                                            caption="Cropped Number Plate", use_column_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Check if OCR is available
                                if result['number_plate'] == "OCR_UNAVAILABLE":
                                    st.warning("OCR is currently unavailable due to network issues. Please manually enter the number plate below.")
                                    st.session_state.has_cropped_plate = True
                                    st.session_state.cropped_plate_image = result['cropped_plate']
                                    st.session_state.extracted_plate = None
                                else:
                                    st.success(f"Extracted Number Plate: {result['number_plate']}")
                                    st.session_state.extracted_plate = result['number_plate']
                                    st.session_state.has_cropped_plate = True
                                
                                # Show next step message
                                if st.session_state.extracted_plate and st.session_state.extracted_plate != "OCR_UNAVAILABLE":
                                    st.info("Please use the form below to register your complaint")
                                elif st.session_state.get('has_cropped_plate', False):
                                    st.info("Image processed successfully. Please enter the number plate and register your complaint below")
                            else:
                                st.error(f"Failed to process image: {result['error']}")
                        
                        finally:
                            # Clean up temporary file
                            if os.path.exists(tmp_file_path):
                                os.unlink(tmp_file_path)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Manual entry section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Register Complaint</div>', unsafe_allow_html=True)
        
        # Auto-fill number plate from OCR if available
        if st.session_state.get('extracted_plate') and st.session_state.extracted_plate != "OCR_UNAVAILABLE":
            default_plate = st.session_state.extracted_plate
            st.markdown(f'<div class="success-message">Detected Number Plate: {default_plate}</div>', unsafe_allow_html=True)
            manual_plate = st.text_input("Edit number plate if needed", value=default_plate)
        else:
            manual_plate = st.text_input("Enter number plate manually", placeholder="e.g., ABC123")
        
        manual_complaint = st.text_area("Complaint Details", key="manual_complaint", 
                                       placeholder="Describe the complaint details...",
                                       help="Enter detailed information about the vehicle complaint")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Register Complaint", key="register_manual", use_container_width=True):
                if manual_plate and manual_complaint:
                    if register_complaint_with_feedback(manual_plate, manual_complaint):
                        if st.button("Start New Upload", key="start_over_manual", use_container_width=True):
                            st.session_state.extracted_plate = None
                            st.session_state.has_cropped_plate = False
                            st.rerun()
                else:
                    st.error("Please enter both number plate and complaint")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        logger.debug("Uploader dashboard: Entering tab2 (Manual Complaint Entry)")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Direct Complaint Registration</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            direct_plate = st.text_input("Vehicle Number Plate", placeholder="e.g., ABC123")
            direct_complaint = st.text_area("Complaint Details", key="direct_complaint", 
                                           placeholder="Describe the complaint details...",
                                           help="Enter detailed information about the vehicle complaint")
            
            if st.button("Register Complaint", key="register_direct", use_container_width=True):
                if direct_plate and direct_complaint:
                    register_complaint_with_feedback(direct_plate, direct_complaint)
                else:
                    st.error("Please enter both number plate and complaint")
        
        st.markdown('</div>', unsafe_allow_html=True)

def admin_dashboard():
    # Modern header with user info
    st.markdown(f'<div class="main-header">Welcome, {st.session_state.username}</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">Admin Dashboard - System Management</p>', unsafe_allow_html=True)
    
    # Modern tabs
    tab1, tab2 = st.tabs(["Users Management", "Vehicles & Complaints"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">All Registered Users</div>', unsafe_allow_html=True)
        
        users = db_manager.get_all_users()
        
        if users:
            users_df = pd.DataFrame(users)
            users_df = users_df.rename(columns={
                'username': 'Username',
                'user_type': 'User Type',
                'created_at': 'Registration Date'
            })
            users_df['Registration Date'] = pd.to_datetime(users_df['Registration Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.markdown(f'<p style="color: #6b7280; margin-bottom: 1rem;">Total registered users: {len(users_df)}</p>', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(users_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No users registered yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">All Vehicles with Complaints</div>', unsafe_allow_html=True)
        
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
            
            st.markdown(f'<p style="color: #6b7280; margin-bottom: 1rem;">Total vehicles with complaints: {len(summary_df)}</p>', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(summary_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed view for selected vehicle
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('<div class="section-header">Detailed Complaint View</div>', unsafe_allow_html=True)
            
            if vehicles:
                selected_plate = st.selectbox("Select Vehicle for Details", 
                                            [v['number_plate'] for v in vehicles],
                                            help="Choose a vehicle to view all complaint details")
                
                if selected_plate:
                    selected_vehicle = next(v for v in vehicles if v['number_plate'] == selected_plate)
                    
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="section-header">{selected_plate} - Complaint Details</div>', unsafe_allow_html=True)
                    
                    if selected_vehicle.get('complaints'):
                        complaints_df = pd.DataFrame(selected_vehicle['complaints'])
                        complaints_df['timestamp'] = pd.to_datetime(complaints_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        complaints_df = complaints_df.rename(columns={
                            'complaint': 'Complaint',
                            'timestamp': 'Date & Time'
                        })
                        
                        st.markdown(f'<p style="color: #6b7280; margin-bottom: 1rem;">Total complaints: {len(complaints_df)}</p>', unsafe_allow_html=True)
                        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                        st.dataframe(complaints_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No complaints for this vehicle")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No vehicles registered yet")
        
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_type = None
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # Modern sidebar with user info and logout
        with st.sidebar:
            st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
            st.markdown(f"### SpeedoLic")
            st.markdown(f"**{st.session_state.username}**")
            st.markdown(f"**{st.session_state.user_type.title()}**")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
            
            # Navigation menu
            st.markdown("### Navigation")
            
            # Quick stats
            if st.session_state.user_type in ['admin', 'viewer']:
                vehicles = db_manager.get_all_vehicles()
                total_complaints = sum(len(v.get('complaints', [])) for v in vehicles)
                st.metric("Vehicles", len(vehicles))
                st.metric("Complaints", total_complaints)
                st.markdown("---")
            
            if st.button("Logout", use_container_width=True):
                logout()
            
            # Footer
            st.markdown("---")
            st.markdown('<p style="text-align: center; color: #6b7280; font-size: 0.8rem;">SpeedoLic v1.0</p>', unsafe_allow_html=True)
        
        # Main content based on user type
        if st.session_state.user_type == 'viewer':
            viewer_dashboard()
        elif st.session_state.user_type == 'uploader':
            uploader_dashboard()
        elif st.session_state.user_type == 'admin':
            admin_dashboard()

if __name__ == "__main__":
    main()
