"""
SMS Service for sending OTP

This module provides SMS functionality using Twilio.
For testing purposes, it includes a mock SMS sender.
"""

import os
from typing import Optional


class SMSService:
    """Service for sending SMS messages"""
    
    def __init__(self):
        """Initialize SMS service with credentials"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.use_mock = os.getenv("USE_MOCK_SMS", "true").lower() == "true"
        
        if not self.use_mock:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except ImportError:
                print("Warning: Twilio not installed. Install with: pip install twilio")
                self.use_mock = True
    
    def send_otp(self, phone: str, otp: str) -> bool:
        """
        Send OTP to phone number
        
        Args:
            phone: Phone number in E.164 format
            otp: OTP code to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        message = f"Your OTP for hackathon team invitation is: {otp}. Valid for 10 minutes."
        
        if self.use_mock:
            return self._send_mock_sms(phone, message)
        
        return self._send_twilio_sms(phone, message)
    
    def _send_mock_sms(self, phone: str, message: str) -> bool:
        """
        Mock SMS sender for development/testing
        
        Args:
            phone: Phone number
            message: Message to send
        
        Returns:
            Always returns True
        """
        print(f"\n{'='*60}")
        print("MOCK SMS SENT")
        print(f"{'='*60}")
        print(f"To: {phone}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        return True
    
    def _send_twilio_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS using Twilio
        
        Args:
            phone: Phone number in E.164 format
            message: Message to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone
            )
            print(f"SMS sent successfully. SID: {message.sid}")
            return True
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False


# Create singleton instance
sms_service = SMSService()


def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Convenience function to send OTP
    
    Args:
        phone: Phone number in E.164 format
        otp: OTP code
    
    Returns:
        True if sent successfully
    """
    return sms_service.send_otp(phone, otp)
