from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models
import schemas
from database import engine, get_db
from utils import (
    generate_invite_token, 
    generate_otp, 
    get_invitation_expiry, 
    get_otp_expiry, 
    is_expired,
    format_phone_number
)
from sms_service import send_otp_sms
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hackathon Team Management API",
    description="API for managing hackathon teams with invitation system",
    version="2.0.0"
)

# Base URL for invitation links
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Hackathon Team Management API"}


@app.post("/api/teams/", response_model=schemas.TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team for the hackathon
    
    - **name**: Team name (unique)
    - **leader_name**: Name of the team leader
    - **leader_email**: Email of the team leader
    - **description**: Team description
    - **max_members**: Maximum team size (default: 5)
    """
    # Check if team name already exists
    existing_team = db.query(models.Team).filter(models.Team.name == team.name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already exists"
        )
    
    # Check if email is already a team leader
    existing_leader = db.query(models.Team).filter(
        models.Team.leader_email == team.leader_email
    ).first()
    if existing_leader:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered as a team leader"
        )
    
    # Create team
    db_team = models.Team(
        name=team.name,
        leader_name=team.leader_name,
        leader_email=team.leader_email,
        description=team.description,
        max_members=team.max_members
    )
    
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    return db_team


@app.get("/api/teams/", response_model=List[schemas.TeamResponse])
def get_all_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all teams
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return teams


@app.get("/api/teams/{team_id}", response_model=schemas.TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team by ID"""
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return team


@app.put("/api/teams/{team_id}", response_model=schemas.TeamResponse)
def update_team(team_id: int, team_update: schemas.TeamUpdate, db: Session = Depends(get_db)):
    """
    Update team details (only team leader can update)
    """
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Update fields if provided
    if team_update.name is not None:
        # Check if new name already exists
        existing_team = db.query(models.Team).filter(
            models.Team.name == team_update.name,
            models.Team.id != team_id
        ).first()
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name already exists"
            )
        db_team.name = team_update.name
    
    if team_update.description is not None:
        db_team.description = team_update.description
    
    if team_update.max_members is not None:
        db_team.max_members = team_update.max_members
    
    db.commit()
    db.refresh(db_team)
    
    return db_team


