import os
from dotenv import load_dotenv
from mongoengine import connect

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # MongoDB settings
    MONGODB_NAME = os.getenv("MONGODB_NAME", "ulocationbot")
    MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    
    # Admin settings
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Base path for admin routes
    BASE_PATH = "/ulocation"

def initialize_db():
    """Initialize MongoDB connection"""
    connection_kwargs = {
        "db": Config.MONGODB_NAME,
        "host": Config.MONGODB_HOST,
        "port": Config.MONGODB_PORT,
    }
    MONGO_URI = f"mongodb://{Config.MONGODB_HOST}:{Config.MONGODB_PORT}/{Config.MONGODB_NAME}"
    
    # Add authentication if provided
    if Config.MONGODB_USERNAME and Config.MONGODB_PASSWORD:
        connection_kwargs["username"] = Config.MONGODB_USERNAME
        connection_kwargs["password"] = Config.MONGODB_PASSWORD
        MONGO_URI = f"mongodb://{Config.MONGODB_USERNAME}:{Config.MONGODB_PASSWORD}@{Config.MONGODB_HOST}:{Config.MONGODB_PORT}/{Config.MONGODB_NAME}"
    
    
    try:
        connect(MONGO_URI)
        print(f"Connected to MongoDB: {MONGO_URI}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")