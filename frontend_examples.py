"""
Frontend Integration Examples
==============================

This file contains example JavaScript/TypeScript code snippets for integrating
the Hackathon Team API with your frontend application.
"""

# Example 1: Create Invitation and Send OTP
'''
async function createInvitation(teamId, email, phone) {
  try {
    const response = await fetch(`http://localhost:8000/api/teams/${teamId}/invitations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        phone: phone  // Optional: include for OTP verification
      })
    });

    if (!response.ok) {
      throw new Error('Failed to create invitation');
    }

    const data = await response.json();
    
    // Display invitation link to team leader
    console.log('Invitation Link:', data.invite_link);
    console.log('Token:', data.token);
    
    // Show success message
    alert(`Invitation sent to ${email}. ${phone ? 'OTP sent to ' + phone : ''}`);
    
    return data;
  } catch (error) {
    console.error('Error creating invitation:', error);
    alert('Failed to create invitation');
  }
}

// Usage
createInvitation(1, 'newmember@example.com', '+919876543210');
'''

# Example 2: Join Team Flow (Member's Perspective)
'''
// Step 1: Get invitation details when user visits /join/:token
async function getInvitationDetails(token) {
  try {
    const response = await fetch(`http://localhost:8000/api/invitations/${token}`);
    
    if (!response.ok) {
      if (response.status === 400) {
        const error = await response.json();
        alert(error.detail); // "Invitation expired" or "Already used"
        return null;
      }
      throw new Error('Failed to fetch invitation');
    }

    const data = await response.json();
    
    // Display team information to user
    console.log('Team:', data.team.name);
    console.log('Leader:', data.team.leader_name);
    console.log('Requires OTP:', data.invitation.requires_otp);
    
    return data;
  } catch (error) {
    console.error('Error fetching invitation:', error);
    return null;
  }
}

// Step 2: Verify OTP (if phone was provided)
async function verifyOTP(token, otpCode) {
  try {
    const response = await fetch('http://localhost:8000/api/invitations/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        invitation_token: token,
        otp_code: otpCode
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'OTP verification failed');
    }

    const data = await response.json();
    alert('OTP verified successfully!');
    return true;
  } catch (error) {
    alert(error.message);
    return false;
  }
}

// Step 3: Resend OTP if needed
async function resendOTP(token) {
  try {
    const response = await fetch(`http://localhost:8000/api/invitations/${token}/resend-otp`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to resend OTP');
    }

    const data = await response.json();
    alert(`OTP sent to ${data.phone}`);
    return data;
  } catch (error) {
    console.error('Error resending OTP:', error);
    alert('Failed to resend OTP');
  }
}

// Step 4: Join team after OTP verification (or directly if no OTP)
async function joinTeam(token, name, role) {
  try {
    const response = await fetch(`http://localhost:8000/api/invitations/${token}/join`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name,
        role: role
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to join team');
    }

    const data = await response.json();
    alert(`Successfully joined team! Welcome, ${data.name}!`);
    return data;
  } catch (error) {
    alert(error.message);
    return null;
  }
}

// Complete join flow
async function completeJoinFlow(token) {
  // 1. Get invitation details
  const invitation = await getInvitationDetails(token);
  if (!invitation) return;

  // 2. If OTP required, show OTP input form
  if (invitation.invitation.requires_otp) {
    const otpCode = prompt('Enter the OTP sent to your phone:');
    const verified = await verifyOTP(token, otpCode);
    
    if (!verified) {
      const retry = confirm('OTP verification failed. Resend OTP?');
      if (retry) {
        await resendOTP(token);
      }
      return;
    }
  }

  // 3. Get member details and join team
  const name = prompt('Enter your name:');
  const role = prompt('Enter your role (e.g., Developer, Designer):');
  
  await joinTeam(token, name, role);
}

// Usage when user visits /join/:token
// completeJoinFlow('abc123def456...');
'''

