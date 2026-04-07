# Mobile Implementation Guide

## Simple Unified Approach

Instead of calling multiple endpoints, use **ONE endpoint** for everything: `/api/v1/message`

## How It Works

### 1. Settings (One Time Setup)
```
POST /api/v1/settings
```

Set user preferences once:
```json
{
  "use_legal_search": true,
  "province": "punjab",
  "top_k": 5,
  "min_score": 0.5,
  "voice": "alloy",
  "tts_enabled": false
}
```

### 2. Send Messages (All Interactions)
```
POST /api/v1/message
```

**One endpoint handles everything:**

#### Example 1: Simple Text Chat
```
FormData:
- message: "What is property law?"
```

#### Example 2: Text + Image
```
FormData:
- message: "What is in this image?"
- image: <file>
```

#### Example 3: Voice Query
```
FormData:
- audio: <audio_file>
- message: "" (optional, will be transcribed from audio)
```

#### Example 4: Document Analysis
```
FormData:
- message: "Summarize this document"
- document: <pdf_file>
```

#### Example 5: Combined (Image + Legal Search)
```
Settings: use_legal_search = true

FormData:
- message: "Explain this legal document"
- image: <image_of_document>
```

## Mobile App Flow

```
┌─────────────────────────────────────────┐
│         User Opens App                  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   Load Settings (GET /api/v1/settings) │
│   - Legal search: ON/OFF                │
│   - Province: All/Specific              │
│   - Voice: alloy/nova/etc               │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         User Interaction                │
│  ┌─────────────────────────────────┐   │
│  │ Text Input                      │   │
│  │ + Optional: Image/Doc/Audio     │   │
│  └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   POST /api/v1/message                  │
│   - Send everything in one request     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         Receive Response                │
│   {                                     │
│     "response": "Answer...",            │
│     "language": "english",              │
│     "audio": "base64..." (if TTS on)    │
│   }                                     │
└─────────────────────────────────────────┘
```

## Android Example (Kotlin)

```kotlin
// 1. Update Settings (once)
fun updateSettings() {
    val settings = JSONObject().apply {
        put("use_legal_search", true)
        put("province", "punjab")
        put("tts_enabled", false)
    }
    
    val request = JsonObjectRequest(
        Request.Method.POST,
        "$API_BASE/settings",
        settings,
        { response -> /* Settings updated */ },
        { error -> /* Handle error */ }
    )
    
    queue.add(request)
}

// 2. Send Message (text only)
fun sendTextMessage(message: String) {
    val request = object : StringRequest(
        Method.POST,
        "$API_BASE/message",
        { response -> handleResponse(response) },
        { error -> handleError(error) }
    ) {
        override fun getParams(): Map<String, String> {
            return mapOf("message" to message)
        }
    }
    
    queue.add(request)
}

// 3. Send Message with Image
fun sendMessageWithImage(message: String, imageFile: File) {
    val request = object : VolleyMultipartRequest(
        Method.POST,
        "$API_BASE/message",
        { response -> handleResponse(response) },
        { error -> handleError(error) }
    ) {
        override fun getParams(): Map<String, String> {
            return mapOf("message" to message)
        }
        
        override fun getByteData(): Map<String, DataPart> {
            return mapOf(
                "image" to DataPart(
                    imageFile.name,
                    imageFile.readBytes(),
                    "image/jpeg"
                )
            )
        }
    }
    
    queue.add(request)
}

// 4. Send Voice Message
fun sendVoiceMessage(audioFile: File) {
    val request = object : VolleyMultipartRequest(
        Method.POST,
        "$API_BASE/message",
        { response -> handleResponse(response) },
        { error -> handleError(error) }
    ) {
        override fun getParams(): Map<String, String> {
            return mapOf("message" to "")
        }
        
        override fun getByteData(): Map<String, DataPart> {
            return mapOf(
                "audio" to DataPart(
                    audioFile.name,
                    audioFile.readBytes(),
                    "audio/mp3"
                )
            )
        }
    }
    
    queue.add(request)
}

// 5. Handle Response
fun handleResponse(response: String) {
    val json = JSONObject(response)
    val answer = json.getString("response")
    val language = json.getString("language")
    
    // Display answer
    displayMessage(answer)
    
    // Play audio if TTS enabled
    if (json.has("audio")) {
        val audioBase64 = json.getString("audio")
        playAudio(audioBase64)
    }
}
```

## iOS Example (Swift)

```swift
// 1. Update Settings
func updateSettings() {
    let settings: [String: Any] = [
        "use_legal_search": true,
        "province": "punjab",
        "tts_enabled": false
    ]
    
    let url = URL(string: "\(API_BASE)/settings")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try? JSONSerialization.data(withJSONObject: settings)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        // Handle response
    }.resume()
}

// 2. Send Text Message
func sendMessage(text: String) {
    let url = URL(string: "\(API_BASE)/message")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    
    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", 
                     forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    body.append("--\(boundary)\r\n")
    body.append("Content-Disposition: form-data; name=\"message\"\r\n\r\n")
    body.append("\(text)\r\n")
    body.append("--\(boundary)--\r\n")
    
    request.httpBody = body
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        self.handleResponse(data: data)
    }.resume()
}

// 3. Send Message with Image
func sendMessageWithImage(text: String, image: UIImage) {
    let url = URL(string: "\(API_BASE)/message")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    
    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", 
                     forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    
    // Add message
    body.append("--\(boundary)\r\n")
    body.append("Content-Disposition: form-data; name=\"message\"\r\n\r\n")
    body.append("\(text)\r\n")
    
    // Add image
    if let imageData = image.jpegData(compressionQuality: 0.8) {
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n")
        body.append("Content-Type: image/jpeg\r\n\r\n")
        body.append(imageData)
        body.append("\r\n")
    }
    
    body.append("--\(boundary)--\r\n")
    request.httpBody = body
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        self.handleResponse(data: data)
    }.resume()
}
```

## Benefits of Unified Approach

### ✅ Simple
- One endpoint for everything
- No need to decide which endpoint to call
- Settings managed separately

### ✅ Flexible
- Send text only
- Send text + image
- Send text + document
- Send audio (transcribed automatically)
- Any combination

### ✅ Efficient
- One request instead of multiple
- Backend handles all processing
- Automatic context integration

### ✅ Consistent
- Same response format always
- Same error handling
- Same authentication (when added)

## Response Format

Always returns:
```json
{
  "success": true,
  "message": "User's message",
  "response": "AI's answer in markdown",
  "language": "detected language",
  "context": {
    "had_audio": false,
    "had_image": true,
    "had_document": false,
    "used_legal_search": true,
    "legal_results_count": 5
  },
  "audio": "base64..." // Only if TTS enabled
}
```

## Settings Options

```json
{
  "use_legal_search": false,    // Enable legal document search
  "province": null,              // Filter by province
  "top_k": 5,                    // Number of results
  "min_score": 0.5,              // Minimum relevance
  "voice": "alloy",              // TTS voice
  "tts_enabled": false           // Enable audio responses
}
```

## Error Handling

All errors return:
```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad request (invalid file, missing params)
- 500: Server error

## Testing

Use the web interface at `http://localhost:8000` to test all features before mobile implementation.
