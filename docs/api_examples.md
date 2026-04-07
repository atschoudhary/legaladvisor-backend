# API Request & Response Examples

Complete collection of API request and response examples for all endpoints.

## Table of Contents

1. [Public Endpoints](#public-endpoints)
   - [Send Message](#1-send-message)
   - [Audio Mode](#2-audio-mode)
   - [Get Settings](#3-get-settings)
   - [Update Settings](#4-update-settings)
   - [Health Check](#5-health-check)
2. [Admin Endpoints](#admin-endpoints)
   - [Admin Login](#1-admin-login)
   - [Get Admin Settings](#2-get-admin-settings)
   - [Update Admin Settings](#3-update-admin-settings)
   - [Verify Token](#4-verify-token)

---

## Public Endpoints

### 1. Send Message

**Endpoint**: `POST /api/v1/message`

#### Example 1: Simple Text Query

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What are fundamental rights in Pakistan?"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "What are fundamental rights in Pakistan?",
  "response": "## Fundamental Rights in Pakistan\n\nFundamental rights in Pakistan are enshrined in **Part II (Articles 8-28)** of the Constitution of Pakistan 1973. These rights are guaranteed to all citizens and include:\n\n### Key Fundamental Rights:\n\n1. **Right to Life (Article 9)**\n   - Protection of life and liberty\n   - No person shall be deprived of life or liberty except in accordance with law\n\n2. **Freedom of Speech (Article 19)**\n   - Freedom of speech and expression\n   - Freedom of press\n   - Subject to reasonable restrictions\n\n3. **Freedom of Religion (Article 20)**\n   - Freedom to profess, practice and propagate religion\n   - Protection of religious institutions\n\n4. **Right to Property (Article 23)**\n   - Protection against acquisition of property without compensation\n\n5. **Equality Before Law (Article 25)**\n   - All citizens are equal before law\n   - No discrimination on basis of sex, religion, caste, or place of birth\n\n6. **Right to Education (Article 25-A)**\n   - Free and compulsory education for children aged 5-16\n\n### Enforcement:\n- These rights can be enforced through courts\n- High Courts and Supreme Court can issue writs for enforcement\n- Any law inconsistent with fundamental rights is void\n\n### Limitations:\n- Rights are subject to reasonable restrictions\n- Can be suspended during emergency\n- Must be exercised within the law",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5,
    "auto_detected": true
  }
}
```

---

#### Example 2: Text Query with Image

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What does this document say?" \
  -F "image=@contract_photo.jpg"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "What does this document say?",
  "response": "Based on the image analysis, this appears to be a rental agreement contract. Here's what I can see:\n\n## Document Summary:\n\n**Type**: Rental/Lease Agreement\n\n**Key Details Visible**:\n- Agreement between landlord and tenant\n- Property address: [Address from image]\n- Monthly rent: Rs. [Amount]\n- Duration: [Period]\n- Security deposit: Rs. [Amount]\n\n**Important Clauses**:\n1. Rent payment terms\n2. Maintenance responsibilities\n3. Termination conditions\n4. Security deposit refund terms\n\n**Legal Validity**:\n- This appears to be a standard rental agreement\n- Should be on stamp paper for legal validity\n- Both parties should sign\n- Consider registering with local authorities\n\n**Recommendations**:\n- Ensure all terms are clearly understood\n- Verify stamp paper value as per provincial law\n- Keep copies of all documents\n- Document property condition at move-in\n\nWould you like me to explain any specific clause in detail?",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": true,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 4,
    "auto_detected": true
  }
}
```

---

#### Example 3: Document Upload

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Summarize this legal document" \
  -F "document=@contract.pdf"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Summarize this legal document",
  "response": "## Document Summary\n\n**Document Type**: Employment Contract\n\n**Parties Involved**:\n- Employer: ABC Corporation (Pvt) Ltd\n- Employee: [Name]\n\n**Key Terms**:\n\n### 1. Position & Duties\n- Position: Senior Software Engineer\n- Department: Technology\n- Reporting to: CTO\n- Start date: January 1, 2026\n\n### 2. Compensation\n- Base salary: Rs. 150,000/month\n- Annual bonus: Performance-based\n- Benefits: Health insurance, provident fund\n\n### 3. Working Hours\n- 9 AM to 6 PM, Monday to Friday\n- 1 hour lunch break\n- Overtime as per company policy\n\n### 4. Leave Entitlement\n- Annual leave: 20 days\n- Sick leave: 15 days\n- Casual leave: 10 days\n\n### 5. Termination\n- Notice period: 2 months\n- Termination with cause: Immediate\n- Severance: As per labor law\n\n### 6. Confidentiality\n- Non-disclosure agreement included\n- Intellectual property belongs to company\n- Non-compete clause: 6 months\n\n### Legal Compliance:\n- Complies with Pakistan labor laws\n- Follows minimum wage requirements\n- Includes mandatory benefits\n\n**Recommendations**:\n- Review termination clauses carefully\n- Understand non-compete restrictions\n- Clarify bonus calculation method\n- Verify provident fund contribution rates",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": true,
    "used_legal_search": true,
    "legal_results_count": 6,
    "auto_detected": true
  }
}
```

---

#### Example 4: Audio Input

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=" \
  -F "audio=@question.mp3"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "What is the legal age for marriage in Pakistan?",
  "response": "## Legal Age for Marriage in Pakistan\n\n### Current Law:\n\n**For Males**: 18 years\n**For Females**: 16 years (under current law)\n\n### Legal Framework:\n\n1. **Child Marriage Restraint Act 1929**\n   - Sets minimum age for marriage\n   - Penalties for violations\n\n2. **Provincial Variations**:\n   - **Sindh**: Minimum age 18 for both (Sindh Child Marriage Restraint Act 2013)\n   - **Punjab**: Working on raising age to 18 for females\n   - **KPK & Balochistan**: Following federal law (16 for females)\n\n### Recent Developments:\n\n- **2021**: Attempts to raise minimum age to 18 for both genders\n- **Sindh**: Already implemented 18 for both\n- **Federal**: Discussions ongoing\n\n### Legal Consequences:\n\n**For Violators**:\n- Imprisonment up to 1 month\n- Fine up to Rs. 1,000\n- Marriage remains valid but punishable\n\n**For Parents/Guardians**:\n- Can be prosecuted\n- Social welfare intervention\n\n### Islamic Perspective:\n\n- Marriage allowed after puberty in Islamic law\n- Modern interpretation emphasizes maturity\n- Many scholars support age 18 minimum\n\n### Recommendations:\n\n1. Follow provincial law in your area\n2. Consider maturity beyond legal age\n3. Ensure consent of both parties\n4. Complete education before marriage\n5. Financial stability important\n\n**Note**: Laws are evolving. Check latest provincial legislation for your area.",
  "language": "english",
  "context": {
    "had_audio": true,
    "had_image": false,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5,
    "auto_detected": true
  }
}
```

---

#### Example 5: With TTS Enabled

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Hello, how are you?"
```

**Response** (200 OK) - When TTS is enabled in admin settings:
```json
{
  "success": true,
  "message": "Hello, how are you?",
  "response": "Hello! I'm doing well, thank you for asking. I'm here to help you with any legal questions or general queries you might have. How can I assist you today?",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": false,
    "legal_results_count": 0,
    "auto_detected": true
  },
  "audio": "//uQxAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAASAAAeMwAUFBQUFCIiIiIiIjAwMDAwPj4+Pj4+TExMTExZWVlZWVlnZ2dnZ3V1dXV1dYODg4ODkZGRkZGRn5+fn5+frKysrKy6urq6urrIyMjIyNbW1tbW1uTk5OTk8vLy8vLy//////8AAAA5TEFNRTMuOThyAZYAAAAAAAAAABQ4JAMGQgAAOAAAHjOBoEWVAAAAAAAAAAAAAAAAAAAA..."
}
```

The `audio` field contains base64-encoded MP3 audio data.

---

#### Example 6: Urdu Query

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=پاکستان میں شادی کی قانونی عمر کیا ہے؟"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "پاکستان میں شادی کی قانونی عمر کیا ہے؟",
  "response": "## پاکستان میں شادی کی قانونی عمر\n\n### موجودہ قانون:\n\n**مردوں کے لیے**: 18 سال\n**خواتین کے لیے**: 16 سال (موجودہ قانون کے تحت)\n\n### قانونی فریم ورک:\n\n1. **چائلڈ میرج ریسٹرینٹ ایکٹ 1929**\n   - شادی کی کم سے کم عمر مقرر کرتا ہے\n   - خلاف ورزی پر سزائیں\n\n2. **صوبائی تغیرات**:\n   - **سندھ**: دونوں کے لیے کم سے کم عمر 18 سال\n   - **پنجاب**: خواتین کے لیے عمر 18 سال کرنے پر کام جاری\n   - **خیبر پختونخوا اور بلوچستان**: وفاقی قانون کی پیروی\n\n### حالیہ پیش رفت:\n\n- **2021**: دونوں جنسوں کے لیے کم سے کم عمر 18 سال کرنے کی کوششیں\n- **سندھ**: پہلے ہی دونوں کے لیے 18 سال نافذ\n- **وفاقی**: بحث جاری\n\n### قانونی نتائج:\n\n**خلاف ورزی کرنے والوں کے لیے**:\n- 1 ماہ تک قید\n- 1000 روپے تک جرمانہ\n- شادی درست رہتی ہے لیکن قابل سزا\n\n### سفارشات:\n\n1. اپنے علاقے میں صوبائی قانون کی پیروی کریں\n2. قانونی عمر سے آگے پختگی پر غور کریں\n3. دونوں فریقوں کی رضامندی یقینی بنائیں\n4. شادی سے پہلے تعلیم مکمل کریں",
  "language": "urdu",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5,
    "auto_detected": true
  }
}
```

---

#### Example 7: Non-Legal Query

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What is the weather like today?"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "What is the weather like today?",
  "response": "I don't have access to real-time weather information. To check today's weather, I recommend:\n\n1. **Weather Websites**:\n   - weather.com\n   - accuweather.com\n   - Pakistan Meteorological Department (pmd.gov.pk)\n\n2. **Mobile Apps**:\n   - Weather app on your phone\n   - Google Weather\n   - AccuWeather app\n\n3. **Quick Check**:\n   - Search \"weather [your city]\" on Google\n   - Ask your voice assistant\n\nIs there anything else I can help you with? I specialize in legal information and general assistance.",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": false,
    "legal_results_count": 0,
    "auto_detected": true
  }
}
```

---

### 2. Audio Mode

**Endpoint**: `POST /api/v1/audio`

#### Example: Voice Question

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/audio \
  -F "audio=@legal_question.mp3" \
  -o response_audio.mp3
```

**Response**: Binary MP3 audio file

**Headers**:
```
HTTP/1.1 200 OK
Content-Type: audio/mpeg
Content-Disposition: attachment; filename=response.mp3
Content-Length: 245678
```

**Flow**:
1. Audio transcribed: "What are my rights as a tenant?"
2. Legal search performed
3. Text response generated
4. Text converted to speech
5. MP3 file returned

---

### 3. Get Settings

**Endpoint**: `GET /api/v1/settings`

#### Example: Get Current Settings

**Request**:
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

**Endpoint**: `POST /api/v1/settings`

#### Example: Enable TTS

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "tts_enabled": true,
    "voice": "nova"
  }'
```

**Response** (200 OK):
```json
{
  "top_k": 5,
  "min_score": 0.5,
  "voice": "nova",
  "tts_enabled": true,
  "note": "use_legal_search and province are auto-detected from query"
}
```

---

#### Example: Update Search Parameters

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "top_k": 10,
    "min_score": 0.6
  }'
```

**Response** (200 OK):
```json
{
  "top_k": 10,
  "min_score": 0.6,
  "voice": "alloy",
  "tts_enabled": false,
  "note": "use_legal_search and province are auto-detected from query"
}
```

---

### 5. Health Check

**Endpoint**: `GET /api/v1/health`

#### Example: Check API Health

**Request**:
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

---

**Response** (503 Service Unavailable):
```json
{
  "detail": "Service unavailable"
}
```

---

## Admin Endpoints

### 1. Admin Login

**Endpoint**: `POST /api/v1/admin/login`

#### Example: Successful Login

**Request**:
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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNTQxMjQwMH0.Xj8kR3mN9pL2qW5vY7zB1cD4eF6gH8iJ0kL2mN4oP6",
  "token_type": "bearer",
  "email": "admin@example.com"
}
```

---

#### Example: Failed Login (Wrong Password)

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "WrongPassword"
  }'
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect email or password"
}
```

---

#### Example: Failed Login (User Not Found)

**Request**:
```bash
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SomePassword"
  }'
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect email or password"
}
```

---

### 2. Get Admin Settings

**Endpoint**: `GET /api/v1/admin/settings`

#### Example: Get Settings (Authenticated)

**Request**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN"
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

#### Example: Unauthorized Access

**Request**:
```bash
curl -X GET http://localhost:8080/api/v1/admin/settings
```

**Response** (403 Forbidden):
```json
{
  "detail": "Not authenticated"
}
```

---

#### Example: Expired Token

**Request**:
```bash
curl -X GET http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer expired_token_here"
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Token has expired"
}
```

---

### 3. Update Admin Settings

**Endpoint**: `POST /api/v1/admin/settings`

#### Example: Update Multiple Settings

**Request**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "top_k": 10,
    "min_score": 0.7,
    "voice": "nova",
    "tts_enabled": true
  }'
```

**Response** (200 OK):
```json
{
  "top_k": 10,
  "min_score": 0.7,
  "voice": "nova",
  "tts_enabled": true,
  "note": "use_legal_search and province are auto-detected from query"
}
```

---

#### Example: Invalid Voice

**Request**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voice": "invalid_voice"
  }'
```

**Response** (400 Bad Request):
```json
{
  "detail": "Invalid voice. Must be one of: alloy, echo, fable, onyx, nova, shimmer"
}
```

---

### 4. Verify Token

**Endpoint**: `GET /api/v1/admin/verify`

#### Example: Valid Token

**Request**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8080/api/v1/admin/verify \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "email": "admin@example.com",
  "valid": true
}
```

---

#### Example: Invalid Token

**Request**:
```bash
curl -X GET http://localhost:8080/api/v1/admin/verify \
  -H "Authorization: Bearer invalid_token"
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Complete Workflow Examples

