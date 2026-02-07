# Hackathon Team Management API v2.0

A comprehensive FastAPI-based backend service for managing hackathon teams with an advanced invitation system. Team leaders can create teams, generate invite links, send OTP verification to members, and manage their teams effectively.

## 🆕 What's New in v2.0

- ✅ **Invitation System**: Generate unique invite links for team members
- ✅ **OTP Verification**: Send SMS OTP to verify members' phone numbers
- ✅ **Secure Token Generation**: Cryptographically secure invitation tokens
- ✅ **Expiration Management**: Automatic expiration for invitations and OTPs
- ✅ **Phone Number Validation**: E.164 format validation and formatting
- ✅ **Mock SMS Service**: Built-in mock SMS for development/testing

## Features

### Team Management
- ✅ Create and manage hackathon teams
- ✅ Team leader registration with unique email validation
- ✅ Add/remove team members
- ✅ Configure maximum team size
- ✅ Full CRUD operations for teams

### Invitation System
- ✅ Generate unique invitation links with tokens
- ✅ Send invitations via email (stored in database)
- ✅ Optional phone number for OTP verification
- ✅ Automatic invitation expiration (48 hours default)
- ✅ Track invitation status (pending/used/expired)
- ✅ Resend OTP functionality

### OTP Verification
- ✅ Generate 6-digit OTP codes
- ✅ Send OTP via SMS (Twilio integration or mock service)
- ✅ OTP expiration (10 minutes default)
- ✅ Verify OTP before joining team
- ✅ Prevent duplicate OTP usage

### API Features
- ✅ RESTful API with automatic OpenAPI documentation
- ✅ SQLAlchemy ORM with support for SQLite, PostgreSQL, and MySQL
- ✅ Pydantic validation for request/response data
- ✅ CORS support for frontend integration
- ✅ Comprehensive error handling

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation
- **Twilio** (Optional): SMS service for OTP delivery

## Project Structure

```
.
├── main.py                      # FastAPI application and routes
├── models.py                    # SQLAlchemy database models
├── schemas.py                   # Pydantic schemas for validation
├── database.py                  # Database configuration
├── utils.py                     # Utility functions (token, OTP generation)
├── sms_service.py              # SMS service (Twilio/Mock)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── test_invitation_api.py      # Comprehensive test suite
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- (Optional) Twilio account for real SMS

### Setup

1. Clone the repository or copy the files to your project directory

2. Create a virtual environment:
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
# Database
DATABASE_URL=sqlite:///./hackathon.db

# Frontend URL for invitation links
BASE_URL=http://localhost:3000

# SMS Configuration
USE_MOCK_SMS=true  # Set to false for real SMS

# Twilio credentials (if using real SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

Or use the startup scripts:
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Teams

#### Create a Team
```http
POST /api/teams/
Content-Type: application/json

{
  "name": "Team Awesome",
  "leader_name": "John Doe",
  "leader_email": "john@example.com",
  "description": "Building an AI-powered solution",
  "max_members": 5
}
```

#### Get All Teams
```http
GET /api/teams/
```

#### Get Team by ID
```http
GET /api/teams/{team_id}
```

#### Update Team
```http
PUT /api/teams/{team_id}
Content-Type: application/json

{
  "description": "Updated description",
  "max_members": 6
}
```

#### Delete Team
```http
DELETE /api/teams/{team_id}
```

### Invitations

#### Create Invitation (with OTP)
```http
POST /api/teams/{team_id}/invitations/
Content-Type: application/json

{
  "email": "member@example.com",
  "phone": "+919876543210"
}

Response:
{
  "id": 1,
  "team_id": 1,
  "email": "member@example.com",
  "phone": "+919876543210",
  "token": "abc123def456...",
  "invite_link": "http://localhost:3000/join/abc123def456...",
  "is_used": false,
  "expires_at": "2024-02-09T10:30:00",
  "created_at": "2024-02-07T10:30:00"
}
```

#### Create Invitation (without OTP)
```http
POST /api/teams/{team_id}/invitations/
Content-Type: application/json

