from app import app, db

def reset_database():
    with app.app_context():
        try:
            # Drop all tables in the correct order
            db.reflect()
            db.drop_all()
            print("All tables dropped successfully.")
        except Exception as e:
            print(f"Error dropping tables: {e}")
        finally:
            # Recreate all tables
            db.create_all()
            print("All tables recreated successfully.")

if __name__ == "__main__":
    reset_database()