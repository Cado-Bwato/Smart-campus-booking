from database.db_manager import create_tables, seed_campuses
from services.auth_service import seed_default_users
from services.resource_service import seed_resources
from gui.app import App

if __name__ == "__main__":
    create_tables()
    seed_campuses()
    seed_default_users()
    seed_resources()

    app = App()
    app.run()