{
  "email": "member@example.com"
}
```

#### Get Team Invitations
```http
GET /api/teams/{team_id}/invitations/
```

#### Get Invitation Details
```http
GET /api/invitations/{token}

Response:
{
  "invitation": {
    "email": "member@example.com",
    "phone": "+919876543210",
    "expires_at": "2024-02-09T10:30:00",
    "requires_otp": true
  },
  "team": {
    "id": 1,
    "name": "Team Awesome",
    "leader_name": "John Doe",
    "description": "Building an AI-powered solution"
  }
}
```

### OTP Management

#### Verify OTP
```http
POST /api/invitations/verify-otp
Content-Type: application/json

{
  "invitation_token": "abc123def456...",
  "otp_code": "123456"
}

Response:
{
  "message": "OTP verified successfully",
  "verified": true
}
```

#### Resend OTP
```http
POST /api/invitations/{token}/resend-otp

Response:
{
  "message": "OTP sent successfully",
  "phone": "+919876543210",
  "expires_at": "2024-02-07T10:40:00"
}
```

#### Join Team via Invitation
```http
POST /api/invitations/{token}/join
Content-Type: application/json

{
  "name": "Jane Smith",
  "role": "Frontend Developer"
}

Response:
{
  "id": 1,
  "team_id": 1,
  "name": "Jane Smith",
  "email": "member@example.com",
  "phone": "+919876543210",
  "role": "Frontend Developer",
  "created_at": "2024-02-07T10:30:00"
}
```

### Team Members (Direct Add - Legacy)

#### Add Member Directly
```http
POST /api/teams/{team_id}/members/
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+919123456789",
  "role": "Frontend Developer"
}
```

#### Get Team Members
```http
GET /api/teams/{team_id}/members/
```

#### Remove Team Member
```http
DELETE /api/teams/{team_id}/members/{member_id}
```

## Database Schema

### Teams Table
- `id`: Primary key
- `name`: Unique team name
- `leader_name`: Team leader's name
- `leader_email`: Team leader's email (unique)
- `description`: Team description
- `max_members`: Maximum team size (default: 5)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Members Table
- `id`: Primary key
- `team_id`: Foreign key to teams table
- `name`: Member name
- `email`: Member email
- `phone`: Member phone number (E.164 format)
- `role`: Member role (e.g., Developer, Designer)
- `created_at`: Timestamp of creation

### Invitations Table
- `id`: Primary key
- `team_id`: Foreign key to teams table
- `email`: Invitee email
- `phone`: Invitee phone (optional)
- `token`: Unique invitation token
- `is_used`: Boolean flag
- `expires_at`: Expiration timestamp
- `created_at`: Timestamp of creation

### OTPs Table
- `id`: Primary key
- `phone`: Phone number
- `otp_code`: 6-digit OTP
- `invitation_token`: Associated invitation token
- `is_verified`: Boolean flag
- `expires_at`: Expiration timestamp
- `created_at`: Timestamp of creation

## Invitation Flow

### With OTP Verification

1. **Team Leader Creates Invitation**
   ```
   POST /api/teams/1/invitations/
   { "email": "user@example.com", "phone": "+919876543210" }
   ```
   - System generates unique token
   - OTP is generated and sent to phone via SMS
   - Returns invitation link

2. **Member Receives Invitation**
   - Clicks invitation link: `http://localhost:3000/join/{token}`
   - Frontend calls: `GET /api/invitations/{token}` to get details

3. **Member Verifies OTP**
   ```
   POST /api/invitations/verify-otp
   { "invitation_token": "...", "otp_code": "123456" }
   ```

4. **Member Joins Team**
   ```
   POST /api/invitations/{token}/join
   { "name": "John Doe", "role": "Developer" }
   ```
   - System validates OTP was verified
   - Adds member to team
   - Marks invitation as used

### Without OTP Verification

1. **Team Leader Creates Invitation**
   ```
   POST /api/teams/1/invitations/
   { "email": "user@example.com" }
   ```

2. **Member Joins Directly**
   ```
   POST /api/invitations/{token}/join
   { "name": "John Doe", "role": "Developer" }
   ```

## SMS Configuration

### Development/Testing (Mock SMS)

