# Account Creation & Authentication System

## Overview

LaunchLens has **two authentication flows**:

1. **Anonymous Mode** - Use app without account (can't save results)
2. **Authenticated Mode** - Create account & save research to database

```
┌─────────────────────────────────────┐
│       User Visits App                │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────────┐  ┌──────────────┐
│ Explore     │  │ Create/Login │
│ Anonymous   │  │ Account      │
└─────────────┘  └──────────────┘
     │                 │
     ▼                 ▼
   Can't          Can save
   save           results
```

---

## Two Authentication Entry Points

### 1. Full Auth Page (`/auth`)
**URL**: `http://localhost:8085/auth` (or 8084)

Dedicated page for login/signup:
- Email + password form
- Toggle between "Sign up" and "Sign in"
- Redirects to `/research` after success

```
┌──────────────────────────────────┐
│         Create account           │
├──────────────────────────────────┤
│                                  │
│  Email: [you@example.com      ] │
│  Password: [••••••••••••••••••] │
│                                  │
│      [Create account] Button     │
│                                  │
│  Already have account? Sign in   │
│                                  │
└──────────────────────────────────┘
```

### 2. In-App Modal (SaveAuthModal)
**When**: User tries to save results without account

Flow:
```
User clicks "Save Results"
        │
        ▼
Are you logged in?
        │
    No ▼
   ┌─────────────────────┐
   │ SaveAuthModal pops  │
   │ up inline           │
   │ ┌─────────────────┐ │
   │ │ Create account  │ │
   │ │ to save your    │ │
   │ │ research...     │ │
   │ │                 │ │
   │ │ Email: [...] │ │
   │ │ Password:[..] │ │
   │ │                 │ │
   │ │ [Save Results] │ │
   │ └─────────────────┘ │
   └─────────────────────┘
        │
        ▼ (After creating account)
   Save to database
   & redirect to dashboard
```

---

## How Account Creation Works

### Step 1: User Submits Signup Form
```
Email: alice@example.com
Password: SecurePassword123
```

### Step 2: Frontend Calls Supabase Auth API
```javascript
// From Auth.tsx or SaveAuthModal.tsx
const endpoint = `${SUPABASE_URL}/auth/v1/signup`;

const response = await fetch(endpoint, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'apikey': SUPABASE_ANON_KEY,  // Public key
  },
  body: JSON.stringify({
    email: 'alice@example.com',
    password: 'SecurePassword123',
    gotrue_meta_security: {}
  })
});
```

### Step 3: Supabase Creates User
**Database**: PostgreSQL (Supabase managed)
**Table**: `auth.users`

```sql
INSERT INTO auth.users (
  id,              -- UUID
  email,           -- alice@example.com
  password_hash,   -- Hashed with bcrypt
  created_at,      -- 2026-03-21
  updated_at,
  last_sign_in_at
) VALUES (...)
```

### Step 4: Supabase Returns JWT Token
```json
{
  "session": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "..."
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com"
  }
}
```

### Step 5: Frontend Stores JWT
```javascript
// Save token to localStorage
localStorage.setItem('auth_token', access_token);
localStorage.setItem('user_email', email);

// Redirect to /research
navigate('/research');
```

### Step 6: Token Sent with Every API Request
```javascript
// In use-research.ts hook
const token = localStorage.getItem('auth_token');

const response = await fetch('/api/save-idea', {
  headers: {
    'Authorization': `Bearer ${token}`,  // ← Token here!
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
});
```

### Step 7: Backend Validates JWT
```python
# From app/core/auth.py
async def get_current_user(credentials):
    token = credentials.credentials

    payload = jwt.decode(
        token,
        settings.SUPABASE_ANON_KEY,
        algorithms=["HS256"]
    )

    user_id = payload.get("sub")  # User ID from token
    email = payload.get("email")

    return {"id": user_id, "email": email}
```

### Step 8: Save Idea to Database
```python
# Backend receives authenticated request
POST /api/ideas
Authorization: Bearer {jwt_token}

{
  "title": "AI Video Editor",
  "decomposition": {...},
  "insights": {...}
}

# Backend inserts into ideas table:
INSERT INTO ideas (
  user_id,              -- From JWT
  title,
  decomposition,        -- JSON
  created_at
) VALUES (...)
```

---

## Data Flow Diagram

```
┌─────────────────────────────┐
│   User Signs Up             │
│  email: alice@example.com   │
│  pass: SecurePassword123    │
└────────────┬────────────────┘
             │ POST /auth/v1/signup
             ▼
┌─────────────────────────────┐
│  Supabase Auth              │
│  ✓ Hash password (bcrypt)   │
│  ✓ Create user record       │
│  ✓ Generate JWT             │
└────────────┬────────────────┘
             │ Return access_token
             ▼
┌─────────────────────────────┐
│  Frontend localStorage      │
│  - auth_token (JWT)         │
│  - user_email               │
└────────────┬────────────────┘
             │
    ┌────────┴──────────┐
    │ User navigates to │
    │ /research         │
    └────────┬──────────┘
             │
             ▼
┌─────────────────────────────┐
│  User analyzes ideas        │
│  (as authenticated user)    │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  User clicks "Save Results" │
└────────────┬────────────────┘
             │ POST /api/ideas
             │ Authorization: Bearer {token}
             ▼
┌─────────────────────────────┐
│  Backend Auth Middleware    │
│  ✓ Decode JWT               │
│  ✓ Extract user_id          │
│  ✓ Verify expiration        │
└────────────┬────────────────┘
             │ ✓ Valid
             ▼
┌─────────────────────────────┐
│  Database                   │
│  INSERT INTO ideas (        │
│    user_id,                 │
│    title,                   │
│    decomposition,           │
│    created_at               │
│  )                          │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  ✓ Idea saved to user       │
│  ✓ User can view in history │
└─────────────────────────────┘
```

---

## What Gets Saved to Database?

### ideas Table
```sql
CREATE TABLE ideas (
  id UUID PRIMARY KEY,
  user_id UUID (from JWT),
  title TEXT,
  decomposition JSONB,          -- Full decomposition output
  insights JSONB,               -- Discovered insights
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Example Saved Idea
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440123",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "AI Video Editor",
  "decomposition": {
    "business_type": "AI video editing software (SaaS)",
    "location": {"city": "SF", "state": "CA"},
    "target_customers": ["Content creators", "Small agencies"],
    "price_tier": "premium ($49-$99/month)",
    ...
  },
  "insights": {
    "insights": [
      {
        "type": "pain_point",
        "title": "Video editing takes too long",
        "evidence": [...],
        ...
      }
    ]
  },
  "created_at": "2026-03-21T10:30:00Z"
}
```

---

## Authentication Flow Comparison

| Scenario | Flow | Can Save | Database |
|----------|------|----------|----------|
| **Anonymous** | Browse app | ❌ No | No entry |
| **Sign up** | Email + password → Supabase → JWT → localStorage | ✅ Yes | ✓ Creates user |
| **Sign in** | Email + password → Supabase → JWT → localStorage | ✅ Yes | ✓ Existing user |
| **Save idea** | Click "Save" → Token sent → Backend validates → Database insert | ✅ Yes | ✓ Linked to user_id |

---

## Frontend Components

### 1. Full Auth Page
**File**: `frontend/src/pages/Auth.tsx`
- Email input
- Password input
- Signup/Login toggle
- Error handling
- Success toast

### 2. Save Modal
**File**: `frontend/src/components/validate/SaveAuthModal.tsx`
- Inline modal popup
- Same auth form
- Appears when saving without token
- Auto-saves after successful auth

### 3. Navigation Auth Logic
**File**: `frontend/src/components/layout/Nav.tsx`
- Shows login/logout button
- Checks localStorage for token
- Calls logout handler

---

## Backend Authentication

### 1. Auth Middleware
**File**: `backend/app/core/auth.py`

Three dependency levels:
```python
# Optional - returns None if no token
@Depends(optional_user)
async def my_endpoint(user: dict | None):
    if user:
        # Has token
    else:
        # Anonymous

# Required - raises 401 if no token
@Depends(require_user)
async def my_endpoint(user: dict):
    # user_id = user['id']
    # user_email = user['email']

# Development bypass
if ENVIRONMENT == 'development' and no token:
    return dev_user  # For testing without signup
```

### 2. Using Auth in Endpoints
```python
# Save idea (requires auth)
@router.post("/api/ideas")
async def save_idea(
    idea: IdeaRequest,
    user: dict = Depends(require_user)
):
    # Insert with user['id']
    new_idea = {
        'user_id': user['id'],
        'title': idea.title,
        'decomposition': idea.decomposition,
        'created_at': datetime.now()
    }
    supabase.table('ideas').insert(new_idea).execute()
    return new_idea

# Get ideas (requires auth)
@router.get("/api/ideas")
async def get_ideas(user: dict = Depends(require_user)):
    results = supabase.table('ideas').select('*').eq('user_id', user['id']).execute()
    return results.data
```

---

## Security Features

### 1. Password Hashing
- Supabase uses **bcrypt** (industry standard)
- Passwords never sent in plain text over network
- HTTPS encryption (production)

### 2. JWT Token Validation
```python
# Token contains:
{
  "sub": "user-id-uuid",        # User ID
  "email": "alice@example.com",
  "exp": 1711000000,             # Expiration time
  "iat": 1710996400              # Issued at
}

# Verified with:
jwt.decode(token, secret_key, algorithms=['HS256'])
```

### 3. Token Storage
- Stored in **localStorage** (accessible from JS)
- Not stored in cookies (avoids CSRF)
- Deleted on logout

### 4. Development Bypass
```python
# Only in development environment
if ENVIRONMENT == 'development' and no token:
    return fake_user  # For local testing

# Production: Always requires token
```

---

## Error Handling

### Signup Errors
```
Email already exists
↓
Weak password
↓
Network error
↓
Server error
```

All show toast notifications to user:
```javascript
toast({
  title: 'Error',
  description: 'Email already exists. Try signing in instead.',
  variant: 'destructive'
})
```

### Token Errors
```
Token expired
↓
Invalid signature
↓
Missing token
```

Triggers logout and redirect to auth page:
```javascript
localStorage.removeItem('auth_token');
navigate('/auth');
```

---

## Current Status

✅ **Implemented**:
- Full signup/login page
- Save modal for in-app signup
- JWT token validation
- Database persistence
- Logout functionality

⚠️ **Not Yet**:
- Email verification
- Password reset
- Social auth (Google, GitHub)
- Rate limiting on signup
- Email confirmation before save

---

## Testing Account Creation

### Test Locally (Dev Mode)
```
Frontend: http://localhost:8085/auth
Backend: http://localhost:8001

1. Click "Create account"
2. Enter: alice@example.com / Password123
3. Should redirect to /research
4. localStorage should have auth_token
5. Click "Save Results" → Saves to database
```

### Test Signup Modal
```
1. Analyze an idea
2. Click "Save Results" (without login)
3. Modal pops up
4. Create account in modal
5. Idea auto-saves to database
```

---

## Environment Variables

**Frontend** (`.env.local`):
```
VITE_SUPABASE_URL=https://umteiflvqqpnnohiwfvc.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

**Backend** (`.env`):
```
SUPABASE_URL=https://umteiflvqqpnnohiwfvc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...
```

---

## Summary

**Account Creation is**:
- ✅ Two-entry point (full page + modal)
- ✅ JWT-based authentication
- ✅ Supabase-managed (no custom auth server)
- ✅ Secure (bcrypt hashing, JWT validation)
- ✅ Optional (can browse anonymously)
- ✅ Linked to database (user_id indexed)

**When user saves results**:
1. Frontend sends JWT token
2. Backend validates it
3. Extracts user_id from token
4. Inserts idea into `ideas` table with user_id
5. User can return later and view their saved research

