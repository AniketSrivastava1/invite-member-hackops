from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Member Schemas
class MemberBase(BaseModel):
    """Base schema for Member"""
    name: str = Field(..., min_length=1, max_length=100, description="Member name")
    email: EmailStr = Field(..., description="Member email")
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$", description="Member phone number (E.164 format)")
    role: Optional[str] = Field(None, max_length=100, description="Member role (e.g., Developer, Designer)")


class MemberCreate(MemberBase):
    """Schema for creating a new member"""
    pass


class MemberResponse(MemberBase):
    """Schema for member response"""
    id: int
    team_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Team Schemas
class TeamBase(BaseModel):
    """Base schema for Team"""
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    leader_name: str = Field(..., min_length=1, max_length=100, description="Team leader name")
    leader_email: EmailStr = Field(..., description="Team leader email")
    description: Optional[str] = Field(None, description="Team description")
    max_members: int = Field(default=5, ge=1, le=20, description="Maximum number of team members")


class TeamCreate(TeamBase):
    """Schema for creating a new team"""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating team details"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    max_members: Optional[int] = Field(None, ge=1, le=20)


class TeamResponse(TeamBase):
    """Schema for team response"""
    id: int
    created_at: datetime
    updated_at: datetime
    members: List[MemberResponse] = []
    
    class ConfigDict:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Schema for listing teams without member details"""
    id: int
    name: str
    leader_name: str
    leader_email: EmailStr
    description: Optional[str]
    max_members: int
    member_count: int
    created_at: datetime
    
    class ConfigDict:
        from_attributes = True


# Invitation Schemas
class InvitationCreate(BaseModel):
    """Schema for creating an invitation"""
    email: EmailStr = Field(..., description="Email of the person to invite")
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number for OTP (E.164 format)")


class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: int
    team_id: int
    email: EmailStr
    phone: Optional[str]
    token: str
    invite_link: str
    is_used: bool
    expires_at: datetime
    created_at: datetime
    
    class ConfigDict:
        from_attributes = True


# OTP Schemas
class OTPVerify(BaseModel):
    """Schema for OTP verification"""
    invitation_token: str = Field(..., description="Invitation token")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class OTPResponse(BaseModel):
    """Schema for OTP response"""
    message: str
    phone: str
    expires_at: datetime


class JoinTeamRequest(BaseModel):
    """Schema for joining a team via invitation"""
    name: str = Field(..., min_length=1, max_length=100, description="Member name")
    role: Optional[str] = Field(None, max_length=100, description="Member role")