Set in `.env`:
```env
USE_MOCK_SMS=true
```

OTPs will be printed to console instead of sending real SMS.

### Production (Twilio)

1. Create a Twilio account at https://www.twilio.com
2. Get your Account SID, Auth Token, and Phone Number
3. Install Twilio SDK:
   ```bash
   pip install twilio
   ```
4. Update `.env`:
   ```env
   USE_MOCK_SMS=false
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## Testing

### Run Test Suite

```bash
python test_invitation_api.py
```

The test suite includes:
- Team creation
- Invitation generation (with and without phone)
- OTP sending and verification
- Team joining via invitation
- Error case handling
- Duplicate prevention

### Manual Testing with cURL

#### Create Invitation
```bash
curl -X POST "http://localhost:8000/api/teams/1/invitations/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newmember@example.com",
    "phone": "+919876543210"
  }'
```

#### Verify OTP
```bash
curl -X POST "http://localhost:8000/api/invitations/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "invitation_token": "your_token_here",
    "otp_code": "123456"
  }'
```

#### Join Team
```bash
curl -X POST "http://localhost:8000/api/invitations/{token}/join" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Member",
    "role": "Developer"
  }'
```

## Validation Rules

### Team Management
1. **Team Names**: Must be unique across all teams
2. **Leader Email**: Must be unique (one team per leader)
3. **Team Size**: Maximum members configurable (1-20)

### Invitations
1. **Email**: Valid email format required
2. **Phone**: E.164 format (e.g., +919876543210)
3. **Token**: 32-character secure random string
4. **Expiration**: 48 hours for invitations, 10 minutes for OTP
5. **Usage**: Single-use only (marked as used after joining)

### OTP
1. **Code**: 6-digit numeric code
2. **Expiration**: 10 minutes
3. **Verification**: Required before joining if phone provided
4. **Resend**: Invalidates previous OTP

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error or business logic violation
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Error Scenarios

#### Team Full
```json
{
  "detail": "Team is full (max 5 members)"
}
```

#### Invitation Expired
```json
{
  "detail": "This invitation has expired"
}
```

#### OTP Required
```json
{
  "detail": "OTP verification required. Please verify your phone number first."
}
```

#### Invalid OTP
```json
{
  "detail": "Invalid OTP code"
}
```

## Security Considerations

1. **Token Generation**: Uses cryptographically secure random tokens
2. **OTP Generation**: Random 6-digit codes with expiration
3. **Phone Validation**: E.164 format validation
4. **Expiration**: Automatic expiration for invitations and OTPs
5. **Single Use**: Invitations and OTPs are single-use only
6. **CORS**: Configure allowed origins in production

## Production Deployment

### Checklist

1. ✅ Use production database (PostgreSQL/MySQL)
2. ✅ Set `USE_MOCK_SMS=false` and configure Twilio
3. ✅ Set `BASE_URL` to your frontend URL
4. ✅ Configure CORS origins in `main.py`
5. ✅ Use environment variables for sensitive data
6. ✅ Enable HTTPS
7. ✅ Implement rate limiting
8. ✅ Add authentication/authorization
9. ✅ Set up logging and monitoring
10. ✅ Use a reverse proxy (Nginx/Apache)

### Production Server

```bash
# Install production dependencies
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Future Enhancements

- [ ] Email service for invitation notifications
- [ ] JWT-based authentication
- [ ] Team leader verification before invitation
- [ ] Invitation link customization
- [ ] Batch invitation creation
- [ ] Team chat or messaging
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Multi-language SMS support
- [ ] Alternative authentication methods (WhatsApp OTP)

## Troubleshooting

### SMS Not Sending

**Mock Mode**: Check console output for OTP
**Twilio Mode**: Verify credentials and phone number format

### Database Errors

**SQLite**: Check file permissions
**PostgreSQL/MySQL**: Verify connection string and credentials

### Invitation Not Working

1. Check invitation hasn't expired
2. Verify OTP was verified (if phone provided)
3. Check team isn't full
4. Ensure invitation hasn't been used

## API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License

## Support

For issues or questions, please check:
1. Server logs for error details
2. API documentation at `/docs`
3. Test suite output for examples

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
