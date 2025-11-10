from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Settings, Pairing
from auth import (
    authenticate_user,
    get_password_hash,
    create_access_token,
    get_current_user_from_token,
)
from pairing import get_user_pairing, pairing_exists

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session token cookie."""
    token = request.cookies.get("access_token")
    if not token:
        print("DEBUG: No access_token cookie found")
        return None
    print(f"DEBUG: Found token: {token[:50]}...")
    try:
        user = get_current_user_from_token(token, db)
        print(f"DEBUG: Successfully authenticated user: {user.email}")
        return user
    except HTTPException as e:
        # Log the error for debugging
        print(f"HTTPException getting current user: {e.detail}")
        return None
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error getting current user: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Login/Registration page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Register a new user."""
    # Check if registration is open
    registration_setting = db.query(Settings).filter(Settings.key == "registration_open").first()
    if registration_setting and registration_setting.value.lower() != "true":
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Registration is currently closed.",
            },
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Email already registered. Please log in instead.",
            },
        )

    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        hashed_password=hashed_password,
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Note: New users are NOT automatically assigned if pairings exist
    # Admin must use "Assign Users Without Pairs" to assign them

    # Create access token and set cookie
    # JWT 'sub' claim must be a string, so convert user.id to string
    access_token = create_access_token(data={"sub": str(new_user.id)})
    print(f"DEBUG: Created token for user {new_user.id}: {access_token[:50]}...")
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/"
    )
    print(f"DEBUG: Cookie set, redirecting to dashboard")
    return response


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Login user."""
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Invalid email or password.",
            },
        )

    # Create access token and set cookie
    # JWT 'sub' claim must be a string, so convert user.id to string
    access_token = create_access_token(data={"sub": str(user.id)})
    print(f"DEBUG: Created token for user {user.id}: {access_token[:50]}...")
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/"
    )
    print(f"DEBUG: Cookie set, redirecting to dashboard")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """User dashboard."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    # Get all users
    all_users = db.query(User).all()

    # Get user's pairing
    pairing = get_user_pairing(db, user.id)
    assigned_person = None
    if pairing:
        assigned_person = db.query(User).filter(User.id == pairing.receiver_id).first()

    # Check if pairings exist
    pairings_exist = pairing_exists(db)

    # Get pairing status for all users (for admin view)
    # Create a dictionary mapping user_id -> has_pairing
    user_pairing_status = {}
    if pairings_exist:
        all_pairings = db.query(Pairing).all()
        users_with_pairings = {p.gifter_id for p in all_pairings}
        for u in all_users:
            user_pairing_status[u.id] = u.id in users_with_pairings
    else:
        for u in all_users:
            user_pairing_status[u.id] = False

    # Get registration status
    registration_setting = db.query(Settings).filter(Settings.key == "registration_open").first()
    registration_open = registration_setting.value.lower() == "true" if registration_setting else True

    # Get error/success messages from query parameters
    error_message = request.query_params.get("error")
    success_message = request.query_params.get("success")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "all_users": all_users,
            "assigned_person": assigned_person,
            "pairings_exist": pairings_exist,
            "registration_open": registration_open,
            "user_pairing_status": user_pairing_status,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@router.post("/logout")
async def logout():
    """Logout user."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

