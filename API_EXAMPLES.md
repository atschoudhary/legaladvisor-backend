# LegalAdvisor API Examples

Complete examples for the unified API endpoint.

## Base URL
```
http://localhost:8000/api/v1
```

## Quick Start

The API has just 3 main endpoints:
1. `POST /message` - Send anything (text, image, doc, audio)
2. `POST /settings` - Configure preferences
3. `GET /settings` - Get current settings

## 1. Settings Management

### Get Current Settings
```bash
curl http://localhost:8000/api/v1/settings
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "use_legal_search": false,
    "province": null,
    "top_k": 5,
    "min_score": 0.5,
    "voice": "alloy",
    "tts_enabled": false
  }
}
```

### Update Settings
```bash
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "use_legal_search": true,
    "province": "punjab",
    "top_k": 10,
    "voice": "nova",
    "tts_enabled": false
  }'
```

### PowerShell (Windows)
```powershell
$settings = @{
    use_legal_search = $true
    province = "punjab"
    top_k = 10
    voice = "nova"
    tts_enabled = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/settings" `
  -Method Post `
  -Body $settings `
  -ContentType "application/json"
```

## 2. Send Messages

### Simple Text Message
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=What are fundamental rights in Pakistan?"
```

### Text Message in Urdu
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=پاکستان میں بنیادی حقوق کیا ہیں؟"
```

### Message with Image
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=What is in this image?" \
  -F "image=@photo.jpg"
```

### Message with Document
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=Summarize this legal document" \
  -F "document=@contract.pdf"
```

### Voice Message (Audio Only)
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=" \
  -F "audio=@recording.mp3"
```

### Combined: Text + Image + Document
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=Analyze this contract and the attached image" \
  -F "image=@signature.jpg" \
  -F "document=@contract.pdf"
```

### With Legal Search Enabled
First enable legal search:
```bash
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"use_legal_search": true, "province": "punjab"}'
```

Then send message:
```bash
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=What are the arrest procedures in Punjab?"
```

## 3. PowerShell Examples (Windows)

### Simple Message
```powershell
$form = @{
    message = "What is property law in Pakistan?"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/message" `
  -Method Post `
  -Form $form
```

### Message with Image
```powershell
$form = @{
    message = "What is in this image?"
    image = Get-Item -Path "photo.jpg"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/message" `
  -Method Post `
  -Form $form
```

### Message with Document
```powershell
$form = @{
    message = "Summarize this document"
    document = Get-Item -Path "contract.pdf"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/message" `
  -Method Post `
  -Form $form
```

### Message with Audio
```powershell
$form = @{
    message = ""
    audio = Get-Item -Path "recording.mp3"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/message" `
  -Method Post `
  -Form $form
```

## 4. Python Examples

### Simple Message
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/message",
    data={"message": "What are fundamental rights?"}
)
print(response.json())
```

### Message with Image
```python
import requests

with open("photo.jpg", "rb") as img:
    response = requests.post(
        "http://localhost:8000/api/v1/message",
        data={"message": "What is in this image?"},
        files={"image": img}
    )
print(response.json())
```

### Message with Document
```python
import requests

with open("contract.pdf", "rb") as doc:
    response = requests.post(
        "http://localhost:8000/api/v1/message",
        data={"message": "Summarize this document"},
        files={"document": doc}
    )
print(response.json())
```

### Message with Audio
```python
import requests

with open("recording.mp3", "rb") as audio:
    response = requests.post(
        "http://localhost:8000/api/v1/message",
        data={"message": ""},
        files={"audio": audio}
    )
print(response.json())
```

### Combined: Image + Document
```python
import requests

with open("photo.jpg", "rb") as img, open("contract.pdf", "rb") as doc:
    response = requests.post(
        "http://localhost:8000/api/v1/message",
        data={"message": "Analyze both files"},
        files={
            "image": img,
            "document": doc
        }
    )
print(response.json())
```

### Update Settings
```python
import requests

settings = {
    "use_legal_search": True,
    "province": "punjab",
    "top_k": 10,
    "voice": "nova",
    "tts_enabled": False
}

