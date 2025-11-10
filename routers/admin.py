from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models import User, Settings
from pairing import create_pairings, reshuffle_all_pairings, assign_users_without_pairs
from routers.users import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/toggle-registration")
async def toggle_registration(request: Request, db: Session = Depends(get_db)):
    """Toggle registration open/closed (admin only)."""
    user = get_current_user(request, db)
    print(f"DEBUG: Toggle registration - user: {user}, is_admin: {user.is_admin if user else 'None'}")
    
    if not user:
        # Redirect to login if not authenticated
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not user.is_admin:
        # Redirect back to dashboard with error
        return RedirectResponse(url="/dashboard?error=Admin access required", status_code=status.HTTP_302_FOUND)

    # Toggle registration status
    registration_setting = db.query(Settings).filter(Settings.key == "registration_open").first()
    if registration_setting:
        new_value = "false" if registration_setting.value.lower() == "true" else "true"
        registration_setting.value = new_value
    else:
        registration_setting = Settings(key="registration_open", value="false")
        db.add(registration_setting)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@router.post("/create-pairings")
async def admin_create_pairings(request: Request, db: Session = Depends(get_db)):
    """Create Secret Santa pairings (admin only). Only works when no pairings exist."""
    user = get_current_user(request, db)
    print(f"DEBUG: Admin create pairings - user: {user}, is_admin: {user.is_admin if user else 'None'}")
    
    if not user:
        # Redirect to login if not authenticated
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not user.is_admin:
        # Redirect back to dashboard with error (we'll show error on dashboard)
        return RedirectResponse(url="/dashboard?error=Admin access required", status_code=status.HTTP_302_FOUND)

    # Check if any pairings already exist
    from pairing import pairing_exists
    if pairing_exists(db):
        return RedirectResponse(
            url="/dashboard?error=Cannot create pairings when some users already have pairs. Use 'Assign Unpaired Users' instead.",
            status_code=status.HTTP_302_FOUND
        )

    result = create_pairings(db)
    if not result["success"]:
        # Redirect with error message
        return RedirectResponse(url=f"/dashboard?error={result.get('message', 'Failed to create pairings')}", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/dashboard?success=Pairings created successfully", status_code=status.HTTP_302_FOUND)


@router.post("/reshuffle-pairings")
async def admin_reshuffle_pairings(request: Request, db: Session = Depends(get_db)):
    """Reshuffle all pairings - clears existing and creates new ones (admin only)."""
    user = get_current_user(request, db)
    print(f"DEBUG: Admin reshuffle pairings - user: {user}, is_admin: {user.is_admin if user else 'None'}")
    
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not user.is_admin:
        return RedirectResponse(url="/dashboard?error=Admin access required", status_code=status.HTTP_302_FOUND)

    result = reshuffle_all_pairings(db)
    if not result["success"]:
        return RedirectResponse(url=f"/dashboard?error={result.get('message', 'Failed to reshuffle pairings')}", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/dashboard?success=All pairings reshuffled successfully", status_code=status.HTTP_302_FOUND)


@router.post("/assign-users-without-pairs")
async def admin_assign_users_without_pairs(request: Request, db: Session = Depends(get_db)):
    """Assign pairings only for users without pairs, leaving existing pairs untouched (admin only)."""
    user = get_current_user(request, db)
    print(f"DEBUG: Admin assign users without pairs - user: {user}, is_admin: {user.is_admin if user else 'None'}")
    
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not user.is_admin:
        return RedirectResponse(url="/dashboard?error=Admin access required", status_code=status.HTTP_302_FOUND)

    result = assign_users_without_pairs(db)
    if not result["success"]:
        return RedirectResponse(url=f"/dashboard?error={result.get('message', 'Failed to assign users')}", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/dashboard?success={result.get('message', 'Users assigned successfully')}", status_code=status.HTTP_302_FOUND)