# Example 3: React Component for Join Team Page
'''
import React, { useState, useEffect } from 'react';

function JoinTeamPage({ token }) {
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [otpRequired, setOtpRequired] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [otp, setOtp] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInvitation();
  }, [token]);

  async function fetchInvitation() {
    try {
      const response = await fetch(`http://localhost:8000/api/invitations/${token}`);
      if (!response.ok) {
        const error = await response.json();
        setError(error.detail);
        setLoading(false);
        return;
      }
      const data = await response.json();
      setInvitation(data);
      setOtpRequired(data.invitation.requires_otp);
      setOtpVerified(!data.invitation.requires_otp);
      setLoading(false);
    } catch (err) {
      setError('Failed to load invitation');
      setLoading(false);
    }
  }

  async function handleVerifyOTP() {
    try {
      const response = await fetch('http://localhost:8000/api/invitations/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invitation_token: token,
          otp_code: otp
        })
      });

      if (!response.ok) {
        const error = await response.json();
        setError(error.detail);
        return;
      }

      setOtpVerified(true);
      setError('');
    } catch (err) {
      setError('Failed to verify OTP');
    }
  }

  async function handleResendOTP() {
    try {
      const response = await fetch(`http://localhost:8000/api/invitations/${token}/resend-otp`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to resend OTP');
      }

      alert('OTP sent successfully!');
    } catch (err) {
      setError('Failed to resend OTP');
    }
  }

  async function handleJoinTeam(e) {
    e.preventDefault();

    try {
      const response = await fetch(`http://localhost:8000/api/invitations/${token}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, role })
      });

      if (!response.ok) {
        const error = await response.json();
        setError(error.detail);
        return;
      }

      const data = await response.json();
      alert(`Successfully joined ${invitation.team.name}!`);
      // Redirect to team page or dashboard
    } catch (err) {
      setError('Failed to join team');
    }
  }

  if (loading) return <div>Loading...</div>;
  if (error && !invitation) return <div>Error: {error}</div>;

  return (
    <div className="join-team-page">
      <h1>Join {invitation.team.name}</h1>
      <p>Leader: {invitation.team.leader_name}</p>
      <p>{invitation.team.description}</p>

      {error && <div className="error">{error}</div>}

      {otpRequired && !otpVerified ? (
        <div className="otp-section">
          <h2>Verify Your Phone Number</h2>
          <p>Enter the OTP sent to {invitation.invitation.phone}</p>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="Enter 6-digit OTP"
            maxLength={6}
          />
          <button onClick={handleVerifyOTP}>Verify OTP</button>
          <button onClick={handleResendOTP}>Resend OTP</button>
        </div>
      ) : (
        <form onSubmit={handleJoinTeam}>
          <h2>Complete Your Registration</h2>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your Name"
            required
          />
          <input
            type="text"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Your Role (e.g., Developer)"
          />
          <button type="submit">Join Team</button>
        </form>
      )}
    </div>
  );
}

export default JoinTeamPage;
'''

# Example 4: Team Leader Dashboard - Create Invitation
'''
import React, { useState } from 'react';

function CreateInvitationForm({ teamId, onInvitationCreated }) {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [useOTP, setUseOTP] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inviteLink, setInviteLink] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/teams/${teamId}/invitations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          phone: useOTP ? phone : null
        })
      });

      if (!response.ok) {
        const error = await response.json();
        alert(error.detail);
        setLoading(false);
        return;
      }

      const data = await response.json();
      setInviteLink(data.invite_link);
      alert(`Invitation created! ${useOTP ? 'OTP sent to ' + phone : ''}`);
      
      if (onInvitationCreated) {
        onInvitationCreated(data);
      }
    } catch (err) {
      alert('Failed to create invitation');
    } finally {
      setLoading(false);
    }
  }

  function copyInviteLink() {
    navigator.clipboard.writeText(inviteLink);
    alert('Invitation link copied to clipboard!');
  }

  return (
    <div className="create-invitation-form">
      <h2>Invite Team Member</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Member's Email"
          required
        />

        <label>
          <input
            type="checkbox"
            checked={useOTP}
            onChange={(e) => setUseOTP(e.target.checked)}
          />
          Require phone verification (OTP)
        </label>

        {useOTP && (
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Phone (e.g., +919876543210)"
            required
          />
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Invitation'}
        </button>
      </form>

      {inviteLink && (
        <div className="invite-link-result">
          <h3>Invitation Created!</h3>
          <p>Share this link with the member:</p>
          <input type="text" value={inviteLink} readOnly />
          <button onClick={copyInviteLink}>Copy Link</button>
        </div>
      )}
    </div>
  );
}

export default CreateInvitationForm;
'''

print(__doc__)
print("\nAll code examples are shown as string literals above.")
print("Copy the relevant sections to your frontend application.")
