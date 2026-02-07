import secrets
import string
from datetime import datetime, timedelta
import hashlib


def generate_invite_token(length: int = 32) -> str:
    """
    Generate a secure random token for invitations
    
    Args:
        length: Length of the token (default: 32)
    
    Returns:
        Random alphanumeric token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP
    
    Args:
        length: Length of OTP (default: 6)
    
    Returns:
        Numeric OTP string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def get_invitation_expiry(hours: int = 48) -> datetime:
    """
    Get expiration datetime for invitation
    
    Args:
        hours: Hours until expiration (default: 48)
    
    Returns:
        Expiration datetime
    """
    return datetime.utcnow() + timedelta(hours=hours)


def get_otp_expiry(minutes: int = 10) -> datetime:
    """
    Get expiration datetime for OTP
    
    Args:
        minutes: Minutes until expiration (default: 10)
    
    Returns:
        Expiration datetime
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


def is_expired(expiry_time: datetime) -> bool:
    """
    Check if a datetime has expired
    
    Args:
        expiry_time: Expiration datetime to check
    
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expiry_time


def format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format
    
    Args:
        phone: Phone number string
    
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add + prefix if not present
    if not phone.startswith('+'):
        return f"+{digits}"
    
    return f"+{digits}"
