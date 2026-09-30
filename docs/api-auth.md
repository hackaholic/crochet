# API Contract: Authentication & Unified Customer Model

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/auth`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT / Codex  

---

## 1. Overview & Authentication Architecture

Conforming to **Sections 5, 8, 17, 18, and 28** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Indian Mobile First**: Phone number with 6-digit OTP verification is the primary login method for Indian e-commerce buyers.
* **Secondary Social Login**: Google OAuth ID token verification.
* **Unified User Model**: Accounts with matching phone numbers or emails automatically link under a single `User` record with multiple `UserIdentity` entries (`phone`, `google`), avoiding duplicate accounts.
* **Cookie-Based Sessions**: The backend issues an `HttpOnly`, `SameSite=Lax`, 30-day session cookie `session_token`. Frontend stores no auth secrets or tokens in `localStorage`.
  ```http
  Set-Cookie: session_token=<random_secure_token>; Max-Age=2592000; Path=/; HttpOnly; SameSite=Lax
  ```
* **Frontend Fetch Requirement**: Always specify `credentials: 'include'` in all fetch/axios calls to send and receive session cookies:
  ```typescript
  fetch('http://localhost:8000/api/v1/auth/me', {
    credentials: 'include',
  });
  ```
* **Automatic Guest Cart Merging**: When `verify-otp` or `google` authentication succeeds, any active anonymous guest cart (`guest_cart_token` cookie or payload) is automatically merged into the user's permanent cart seamlessly.
* **Development / Testing OTP**: In non-production testing, `send-otp` returns `"devOtp": "123456"` in the response payload for easy local testing without external SMS gateway integration.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/phone/send-otp` | Request a 6-digit OTP to mobile number. Enforces 60-second cooldown and 5-minute expiry. |
| `POST` | `/api/v1/auth/phone/verify-otp` | Verify OTP code (max 3 attempts). Creates or links user, auto-merges guest cart, sets `session_token` cookie. |
| `POST` | `/api/v1/auth/google` | Exchange Google OAuth ID token. Verifies email, links identity, auto-merges cart, sets `session_token` cookie. |
| `GET` | `/api/v1/auth/me` | Fetch active logged-in customer profile. Requires `credentials: 'include'`. Returns 401 if not authenticated. |
| `POST` | `/api/v1/auth/logout` | Revokes the active session token in DB and clears the `session_token` cookie. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface SendOtpRequest {
  /** 10-digit Indian phone number or E.164 string, e.g. "9876543210" or "+919876543210" */
  phone: string;
}

export interface SendOtpResponse {
  status: 'sent' | 'rate_limited' | 'error';
  message: string;
  cooldownSeconds: number;
  /** Populated in local/dev environments for convenience */
  devOtp?: string | null;
}

export interface VerifyOtpRequest {
  phone: string;
  otp: string;
  /** Optional explicit guest token fallback if cookies are restricted */
  guest_cart_token?: string | null;
}

export interface GoogleAuthRequest {
  id_token: string;
  guest_cart_token?: string | null;
}

export interface UserOut {
  id: number;
  phone?: string | null;
  email?: string | null;
  fullName?: string | null;
  isVerified: boolean;
  role: 'CUSTOMER' | 'ADMIN' | 'SUPPORT';
  createdAt: string;
  identities: string[];
}

export interface AuthResponse {
  user: UserOut;
  message: string;
}
```

---

## 4. Request / Response Examples

### 1. `POST /api/v1/auth/phone/send-otp`
**Request:**
```json
{
  "phone": "9876543210"
}
```
**Response (`200 OK`):**
```json
{
  "status": "sent",
  "message": "OTP sent successfully to +919876543210",
  "cooldownSeconds": 60,
  "devOtp": "123456"
}
```

### 2. `POST /api/v1/auth/phone/verify-otp`
**Request:**
```json
{
  "phone": "9876543210",
  "otp": "123456"
}
```
**Response (`200 OK` with `Set-Cookie: session_token=...`):**
```json
{
  "user": {
    "id": 1,
    "phone": "+919876543210",
    "email": null,
    "fullName": null,
    "isVerified": true,
    "role": "CUSTOMER",
    "createdAt": "2026-09-30T12:00:00Z",
    "identities": ["phone"]
  },
  "message": "Authentication successful"
}
```

### 3. `GET /api/v1/auth/me`
*Include `credentials: 'include'` with request.*
**Response (`200 OK`):**
```json
{
  "id": 1,
  "phone": "+919876543210",
  "email": "customer@example.com",
  "fullName": "Priya Sharma",
  "isVerified": true,
  "role": "CUSTOMER",
  "createdAt": "2026-09-30T12:00:00Z",
  "identities": ["phone", "google"]
}
```

If not logged in:
**Response (`401 Unauthorized`):**
```json
{
  "detail": "Not authenticated"
}
```

### 4. `POST /api/v1/auth/logout`
**Response (`200 OK` with cleared cookie):**
```json
{
  "message": "Successfully logged out"
}
```
