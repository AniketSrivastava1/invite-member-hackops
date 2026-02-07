"""
Comprehensive test script for Hackathon Team API with Invitation System
Run this after starting the FastAPI server
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_response(response, operation):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"{operation}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print(f"{'='*70}\n")
    return response


def test_invitation_flow():
    """Test the complete invitation flow"""
    
    print("\n" + "="*70)
    print("TESTING INVITATION AND OTP FLOW")
    print("="*70)
    
    # Step 1: Create a team
    print("\n>>> STEP 1: Creating a team...")
    team_data = {
        "name": "Innovation Squad",
        "leader_name": "Alice Johnson",
        "leader_email": "alice@innovationsquad.com",
        "description": "Building the next generation of AI tools",
        "max_members": 5
    }
    
    response = print_response(
        requests.post(f"{BASE_URL}/api/teams/", json=team_data),
        "1. CREATE TEAM"
    )
    
    if response.status_code != 201:
        print("Failed to create team. Exiting...")
        return
    
    team_id = response.json()["id"]
    print(f"✓ Team created with ID: {team_id}")
    
    # Step 2: Create invitation with phone number (OTP required)
    print("\n>>> STEP 2: Creating invitation with phone number...")
    invitation_data = {
        "email": "bob@example.com",
        "phone": "+919876543210"  # Indian phone number format
    }
    
    response = print_response(
        requests.post(f"{BASE_URL}/api/teams/{team_id}/invitations/", json=invitation_data),
        "2. CREATE INVITATION WITH PHONE"
    )
    
    if response.status_code != 201:
        print("Failed to create invitation. Exiting...")
        return
    
    invitation_token = response.json()["token"]
    invite_link = response.json()["invite_link"]
    print(f"✓ Invitation created")
    print(f"  Token: {invitation_token}")
    print(f"  Link: {invite_link}")
    print(f"  OTP sent to: {invitation_data['phone']}")
    
    # Step 3: Get invitation details
    print("\n>>> STEP 3: Getting invitation details...")
    response = print_response(
        requests.get(f"{BASE_URL}/api/invitations/{invitation_token}"),
        "3. GET INVITATION DETAILS"
    )
    
    # Step 4: Simulate OTP verification (get OTP from console output in mock mode)
    print("\n>>> STEP 4: OTP Verification...")
    print("Check the server console for the OTP code (in mock mode)")
    print("In production, user would receive SMS")
    
    # For testing, we'll use a known OTP from the database
    # In real scenario, user gets this via SMS
    otp_code = input("\nEnter the OTP code from server console (or press Enter to skip): ").strip()
    
    if otp_code:
        otp_verify_data = {
            "invitation_token": invitation_token,
            "otp_code": otp_code
        }
        
        response = print_response(
            requests.post(f"{BASE_URL}/api/invitations/verify-otp", json=otp_verify_data),
            "4. VERIFY OTP"
        )
        
        if response.status_code == 200:
            print("✓ OTP verified successfully!")
        else:
            print("✗ OTP verification failed. Try resending OTP.")
    else:
        print("⊘ Skipping OTP verification (for testing without OTP)")
    
    # Step 5: Resend OTP (optional test)
    print("\n>>> STEP 5: Testing OTP resend...")
    response = print_response(
        requests.post(f"{BASE_URL}/api/invitations/{invitation_token}/resend-otp"),
        "5. RESEND OTP"
    )
    
    # Step 6: Join team via invitation (if OTP verified or skipped)
    print("\n>>> STEP 6: Joining team via invitation...")
    join_data = {
        "name": "Bob Smith",
        "role": "Backend Developer"
    }
    
    response = print_response(
        requests.post(f"{BASE_URL}/api/invitations/{invitation_token}/join", json=join_data),
        "6. JOIN TEAM VIA INVITATION"
    )
    
    if response.status_code == 201:
        print("✓ Successfully joined the team!")
    elif response.status_code == 400 and "OTP verification required" in response.text:
        print("⚠ OTP verification is required to join the team")
    
    # Step 7: Create invitation without phone (no OTP required)
    print("\n>>> STEP 7: Creating invitation without phone number...")
    invitation_data_no_phone = {
        "email": "charlie@example.com"
    }
    
    response = print_response(
        requests.post(f"{BASE_URL}/api/teams/{team_id}/invitations/", json=invitation_data_no_phone),
        "7. CREATE INVITATION WITHOUT PHONE"
    )
    
    if response.status_code == 201:
        token_no_phone = response.json()["token"]
        print(f"✓ Invitation created (no OTP required)")
        print(f"  Token: {token_no_phone}")
        
        # Join team directly (no OTP verification needed)
        join_data_2 = {
            "name": "Charlie Davis",
            "role": "Frontend Developer"
        }
        
        response = print_response(
            requests.post(f"{BASE_URL}/api/invitations/{token_no_phone}/join", json=join_data_2),
            "8. JOIN TEAM WITHOUT OTP"
        )
    
    # Step 8: Get all team invitations
    print("\n>>> STEP 9: Getting all team invitations...")
    response = print_response(
        requests.get(f"{BASE_URL}/api/teams/{team_id}/invitations/"),
        "9. GET ALL TEAM INVITATIONS"
    )
    
    # Step 9: Get team details with members
    print("\n>>> STEP 10: Getting team details...")
    response = print_response(
        requests.get(f"{BASE_URL}/api/teams/{team_id}"),
        "10. GET TEAM DETAILS WITH MEMBERS"
    )
    
    # Step 10: Get all team members
    print("\n>>> STEP 11: Getting all team members...")
    response = print_response(
        requests.get(f"{BASE_URL}/api/teams/{team_id}/members/"),
        "11. GET TEAM MEMBERS"
    )
    
    # Step 11: Test error cases
    print("\n>>> STEP 12: Testing error cases...")
    
    # Try to use invitation again
    print("\nTrying to reuse invitation token...")
    response = print_response(
        requests.post(f"{BASE_URL}/api/invitations/{token_no_phone}/join", json=join_data_2),
        "12a. TRY TO REUSE INVITATION (Should Fail)"
    )
    
    # Try to create duplicate invitation
    print("\nTrying to create duplicate invitation...")
    response = print_response(
        requests.post(f"{BASE_URL}/api/teams/{team_id}/invitations/", json=invitation_data_no_phone),
        "12b. TRY TO CREATE DUPLICATE INVITATION (Should Fail)"
    )
    
    print("\n" + "="*70)
    print("INVITATION FLOW TEST COMPLETE!")
    print("="*70)


def test_basic_flow():
    """Test basic team creation without invitations"""
    
    print("\n" + "="*70)
    print("TESTING BASIC TEAM CREATION")
    print("="*70)
    
    # Create a simple team
    team_data = {
        "name": "Quick Team",
        "leader_name": "David Lee",
        "leader_email": "david@quickteam.com",
        "description": "Rapid prototyping team",
        "max_members": 3
    }
    
    response = print_response(
        requests.post(f"{BASE_URL}/api/teams/", json=team_data),
        "CREATE BASIC TEAM"
    )
    
    if response.status_code == 201:
        team_id = response.json()["id"]
        
        # Add member directly (old method)
        member_data = {
            "name": "Emma Wilson",
            "email": "emma@example.com",
            "phone": "+919123456789",
            "role": "UI/UX Designer"
        }
        
        response = print_response(
            requests.post(f"{BASE_URL}/api/teams/{team_id}/members/", json=member_data),
            "ADD MEMBER DIRECTLY"
        )


if __name__ == "__main__":
    print("\n" + "="*70)
    print("HACKATHON TEAM API - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start server with: uvicorn main:app --reload")
    print("="*70)
    
    try:
        # Check if server is running
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✓ Server is running!")
            
            print("\n" + "="*70)
            print("SELECT TEST TO RUN:")
            print("="*70)
            print("1. Full Invitation & OTP Flow (Recommended)")
            print("2. Basic Team Creation (No Invitations)")
            print("3. Both Tests")
            print("="*70)
            
            choice = input("Enter choice (1-3, default: 1): ").strip() or "1"
            
            if choice == "1":
                test_invitation_flow()
            elif choice == "2":
                test_basic_flow()
            elif choice == "3":
                test_basic_flow()
                time.sleep(2)
                test_invitation_flow()
            else:
                print("Invalid choice. Running full invitation flow...")
                test_invitation_flow()
                
        else:
            print("✗ Server responded with unexpected status code")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Please start the FastAPI server first.")
        print("  Run: uvicorn main:app --reload")