response = requests.post(
    "http://localhost:8000/api/v1/settings",
    json=settings
)
print(response.json())
```

## 5. JavaScript/Fetch Examples

### Simple Message
```javascript
const formData = new FormData();
formData.append('message', 'What are fundamental rights?');

fetch('http://localhost:8000/api/v1/message', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Message with Image
```javascript
const formData = new FormData();
formData.append('message', 'What is in this image?');
formData.append('image', imageFile); // File from input

fetch('http://localhost:8000/api/v1/message', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Update Settings
```javascript
const settings = {
    use_legal_search: true,
    province: 'punjab',
    top_k: 10,
    voice: 'nova',
    tts_enabled: false
};

fetch('http://localhost:8000/api/v1/settings', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
})
.then(response => response.json())
.then(data => console.log(data));
```

## 6. Response Examples

### Successful Text Response
```json
{
  "success": true,
  "message": "What are fundamental rights?",
  "response": "## Fundamental Rights in Pakistan\n\nFundamental rights are...",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5
  }
}
```

### Response with Image Analysis
```json
{
  "success": true,
  "message": "What is in this image?",
  "response": "## Image Analysis\n\nThe image shows...",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": true,
    "had_document": false,
    "used_legal_search": false,
    "legal_results_count": 0
  }
}
```

### Response with TTS Audio
```json
{
  "success": true,
  "message": "Explain property law",
  "response": "## Property Law\n\nProperty law governs...",
  "language": "english",
  "context": {
    "had_audio": false,
    "had_image": false,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5
  },
  "audio": "base64_encoded_mp3_data...",
  "audio_format": "mp3"
}
```

### Error Response
```json
{
  "detail": "Unsupported file type. Allowed: .pdf, .docx, .txt"
}
```

## 7. Common Use Cases

### Use Case 1: Simple Legal Query
```bash
# 1. Enable legal search
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"use_legal_search": true}'

# 2. Send query
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=What is the legal age for marriage?"
```

### Use Case 2: Document Analysis with Legal Context
```bash
# 1. Enable legal search
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"use_legal_search": true, "province": "sindh"}'

# 2. Analyze document
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=Is this contract legally valid in Sindh?" \
  -F "document=@contract.pdf"
```

### Use Case 3: Voice Query with TTS Response
```bash
# 1. Enable TTS
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"tts_enabled": true, "voice": "nova"}'

# 2. Send voice query
curl -X POST http://localhost:8000/api/v1/message \
  -F "audio=@question.mp3" \
  -o response.json

# 3. Extract and play audio
# Audio is in response.json as base64
```

### Use Case 4: Image OCR + Legal Search
```bash
# 1. Enable legal search
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"use_legal_search": true}'

# 2. Send image of legal document
curl -X POST http://localhost:8000/api/v1/message \
  -F "message=Extract and explain the legal text in this image" \
  -F "image=@legal_doc_photo.jpg"
```

## 8. Testing Workflow

1. **Start with settings**:
   ```bash
   curl http://localhost:8000/api/v1/settings
   ```

2. **Configure as needed**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/settings \
     -H "Content-Type: application/json" \
     -d '{"use_legal_search": true, "province": "punjab"}'
   ```

3. **Send messages**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/message \
     -F "message=Your question here"
   ```

4. **Test with files**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/message \
     -F "message=Analyze this" \
     -F "image=@file.jpg"
   ```

## 9. Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `use_legal_search` | boolean | false | Enable legal document search |
| `province` | string | null | Filter by province (sindh, punjab, khyber_pakhtunkhwa, balochistan) |
| `top_k` | integer | 5 | Number of search results (1-20) |
| `min_score` | float | 0.5 | Minimum relevance score (0.0-1.0) |
| `voice` | string | "alloy" | TTS voice (alloy, echo, fable, onyx, nova, shimmer) |
| `tts_enabled` | boolean | false | Enable audio responses |

## 10. Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (invalid file type, missing params) |
| 500 | Server error (processing failed) |

## Notes

- All file uploads use `multipart/form-data`
- Settings updates use `application/json`
- Settings persist for the session (use database in production)
- Audio responses are base64 encoded MP3
- Markdown formatting in responses
- Automatic language detection
- Context is automatically integrated
