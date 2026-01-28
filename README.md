# SpeedoLic - Vehicle Complaint Management System

A comprehensive Streamlit application for managing vehicle complaints using ANPR (Automatic Number Plate Recognition) technology.

## Features

- **User Authentication**: Secure login system with different user types
- **ANPR Integration**: Automatic number plate detection using YOLO and OCR with EasyOCR
- **Dual User Types**:
  - **Viewer**: Can search complaints by number plate
  - **Uploader**: Can upload vehicle images, extract number plates, and register complaints
  - **Admin**: Can view all users and vehicles
- **MongoDB Integration**: Persistent storage for users and vehicle data
- **Real-time Processing**: Instant number plate detection and complaint registration

## Dataset

Indian Vehicle Dataset (Number Plate Detection)

🔗 Dataset Link:  
https://www.kaggle.com/datasets/saisirishan/indian-vehicle-dataset

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your MongoDB connection string:
   ```
   MONGO_DB_URL=mongodb://localhost:27017/speedolic
   ```

4. Run the setup script to create initial users:
```bash
python setup_admin.py
```

5. Run the Streamlit application:
```bash
streamlit run app.py
```

## Usage

### Default Users

After running the setup script, you can use these credentials:

- **Admin**: Username: `admin`, Password: `admin123`
- **Viewer**: Username: `viewer1`, Password: `viewer123`
- **Uploader**: Username: `uploader1`, Password: `uploader123`

### User Roles

1. **Viewer**:
   - Search vehicle complaints by entering number plate
   - View all complaints associated with a vehicle

2. **Uploader**:
   - Upload vehicle images for automatic number plate detection
   - Manually enter number plates and register complaints
   - View detection results with bounding boxes

3. **Admin**:
   - View all registered users
   - View all vehicles and their complaint history
   - Access detailed complaint information

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MongoDB
- **Computer Vision**: YOLOv8 (Ultralytics)
- **OCR**: EasyOCR
- **Image Processing**: OpenCV
- **Authentication**: Custom session management

## Project Structure

```
SpeedoLic/
├── app.py                 # Main Streamlit application
├── database.py            # MongoDB connection and operations
├── anpr_processor.py      # ANPR processing logic
├── setup_admin.py         # Initial user setup script
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── ANPR_Model_Full/      # Trained YOLO model
│   └── weights/
│       ├── best.pt       # Best model weights
│       └── last.pt       # Last epoch weights
└── README.md             # This file
```

## How It Works

1. **Number Plate Detection**: Uses trained YOLO model to detect number plates in uploaded images
2. **Text Extraction**: Applies EasyOCR to extract text from detected number plates
3. **Data Storage**: Stores user information and vehicle complaints in MongoDB
4. **User Interface**: Provides role-based interfaces for different user types

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
