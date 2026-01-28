import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGO_DB_URL"),
            ssl=True,
            ssl_cert_reqs='CERT_NONE',
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
        self.db = self.client["speedolic"]
        self.users_collection = self.db["users"]
        self.vehicles_collection = self.db["vehicles"]
    
    def create_user(self, username: str, password: str, user_type: str) -> bool:
        """Create a new user with specified type (viewer or uploader)"""
        if self.users_collection.find_one({"username": username}):
            return False
        
        user_doc = {
            "username": username,
            "password": password,  # In production, hash this
            "user_type": user_type,  # "viewer" or "uploader"
            "created_at": datetime.now()
        }
        
        self.users_collection.insert_one(user_doc)
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user document"""
        user = self.users_collection.find_one({"username": username, "password": password})
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        user = self.users_collection.find_one({"username": username})
        return user
    
    def add_vehicle_complaint(self, number_plate: str, complaint: str) -> bool:
        """Add a complaint to a vehicle's record"""
        # Remove spaces from number plate
        clean_plate = number_plate.replace(" ", "")
        
        # Update or create vehicle record
        result = self.vehicles_collection.update_one(
            {"number_plate": clean_plate},
            {
                "$push": {
                    "complaints": {
                        "complaint": complaint,
                        "timestamp": datetime.now()
                    }
                },
                "$setOnInsert": {
                    "number_plate": clean_plate,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
        
        return result.acknowledged
    
    def get_vehicle_complaints(self, number_plate: str) -> Optional[Dict]:
        """Get all complaints for a vehicle"""
        clean_plate = number_plate.replace(" ", "")
        vehicle = self.vehicles_collection.find_one({"number_plate": clean_plate})
        return vehicle
    
    def get_all_vehicles(self) -> List[Dict]:
        """Get all vehicles with their complaints"""
        vehicles = list(self.vehicles_collection.find({}))
        return vehicles
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        users = list(self.users_collection.find({}, {"password": 0}))  # Exclude password
        return users

# Initialize database manager
db_manager = DatabaseManager()
