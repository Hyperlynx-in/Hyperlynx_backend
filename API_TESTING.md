# API Testing Examples

This document contains curl examples for testing the Hyperlynx Backend API.

## Starting the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 1. Health Check

```bash
curl -X GET http://localhost:8000/api/health/
```

Expected Response:
```json
{
  "status": "success",
  "message": "Hyperlynx API is running",
  "code": 200
}
```

## 2. User Registration

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Expected Response (201 Created):
```json
{
  "message": "User registered successfully"
}
```

## 3. Login (Get JWT Tokens)

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Expected Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Save the `access` token - you'll need it for authenticated requests.

## 4. Get User Profile

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected Response (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "date_joined": "2024-01-30T10:30:00Z"
}
```

## 5. Update User Profile

```bash
curl -X PUT http://localhost:8000/api/users/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name",
    "email": "newemail@example.com"
  }'
```

Expected Response (200 OK):
```json
{
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "newemail@example.com",
    "first_name": "Updated",
    "last_name": "Name",
    "date_joined": "2024-01-30T10:30:00Z"
  }
}
```

## 6. Refresh Access Token

When your access token expires, use the refresh token to get a new access token:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

Expected Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Testing with Postman

1. **Import Collection**: Create a new collection called "Hyperlynx API"

2. **Health Check Request**
   - Method: GET
   - URL: `http://localhost:8000/api/health/`

3. **Register Request**
   - Method: POST
   - URL: `http://localhost:8000/api/users/register/`
   - Body (JSON):
   ```json
   {
     "username": "testuser",
     "email": "testuser@example.com",
     "password": "SecurePassword123!",
     "password2": "SecurePassword123!",
     "first_name": "Test",
     "last_name": "User"
   }
   ```

4. **Login Request**
   - Method: POST
   - URL: `http://localhost:8000/api/token/`
   - Body (JSON):
   ```json
   {
     "username": "testuser",
     "password": "SecurePassword123!"
   }
   ```
   - In the response, copy the `access` token

5. **Get Profile Request**
   - Method: GET
   - URL: `http://localhost:8000/api/users/profile/`
   - Headers:
     - Key: `Authorization`
     - Value: `Bearer {YOUR_ACCESS_TOKEN}`

## Testing with Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Register
register_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
}
response = requests.post(f"{BASE_URL}/api/users/register/", json=register_data)
print("Register:", response.status_code, response.json())

# 2. Login
login_data = {
    "username": "testuser",
    "password": "SecurePassword123!"
}
response = requests.post(f"{BASE_URL}/api/token/", json=login_data)
print("Login:", response.status_code, response.json())
tokens = response.json()
access_token = tokens['access']

# 3. Get Profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/api/users/profile/", headers=headers)
print("Profile:", response.status_code, response.json())

# 4. Update Profile
update_data = {
    "first_name": "Updated",
    "last_name": "Name"
}
response = requests.put(f"{BASE_URL}/api/users/profile/", json=update_data, headers=headers)
print("Update:", response.status_code, response.json())

# 5. Refresh Token
refresh_data = {"refresh": tokens['refresh']}
response = requests.post(f"{BASE_URL}/api/token/refresh/", json=refresh_data)
print("Refresh:", response.status_code, response.json())
```

## Testing with JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";

// 1. Register
async function register() {
  const response = await fetch(`${BASE_URL}/api/users/register/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: "testuser",
      email: "testuser@example.com",
      password: "SecurePassword123!",
      password2: "SecurePassword123!",
      first_name: "Test",
      last_name: "User"
    })
  });
  const data = await response.json();
  console.log("Register:", data);
}

// 2. Login
async function login() {
  const response = await fetch(`${BASE_URL}/api/token/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: "testuser",
      password: "SecurePassword123!"
    })
  });
  const data = await response.json();
  console.log("Login:", data);
  return data.access;
}

// 3. Get Profile
async function getProfile(accessToken) {
  const response = await fetch(`${BASE_URL}/api/users/profile/`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
    }
  });
  const data = await response.json();
  console.log("Profile:", data);
}

// Usage
(async () => {
  await register();
  const token = await login();
  await getProfile(token);
})();
```

## Common Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid data provided
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User doesn't have permission
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Error Response Examples

```json
{
  "username": ["This field is required."],
  "email": ["Enter a valid email address."],
  "password": ["This password is too common."]
}
```

## Tips

1. Always include the `Authorization` header with `Bearer {token}` for authenticated endpoints
2. Keep your refresh token secure and never expose it
3. Use HTTPS in production
4. Set appropriate `CORS_ALLOWED_ORIGINS` for your frontend
5. Monitor token expiration and refresh proactively
6. Use short-lived access tokens and longer-lived refresh tokens for security