### Workflow 1: Admin Login and Configure Settings

```bash
# Step 1: Login
TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Step 2: Get current settings
curl -X GET http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN"

# Step 3: Update settings
curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "top_k": 10,
    "voice": "nova",
    "tts_enabled": true
  }'

# Step 4: Verify token is still valid
curl -X GET http://localhost:8080/api/v1/admin/verify \
  -H "Authorization: Bearer $TOKEN"
```

---

### Workflow 2: Send Query with Image and Get Audio Response

```bash
# Step 1: Enable TTS (as admin)
TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePass123"}' \
  | jq -r '.access_token')

curl -X POST http://localhost:8080/api/v1/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tts_enabled": true, "voice": "nova"}'

# Step 2: Send query with image
RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/message \
  -F "message=What does this legal document say?" \
  -F "image=@document.jpg")

# Step 3: Extract and save audio
echo $RESPONSE | jq -r '.audio' | base64 -d > response.mp3

# Step 4: Play audio (on Mac)
afplay response.mp3
```

---

### Workflow 3: Audio-Only Conversation

```bash
# Record audio question
# (Use your device's audio recorder)

# Send audio and get audio response
curl -X POST http://localhost:8080/api/v1/audio \
  -F "audio=@my_question.mp3" \
  -o ai_response.mp3

# Play response
afplay ai_response.mp3
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Not Found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to process message: OpenAI API error"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Service unavailable"
}
```

---

## Testing with Different Tools

### cURL
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Test query"
```

### HTTPie
```bash
http POST http://localhost:8080/api/v1/message \
  message="Test query"
```

### Postman
1. Create new POST request
2. URL: `http://localhost:8080/api/v1/message`
3. Body → form-data
4. Add key "message" with value
5. Send

### Python (requests)
```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/message",
    data={"message": "Test query"}
)
print(response.json())
```

### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('message', 'Test query');

fetch('http://localhost:8080/api/v1/message', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## Next Steps

- See [API Reference](API_REFERENCE.md) for detailed documentation
- Check [Mobile Integration](MOBILE_INTEGRATION.md) for mobile app examples
- Review [Architecture](ARCHITECTURE.md) for system design

