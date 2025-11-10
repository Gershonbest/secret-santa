from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from database import init_db, SessionLocal
from models import Settings
from routers import users, admin

# Initialize FastAPI app
app = FastAPI(title="Secret Santa App")

# Initialize database
init_db()

# Initialize default settings
def init_settings():
    """Initialize default settings if they don't exist."""
    db = SessionLocal()
    try:
        registration_setting = db.query(Settings).filter(Settings.key == "registration_open").first()
        if not registration_setting:
            registration_setting = Settings(key="registration_open", value="true")
            db.add(registration_setting)
            db.commit()
    finally:
        db.close()

# Initialize settings on startup
init_settings()

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(users.router)
app.include_router(admin.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
