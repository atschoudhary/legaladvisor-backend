# API Reference

Complete API documentation with request/response examples.

## Base URLs

- **Development**: `http://localhost:8080/api/v1`
- **Production**: `https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1`

## Authentication

Protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Public Endpoints

### 1. Send Message

Send text, image, document, or audio for processing.

**Endpoint**: `POST /message`

**Content-Type**: `multipart/form-data`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| message | string | Yes* | Text message/query |
| image | file | No | Image file (JPG, PNG, etc.) |
| document | file | No | Document file (PDF, DOCX, TXT) |
| audio | file | No | Audio file (MP3, WAV, etc.) |

*Required unless audio is provided

**Request Example**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What are fundamental rights in Pakistan?" \
  -F "image=@photo.jpg"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "What are fundamental rights in Pakistan?",
  "response": "## Fundamental Rights in Pakistan\n\nFundamental rights in Pakistan are enshrined in **Part II (Articles 8-28)** of the Constitution...",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": true,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5,
    "auto_detected": true
  },
  "audio": "base64_encoded_audio_data..." // Only if TTS enabled
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Invalid file format"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Failed to process message: <error details>"
}
```

---

### 2. Audio Mode

Audio-only endpoint (audio in, audio out).

**Endpoint**: `POST /audio`

**Content-Type**: `multipart/form-data`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| audio | file | Yes | Audio file to transcribe and process |

**Request Example**:
```bash
curl -X POST http://localhost:8080/api/v1/audio \
  -F "audio=@question.mp3" \
  -o response.mp3
```

**Response**: Binary audio file (MP3)

**Headers**:
```
Content-Type: audio/mpeg
Content-Disposition: attachment; filename=response.mp3
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Invalid audio format"
}
```

---

### 3. Get Settings

Get current system settings.

**Endpoint**: `GET /settings`

**Request Example**:
```bash
curl http://localhost:8080/api/v1/settings
```

**Response** (200 OK):
```json
{
  "top_k": 5,
  "min_score": 0.5,
  "voice": "alloy",
  "tts_enabled": false,
  "note": "use_legal_search and province are auto-detected from query"
}
```

---

### 4. Update Settings

Update system settings (public endpoint for backward compatibility).

**Endpoint**: `POST /settings`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "top_k": 10,
  "min_score": 0.6,
  "voice": "nova",
  "tts_enabled": true
}
```

**Request Example**:
```bash
curl -X POST http://localhost:8080/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "top_k": 10,
    "voice": "nova",
    "tts_enabled": true
  }'
```

**Response** (200 OK):
```json
{
  "top_k": 10,
  "min_score": 0.6,
  "voice": "nova",
  "tts_enabled": true,
  "note": "use_legal_search and province are auto-detected from query"
}
```

---

### 5. Health Check

Check API health and available collections.

**Endpoint**: `GET /health`

**Request Example**:
```bash
curl http://localhost:8080/api/v1/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "collections_available": [
    "legaladvisor_sindh",
    "legaladvisor_punjab",
    "legaladvisor_khyber_pakhtunkhwa",
    "legaladvisor_balochistan",
    "legaladvisor_all_pakistan"
  ],
  "total_chunks": 15234
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "detail": "Service unavailable"
}
```

---

## Admin Endpoints (Protected)

### 1. Admin Login

Authenticate admin user and receive JWT token.

**Endpoint**: `POST /admin/login`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Request Example**:
```bash
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123"
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNTQxMjQwMH0.abc123...",
  "token_type": "bearer",
  "email": "admin@example.com"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect email or password"
}
```

---

### 2. Get Admin Settings

Get settings (requires authentication).

**Endpoint**: `GET /admin/settings`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Example**:
```bash
curl -X GET http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer eyJhbGci..."
```

**Response** (200 OK):
```json
{
  "top_k": 5,
  "min_score": 0.5,
  "voice": "alloy",
  "tts_enabled": false,
  "note": "use_legal_search and province are auto-detected from query"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Error Response** (401 Token Expired):
```json
{
  "detail": "Token has expired"
}
```

---

### 3. Update Admin Settings

Update settings (requires authentication).

**Endpoint**: `POST /admin/settings`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "top_k": 10,
  "min_score": 0.6,
  "voice": "nova",
  "tts_enabled": true
}
```

**Request Example**:
```bash
curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "top_k": 10,
    "voice": "nova",
    "tts_enabled": true
  }'
```

**Response** (200 OK):
```json
{
  "top_k": 10,
  "min_score": 0.6,
  "voice": "nova",
  "tts_enabled": true,
  "note": "use_legal_search and province are auto-detected from query"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Invalid voice. Must be one of: alloy, echo, fable, onyx, nova, shimmer"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Token has expired"
}
```

---

### 4. Verify Token

Verify if JWT token is valid.

**Endpoint**: `GET /admin/verify`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Example**:
```bash
curl -X GET http://localhost:8080/api/v1/admin/verify \
  -H "Authorization: Bearer eyJhbGci..."
```

**Response** (200 OK):
```json
{
  "email": "admin@example.com",
  "valid": true
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Data Models

### Message Response
```typescript
{
  success: boolean;
  message: string;
  response: string;  // Markdown formatted
  language: string;  // "english" | "urdu" | "punjabi" | "sindhi" | "roman_urdu"
  context: {
    had_audio: boolean;
    had_image: boolean;
    had_document: boolean;
    used_legal_search: boolean;
    legal_results_count: number;
    auto_detected: boolean;
  };
  audio?: string;  // Base64 encoded MP3 (if TTS enabled)
}
```

### Settings
```typescript
{
  top_k: number;        // 1-20
  min_score: number;    // 0.0-1.0
  voice: string;        // "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer"
  tts_enabled: boolean;
  note?: string;
}
```

### Login Response
```typescript
{
  access_token: string;
  token_type: string;  // "bearer"
  email: string;
}
```

### Health Response
```typescript
{
  status: string;
  version: string;
  collections_available: string[];
  total_chunks: number;
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or expired token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Endpoint doesn't exist |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing in production.

---

## CORS

CORS is enabled for all origins (`*`). Configure appropriately for production.

---

## File Upload Limits

- **Max file size**: 25MB
- **Supported image formats**: JPG, JPEG, PNG, GIF, WebP
- **Supported document formats**: PDF, DOCX, TXT
- **Supported audio formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM

---

## Best Practices

1. **Always handle errors**: Check response status codes
2. **Store tokens securely**: Use secure storage (not localStorage for sensitive apps)
3. **Refresh tokens**: Implement token refresh before expiration
4. **Validate inputs**: Validate file types and sizes before upload
5. **Use HTTPS**: Always use HTTPS in production
6. **Handle timeouts**: Set appropriate timeout values
7. **Retry logic**: Implement exponential backoff for retries

---

## Examples by Use Case

### Legal Query
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What is the legal age for marriage in Pakistan?"
```

### Document Analysis
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Summarize this contract" \
  -F "document=@contract.pdf"
```

### Image Analysis
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Extract text from this image" \
  -F "image=@document_photo.jpg"
```

### Voice Query
```bash
curl -X POST http://localhost:8080/api/v1/audio \
  -F "audio=@question.mp3" \
  -o response.mp3
```

### Admin Workflow
```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass123"}' \
  | jq -r '.access_token')

# 2. Get settings
curl -X GET http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN"

# 3. Update settings
curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"top_k": 10, "tts_enabled": true}'
```
