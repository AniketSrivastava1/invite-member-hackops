from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Team(Base):
    """Team model representing a hackathon team"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    leader_name = Column(String(100), nullable=False)
    leader_email = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    max_members = Column(Integer, default=5, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    members = relationship("Member", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, leader={self.leader_name})>"


class Member(Base):
    """Member model representing a team member"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(15), nullable=True, index=True)  # Added phone number
    role = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to team
    team = relationship("Team", back_populates="members")
    
    def __repr__(self):
        return f"<Member(id={self.id}, name={self.name}, team_id={self.team_id})>"


class Invitation(Base):
    """Invitation model for team invitations"""
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to team
    team = relationship("Team", back_populates="invitations")
    
    def __repr__(self):
        return f"<Invitation(id={self.id}, email={self.email}, token={self.token})>"


class OTP(Base):
    """OTP model for phone verification"""
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    invitation_token = Column(String(100), nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<OTP(id={self.id}, phone={self.phone}, verified={self.is_verified})>"
