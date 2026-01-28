import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class SimpleDatabaseManager:
    def __init__(self):
        self.data_file = "speedolic_data.json"
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"users": [], "vehicles": []}
    
    def _save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def create_user(self, username: str, password: str, user_type: str) -> bool:
        """Create a new user with specified type (viewer or uploader)"""
        # Check if user already exists
        for user in self.data["users"]:
            if user["username"] == username:
                return False
        
        user_doc = {
            "username": username,
            "password": password,  # In production, hash this
            "user_type": user_type,  # "viewer" or "uploader"
            "created_at": datetime.now()
        }
        
        self.data["users"].append(user_doc)
        self._save_data()
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user document"""
        for user in self.data["users"]:
            if user["username"] == username and user["password"] == password:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        for user in self.data["users"]:
            if user["username"] == username:
                return user
        return None
    
    def add_vehicle_complaint(self, number_plate: str, complaint: str) -> bool:
        """Add a complaint to a vehicle's record"""
        # Remove spaces from number plate
        clean_plate = number_plate.replace(" ", "")
        
        # Find existing vehicle or create new one
        vehicle = None
        for v in self.data["vehicles"]:
            if v["number_plate"] == clean_plate:
                vehicle = v
                break
        
        if vehicle is None:
            # Create new vehicle record
            vehicle = {
                "number_plate": clean_plate,
                "created_at": datetime.now(),
                "complaints": []
            }
            self.data["vehicles"].append(vehicle)
        
        # Add complaint
        complaint_doc = {
            "complaint": complaint,
            "timestamp": datetime.now()
        }
        vehicle["complaints"].append(complaint_doc)
        
        self._save_data()
        return True
    
    def get_vehicle_complaints(self, number_plate: str) -> Optional[Dict]:
        """Get all complaints for a vehicle"""
        clean_plate = number_plate.replace(" ", "")
        for vehicle in self.data["vehicles"]:
            if vehicle["number_plate"] == clean_plate:
                return vehicle
        return None
    
    def get_all_vehicles(self) -> List[Dict]:
        """Get all vehicles with their complaints"""
        return self.data["vehicles"]
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.data["users"]

# Initialize database manager
db_manager = SimpleDatabaseManager()
