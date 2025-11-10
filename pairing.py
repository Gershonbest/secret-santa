import random
from sqlalchemy.orm import Session
from models import User, Pairing
from typing import List, Dict


def create_pairings(db: Session) -> Dict[str, any]:
    """
    Create Secret Santa pairings for all users.
    Ensures one-to-one mapping with no self-assignments.
    Returns a dict with success status and message.
    Requires at least 2 users to create pairings.
    """
    # Get all users
    users = db.query(User).all()
    
    if len(users) < 2:
        return {"success": False, "message": "Need at least 2 members to create pairings"}
    
    # Clear existing pairings
    db.query(Pairing).delete()
    db.commit()
    
    # Create a list of user IDs
    user_ids = [user.id for user in users]
    
    # Shuffle to randomize
    random.shuffle(user_ids)
    
    # Create pairings: each user gives to the next one, last gives to first
    pairings = []
    for i in range(len(user_ids)):
        gifter_id = user_ids[i]
        receiver_id = user_ids[(i + 1) % len(user_ids)]  # Circular assignment
        
        # Double-check no self-assignment (shouldn't happen with this logic, but safety check)
        if gifter_id == receiver_id:
            # This should never happen, but if it does, reshuffle
            return create_pairings(db)
        
        pairing = Pairing(gifter_id=gifter_id, receiver_id=receiver_id)
        pairings.append(pairing)
        db.add(pairing)
    
    try:
        db.commit()
        return {"success": True, "message": f"Successfully created {len(pairings)} pairings"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error creating pairings: {str(e)}"}


def get_user_pairing(db: Session, user_id: int) -> Pairing:
    """Get the pairing for a specific user (who they are gifting to)."""
    return db.query(Pairing).filter(Pairing.gifter_id == user_id).first()


def get_all_pairings(db: Session) -> List[Pairing]:
    """Get all pairings (admin only)."""
    return db.query(Pairing).all()


def pairing_exists(db: Session) -> bool:
    """Check if pairings have been created."""
    return db.query(Pairing).count() > 0


def assign_new_user(db: Session, new_user_id: int) -> Dict[str, any]:
    """
    Assign a newly registered user to the pairing system without disrupting existing pairings.
    This allows late registrations without reshuffling existing assignments.
    """
    # Check if pairings exist
    existing_pairings = db.query(Pairing).all()
    if not existing_pairings:
        return {"success": False, "message": "No existing pairings found. Admin must create initial pairings first."}
    
    # Get all users
    all_users = db.query(User).all()
    all_user_ids = {user.id for user in all_users}
    
    # Get users who already have pairings (as gifter)
    users_with_pairings = {pairing.gifter_id for pairing in existing_pairings}
    
    # Check if new user already has a pairing
    if new_user_id in users_with_pairings:
        return {"success": True, "message": "User already has a pairing"}
    
    # Get all users who are currently receivers
    current_receivers = {pairing.receiver_id for pairing in existing_pairings}
    
    # Find users who don't have anyone gifting to them yet
    # These are users who are not in the receiver list
    available_receivers = all_user_ids - current_receivers - {new_user_id}
    
    if not available_receivers:
        # If all users are already receivers, we need to insert the new user into the chain
        # We'll modify one existing pairing to include the new user
        # Strategy: Find a pairing where we can insert the new user
        # The new user will gift to someone, and someone will gift to the new user
        import random
        
        # Pick a random existing pairing to modify
        # We'll change: A -> B to A -> NewUser -> B
        pairing_to_modify = random.choice(existing_pairings)
        old_gifter = pairing_to_modify.gifter_id
        old_receiver = pairing_to_modify.receiver_id
        
        # Create two new pairings:
        # 1. Old gifter now gifts to new user
        # 2. New user gifts to old receiver
        pairing_to_modify.receiver_id = new_user_id
        new_pairing = Pairing(gifter_id=new_user_id, receiver_id=old_receiver)
        db.add(new_pairing)
        
        try:
            db.commit()
            return {"success": True, "message": f"New user inserted into pairing chain between users {old_gifter} and {old_receiver}"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error assigning new user: {str(e)}"}
    else:
        # We have users who don't have anyone gifting to them
        # Assign the new user to gift one of them
        import random
        selected_receiver = random.choice(list(available_receivers))
        
        new_pairing = Pairing(gifter_id=new_user_id, receiver_id=selected_receiver)
        db.add(new_pairing)
        
        try:
            db.commit()
            return {"success": True, "message": f"New user assigned to gift user ID {selected_receiver}"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error assigning new user: {str(e)}"}


def get_users_without_gifters(db: Session) -> List[int]:
    """Get list of user IDs who don't have anyone gifting to them."""
    all_users = db.query(User).all()
    all_user_ids = {user.id for user in all_users}
    
    existing_pairings = db.query(Pairing).all()
    users_with_gifters = {pairing.receiver_id for pairing in existing_pairings}
    
    return list(all_user_ids - users_with_gifters)


def reshuffle_all_pairings(db: Session) -> Dict[str, any]:
    """
    Reshuffle all pairings - clears existing pairings and creates new ones for all users.
    This will reassign everyone, including those who already had pairs.
    """
    # This is essentially the same as create_pairings, but with a clearer name
    return create_pairings(db)


def assign_users_without_pairs(db: Session) -> Dict[str, any]:
    """
    Assign pairings only for users who don't have pairs yet.
    Users with existing pairs will not be affected.
    Requires at least 2 unpaired members to create pairings.
    """
    # Get all users
    all_users = db.query(User).all()
    all_user_ids = {user.id for user in all_users}
    
    if len(all_user_ids) < 2:
        return {"success": False, "message": "Need at least 2 users to create pairings"}
    
    # Get existing pairings
    existing_pairings = db.query(Pairing).all()
    users_with_pairings = {pairing.gifter_id for pairing in existing_pairings}
    
    # Find users without pairings
    users_without_pairings = all_user_ids - users_with_pairings
    
    if not users_without_pairings:
        return {"success": True, "message": "All users already have pairings. No action needed."}
    
    # Check if there are at least 2 unpaired members
    if len(users_without_pairings) < 2:
        return {"success": False, "message": f"Need at least 2 unpaired members to create pairings. Currently only {len(users_without_pairings)} unpaired member(s)."}
    
    if len(users_without_pairings) == 2:
        # Exactly 2 users without pairing - create a pair between them
        users_list = list(users_without_pairings)
        random.shuffle(users_list)
        gifter_id = users_list[0]
        receiver_id = users_list[1]
        
        new_pairing = Pairing(gifter_id=gifter_id, receiver_id=receiver_id)
        db.add(new_pairing)
        
        try:
            db.commit()
            return {"success": True, "message": f"Successfully paired 2 unpaired members"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error creating pairing: {str(e)}"}
    
    # Get all current receivers
    current_receivers = {pairing.receiver_id for pairing in existing_pairings}
    
    # Find available receivers (users who don't have gifters yet)
    available_receivers = all_user_ids - current_receivers
    
    # Shuffle users without pairings
    users_to_assign = list(users_without_pairings)
    random.shuffle(users_to_assign)
    
    # Try to create a circular chain among users without pairings
    # and connect them to users who don't have gifters
    assigned_count = 0
    new_pairings = []
    
    # First, try to assign users without pairings to available receivers
    assigned_gifters = set()
    for gifter_id in users_to_assign:
        if available_receivers:
            # Assign to an available receiver
            receiver_id = random.choice(list(available_receivers))
            available_receivers.remove(receiver_id)
            
            new_pairing = Pairing(gifter_id=gifter_id, receiver_id=receiver_id)
            db.add(new_pairing)
            new_pairings.append(new_pairing)
            assigned_gifters.add(gifter_id)
            assigned_count += 1
    
    # If there are still users without pairings, create a circular chain among them
    remaining_unassigned = users_without_pairings - assigned_gifters
    if len(remaining_unassigned) > 1:
        remaining_list = list(remaining_unassigned)
        random.shuffle(remaining_list)
        for i in range(len(remaining_list)):
            gifter_id = remaining_list[i]
            receiver_id = remaining_list[(i + 1) % len(remaining_list)]
            new_pairing = Pairing(gifter_id=gifter_id, receiver_id=receiver_id)
            db.add(new_pairing)
            new_pairings.append(new_pairing)
            assigned_count += 1
    elif len(remaining_unassigned) == 1:
        # One remaining user - insert into existing chain
        new_user_id = list(remaining_unassigned)[0]
        result = assign_new_user(db, new_user_id)
        if result["success"]:
            assigned_count += 1
    
    try:
        db.commit()
        return {"success": True, "message": f"Successfully assigned {assigned_count} users without disrupting existing pairings"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error assigning users: {str(e)}"}