@app.delete("/api/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team"""
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    db.delete(db_team)
    db.commit()
    
    return None


@app.post("/api/teams/{team_id}/members/", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(team_id: int, member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """
    Add a member to a team
    """
    # Check if team exists
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if team is full
    current_members = db.query(models.Member).filter(models.Member.team_id == team_id).count()
    if current_members >= db_team.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full (max {db_team.max_members} members)"
        )
    
    # Check if member email already exists in this team
    existing_member = db.query(models.Member).filter(
        models.Member.team_id == team_id,
        models.Member.email == member.email
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member with this email already exists in the team"
        )
    
    # Create member
    db_member = models.Member(
        team_id=team_id,
        name=member.name,
        email=member.email,
        role=member.role
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return db_member


@app.get("/api/teams/{team_id}/members/", response_model=List[schemas.MemberResponse])
def get_team_members(team_id: int, db: Session = Depends(get_db)):
    """Get all members of a specific team"""
    # Check if team exists
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    members = db.query(models.Member).filter(models.Member.team_id == team_id).all()
    return members


@app.delete("/api/teams/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(team_id: int, member_id: int, db: Session = Depends(get_db)):
    """Remove a member from a team"""
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.team_id == team_id
    ).first()
    
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this team"
        )
    
    db.delete(db_member)
    db.commit()
    
    return None


# ==================== INVITATION ENDPOINTS ====================

@app.post("/api/teams/{team_id}/invitations/", response_model=schemas.InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    team_id: int, 
    invitation: schemas.InvitationCreate, 
    db: Session = Depends(get_db)
):
    """
    Create an invitation link for a team member
    
    - Generates a unique invite token
    - Optionally sends OTP to phone number if provided
    - Returns invitation link and details
    """
    # Check if team exists
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if team is full
    current_members = db.query(models.Member).filter(models.Member.team_id == team_id).count()
    if current_members >= db_team.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full (max {db_team.max_members} members)"
        )
    
    # Check if email already has a pending invitation
    existing_invitation = db.query(models.Invitation).filter(
        models.Invitation.team_id == team_id,
        models.Invitation.email == invitation.email,
        models.Invitation.is_used == False,
        models.Invitation.expires_at > datetime.utcnow()
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active invitation already exists for this email"
        )
    
    # Check if email is already a team member
    existing_member = db.query(models.Member).filter(
        models.Member.team_id == team_id,
        models.Member.email == invitation.email
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already a member of the team"
        )
    
    # Format phone number if provided
    formatted_phone = None
    if invitation.phone:
        formatted_phone = format_phone_number(invitation.phone)
    
    # Generate invitation token
    token = generate_invite_token()
    expires_at = get_invitation_expiry()
    
    # Create invitation
    db_invitation = models.Invitation(
        team_id=team_id,
        email=invitation.email,
        phone=formatted_phone,
        token=token,
        expires_at=expires_at
    )
    
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    
    # Generate OTP if phone number provided
    if formatted_phone:
        otp_code = generate_otp()
        otp_expires_at = get_otp_expiry()
        
        # Save OTP to database
        db_otp = models.OTP(
            phone=formatted_phone,
            otp_code=otp_code,
            invitation_token=token,
            expires_at=otp_expires_at
        )
        db.add(db_otp)
        db.commit()
        
        # Send OTP via SMS
        send_otp_sms(formatted_phone, otp_code)
    
    # Generate invitation link
    invite_link = f"{BASE_URL}/join/{token}"
    
    return {
        "id": db_invitation.id,
        "team_id": db_invitation.team_id,
        "email": db_invitation.email,
        "phone": db_invitation.phone,
        "token": db_invitation.token,
        "invite_link": invite_link,
        "is_used": db_invitation.is_used,
        "expires_at": db_invitation.expires_at,
        "created_at": db_invitation.created_at
    }


@app.get("/api/teams/{team_id}/invitations/", response_model=List[schemas.InvitationResponse])
def get_team_invitations(team_id: int, db: Session = Depends(get_db)):
    """Get all invitations for a team"""
    # Check if team exists
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    invitations = db.query(models.Invitation).filter(
        models.Invitation.team_id == team_id
    ).all()
    
    # Add invite links to response
    result = []
    for inv in invitations:
        result.append({
            "id": inv.id,
            "team_id": inv.team_id,
            "email": inv.email,
            "phone": inv.phone,
            "token": inv.token,
            "invite_link": f"{BASE_URL}/join/{inv.token}",
            "is_used": inv.is_used,
            "expires_at": inv.expires_at,
            "created_at": inv.created_at
        })
    
    return result


@app.get("/api/invitations/{token}")
def get_invitation_details(token: str, db: Session = Depends(get_db)):
    """
    Get invitation details by token
    Used when someone clicks the invitation link
    """
    invitation = db.query(models.Invitation).filter(
        models.Invitation.token == token
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has already been used"
        )
    
    if is_expired(invitation.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    # Get team details
    team = db.query(models.Team).filter(models.Team.id == invitation.team_id).first()
    
    return {
        "invitation": {
            "email": invitation.email,
            "phone": invitation.phone,
            "expires_at": invitation.expires_at,
            "requires_otp": invitation.phone is not None
        },
        "team": {
            "id": team.id,
            "name": team.name,
            "leader_name": team.leader_name,
            "description": team.description
        }
    }


@app.post("/api/invitations/{token}/resend-otp", response_model=schemas.OTPResponse)
def resend_otp(token: str, db: Session = Depends(get_db)):
    """
    Resend OTP for an invitation
    """
    # Get invitation
    invitation = db.query(models.Invitation).filter(
        models.Invitation.token == token
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if not invitation.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation does not have a phone number"
        )
    
    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has already been used"
        )
    
    if is_expired(invitation.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    # Invalidate old OTPs
    db.query(models.OTP).filter(
        models.OTP.invitation_token == token,
        models.OTP.is_verified == False
    ).delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    otp_expires_at = get_otp_expiry()
    
    db_otp = models.OTP(
        phone=invitation.phone,
        otp_code=otp_code,
        invitation_token=token,
        expires_at=otp_expires_at
    )
    
    db.add(db_otp)
    db.commit()
    
    # Send OTP
    send_otp_sms(invitation.phone, otp_code)
    
    return {
        "message": "OTP sent successfully",
        "phone": invitation.phone,
        "expires_at": otp_expires_at
    }


@app.post("/api/invitations/verify-otp")
def verify_otp(otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    """
    Verify OTP for an invitation
    """
    # Get OTP record
    otp_record = db.query(models.OTP).filter(
        models.OTP.invitation_token == otp_data.invitation_token,
        models.OTP.otp_code == otp_data.otp_code,
        models.OTP.is_verified == False
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
    
    if is_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    # Mark OTP as verified
    otp_record.is_verified = True
    db.commit()
    
    return {
        "message": "OTP verified successfully",
        "verified": True
    }


@app.post("/api/invitations/{token}/join", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def join_team_via_invitation(
    token: str, 
    join_data: schemas.JoinTeamRequest, 
    db: Session = Depends(get_db)
):
    """
    Join a team using invitation token
    
    - Validates invitation
    - Checks OTP verification if phone number was provided
    - Adds member to team
    - Marks invitation as used
    """
    # Get invitation
    invitation = db.query(models.Invitation).filter(
        models.Invitation.token == token
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has already been used"
        )
    
    if is_expired(invitation.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
    # Check if OTP verification is required
    if invitation.phone:
        verified_otp = db.query(models.OTP).filter(
            models.OTP.invitation_token == token,
            models.OTP.is_verified == True
        ).first()
        
        if not verified_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP verification required. Please verify your phone number first."
            )
    
    # Check if team is full
    team = db.query(models.Team).filter(models.Team.id == invitation.team_id).first()
    current_members = db.query(models.Member).filter(
        models.Member.team_id == invitation.team_id
    ).count()
    
    if current_members >= team.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full (max {team.max_members} members)"
        )
    
    # Create member
    db_member = models.Member(
        team_id=invitation.team_id,
        name=join_data.name,
        email=invitation.email,
        phone=invitation.phone,
        role=join_data.role
    )
    
    db.add(db_member)
    
    # Mark invitation as used
    invitation.is_used = True
    
    db.commit()
    db.refresh(db_member)
    
    return db_member
