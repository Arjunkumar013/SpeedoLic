# SpeedoLic - Vehicle Complaint Management System

A comprehensive Streamlit application for managing vehicle complaints using ANPR (Automatic Number Plate Recognition) technology.

## 🚀 Current Progress

### ✅ Completed Features
- **User Authentication System**: Secure login with role-based access control
- **ANPR Integration**: 
  - YOLOv8 model for number plate detection
  - EasyOCR for text extraction from number plates
  - Real-time image processing with bounding box visualization
- **Multi-User System**:
  - **Viewer**: Search and view vehicle complaints by number plate
  - **Uploader**: Upload images, extract number plates, register complaints
  - **Admin**: Complete system management and oversight
- **Database Management**: JSON-based storage (fallback from MongoDB)
- **Modern UI**: Responsive Streamlit interface with custom CSS styling
- **Error Handling**: Graceful OCR fallback when network issues occur

### 🛠️ Technical Implementation
- **Frontend**: Streamlit with custom CSS for modern styling
- **Backend**: Python with modular architecture
- **Computer Vision**: YOLOv8 (Ultralytics) for object detection
- **OCR**: EasyOCR for text extraction with network resilience
- **Image Processing**: OpenCV for image manipulation
- **Database**: Simple JSON-based storage system
- **Authentication**: Session-based user management

## 📋 Dataset

Indian Vehicle Dataset (Number Plate Detection)

🔗 Dataset Link:  
https://www.kaggle.com/datasets/saisirishan/indian-vehicle-dataset

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit
- Required ML libraries (see requirements.txt)

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd SpeedoLic
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the setup script** (creates initial users)
```bash
python setup_admin.py
```

4. **Start the application**
```bash
streamlit run app.py
```

The application will automatically open in your web browser at `http://localhost:8501`

### Default User Credentials
After running setup_admin.py:

- **Admin**: Username: `admin`, Password: `admin123`
- **Viewer**: Username: `viewer1`, Password: `viewer123`
- **Uploader**: Username: `uploader1`, Password: `uploader123`

## 👥 User Roles & Features

### 🔍 Viewer
- **Search Functionality**: Look up vehicle complaints by number plate
- **Complaint History**: View all complaints associated with a vehicle
- **Data Visualization**: Clean, tabular display of complaint records

### 📤 Uploader
- **Image Upload**: Upload vehicle images for automatic number plate detection
- **ANPR Processing**: Real-time number plate extraction with visual feedback
- **Manual Entry**: Direct complaint registration without image upload
- **Detection Preview**: View bounding boxes and cropped number plates

### 👨‍💼 Admin
- **User Management**: View all registered users and their roles
- **Vehicle Oversight**: Complete view of all vehicles and complaint history
- **System Analytics**: Quick stats on total vehicles and complaints
- **Detailed Reports**: In-depth complaint analysis per vehicle

## 🏗️ Project Structure

```
SpeedoLic/
├── app.py                 # Main Streamlit application
├── simple_database.py     # JSON-based database management
├── database.py            # MongoDB connection (backup)
├── anpr_processor.py      # ANPR processing logic
├── setup_admin.py         # Initial user setup script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── speedolic_data.json    # Local database file
├── ANPR_Model_Full/      # Trained YOLO model
│   └── weights/
│       └── best.pt       # Best model weights
└── README.md             # This file
```

## 🔧 How It Works

1. **Image Processing**: User uploads vehicle image
2. **Plate Detection**: YOLOv8 model identifies number plate location
3. **Text Extraction**: EasyOCR reads text from the detected plate
4. **Data Storage**: Complaints stored with vehicle information
5. **User Interface**: Role-based dashboards for different user types

---

## 🚀 Future Scope & Enhancements

### 🎯 Advanced OCR Fine-Tuning
- **Custom Model Training**: Fine-tune EasyOCR specifically for Indian number plates
- **Regional Adaptation**: Training on diverse number plate formats across states
- **Accuracy Improvement**: Target 95%+ accuracy through specialized training
- **Edge Case Handling**: Better recognition of damaged or obscured plates

### 👮 Traffic Police Authorization System
- **Official Verification**: Integration with traffic police department databases
- **Role-Based Access**: Special permissions for law enforcement personnel
- **Badge System**: Digital verification for authorized officers
- **Audit Trail**: Complete logging of all official activities

### 🚗 Complete Vehicle Information System
- **RTO Database Integration**: Real-time access to Regional Transport Office data
- **Vehicle Details**: Complete information including:
  - Owner name and address
  - Vehicle registration details
  - Insurance status and validity
  - Pollution certificate status
  - Vehicle type and specifications
- **Historical Data**: Past violations and ownership history

### 📝 Complaint Management Enhancement
- **Structured Complaint Forms**: Categorized violation types
- **Evidence Management**: Upload multiple images/videos
- **Location Tagging**: GPS-based incident location
- **Severity Classification**: Automatic violation categorization
- **Status Tracking**: Real-time complaint status updates

### 💳 Integrated Fine Payment System
- **Online Payment Gateway**: Integration with payment processors
- **Fine Calculation**: Automatic penalty amount based on violation type
- **Receipt Generation**: Digital receipts for all transactions
- **Payment History**: Complete payment records for vehicles
- **Discount System**: Early payment discounts

### 🎥 CCTV Automation Integration
- **Real-time Monitoring**: Live CCTV feed analysis
- **Automatic Violation Detection**: AI-powered traffic violation identification
- **Alert System**: Instant notifications for detected violations
- **24/7 Operation**: Continuous monitoring without human intervention
- **Multi-Camera Support**: Simultaneous analysis of multiple feeds

### 🤖 Intelligent Automation Pipeline
```
CCTV Feed → AI Analysis → Violation Detection → 
Number Plate Extraction → Vehicle Lookup → 
Auto-Complaint Generation → Fine Calculation → 
Notification → Payment Processing
```

### 📊 Analytics & Reporting
- **Violation Patterns**: Geographic and temporal analysis
- **Hotspot Identification**: Areas with high violation rates
- **Trend Analysis**: Monthly/ yearly violation trends
- **Performance Metrics**: System efficiency and accuracy reports
- **Export Functionality**: Generate PDF/Excel reports

### 🔒 Security & Compliance
- **Data Encryption**: End-to-end encryption for sensitive data
- **GDPR Compliance**: Privacy protection for vehicle owner data
- **Access Controls**: Multi-level authentication and authorization
- **Audit Logs**: Complete activity tracking for compliance

### 🌐 Mobile Application
- **Native Apps**: iOS and Android applications
- **Push Notifications**: Real-time alerts for violations
- **Offline Mode**: Functionality without internet connection
- **QR Code Scanning**: Quick number plate input

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

For queries and support, please reach out through the project issues section.

---

**SpeedoLic** - Making traffic management smarter with AI-powered vehicle recognition 🚗💨
