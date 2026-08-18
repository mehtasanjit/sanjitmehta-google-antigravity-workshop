from app.database import init_db

if __name__ == "__main__":
    print("Initializing SQLite complaints.db and seeding robust mock data...")
    init_db("sqlite:///complaints.db")
    print("Initialization complete! Created complaints.db on disk successfully.")
