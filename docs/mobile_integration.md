# Mobile Integration Guide

Complete guide for integrating LegalAdvisor API into mobile applications.

## Overview

The LegalAdvisor API is designed for seamless mobile integration with:
- Simple unified endpoint
- AI-powered auto-detection
- Multi-modal input support
- Efficient responses

## Quick Start

### 1. Configure Base URL

```javascript
// React Native / JavaScript
const API_BASE = 'https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1';
```

```swift
// iOS / Swift
let API_BASE = "https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1"
```

```kotlin
// Android / Kotlin
const val API_BASE = "https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1"
```

### 2. Send Message

```javascript
// React Native
const sendMessage = async (text) => {
  const formData = new FormData();
  formData.append('message', text);
  
  const response = await fetch(`${API_BASE}/message`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

### 3. Handle Response

```javascript
const data = await sendMessage("What are fundamental rights?");

console.log(data.response);  // AI response
console.log(data.language);  // Detected language
console.log(data.context.used_legal_search);  // Auto-detected
```

## Complete Examples

### React Native

See [../MOBILE_IMPLEMENTATION.md](../MOBILE_IMPLEMENTATION.md) for complete React Native examples.

### iOS (Swift)

```swift
import Foundation

class LegalAdvisorAPI {
    let baseURL = "https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1"
    
    func sendMessage(text: String, completion: @escaping (Result<MessageResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/message")!
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
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "", code: -1)))
                return
            }
            
            do {
                let response = try JSONDecoder().decode(MessageResponse.self, from: data)
                completion(.success(response))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

struct MessageResponse: Codable {
    let success: Bool
    let message: String
    let response: String
    let language: String
    let context: Context
    let audio: String?
}

struct Context: Codable {
    let hadAudio: Bool
    let hadImage: Bool
    let hadDocument: Bool
    let usedLegalSearch: Bool
    let legalResultsCount: Int
    let autoDetected: Bool
    
    enum CodingKeys: String, CodingKey {
        case hadAudio = "had_audio"
        case hadImage = "had_image"
        case hadDocument = "had_document"
        case usedLegalSearch = "used_legal_search"
        case legalResultsCount = "legal_results_count"
        case autoDetected = "auto_detected"
    }
}
```

### Android (Kotlin)

```kotlin
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import com.google.gson.Gson
import java.io.File

class LegalAdvisorAPI {
    private val baseUrl = "https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev/api/v1"
    private val client = OkHttpClient()
    private val gson = Gson()
    
    fun sendMessage(
        text: String,
        image: File? = null,
        document: File? = null,
        audio: File? = null,
        callback: (Result<MessageResponse>) -> Unit
    ) {
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("message", text)
        
        image?.let {
            requestBody.addFormDataPart(
                "image",
                it.name,
                it.asRequestBody("image/*".toMediaType())
            )
        }
        
        document?.let {
            requestBody.addFormDataPart(
                "document",
                it.name,
                it.asRequestBody("application/*".toMediaType())
            )
        }
        
        audio?.let {
            requestBody.addFormDataPart(
                "audio",
                it.name,
                it.asRequestBody("audio/*".toMediaType())
            )
        }
        
        val request = Request.Builder()
            .url("$baseUrl/message")
            .post(requestBody.build())
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(Result.failure(e))
            }
            
            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let { json ->
                    try {
                        val data = gson.fromJson(json, MessageResponse::class.java)
                        callback(Result.success(data))
                    } catch (e: Exception) {
                        callback(Result.failure(e))
                    }
                }
            }
        })
    }
}

data class MessageResponse(
    val success: Boolean,
    val message: String,
    val response: String,
    val language: String,
    val context: Context,
    val audio: String?
)

data class Context(
    val had_audio: Boolean,
    val had_image: Boolean,
    val had_document: Boolean,
    val used_legal_search: Boolean,
    val legal_results_count: Int,
    val auto_detected: Boolean
)
```

## Features

### Auto-Detection

The API automatically detects:
- **Legal queries**: No manual configuration
- **Province**: From query content
- **Language**: From user input

```javascript
// Just send the query
const response = await sendMessage("Can I marry at 16?");

// API automatically detects:
// - Legal query: true
// - Language: english
// - Province: (if mentioned)
```

### Multi-Modal Input

Send any combination of inputs:

```javascript
// Text only
formData.append('message', 'What is this?');

// Text + Image
formData.append('message', 'Explain this image');
formData.append('image', imageFile);

// Text + Document
formData.append('message', 'Summarize this');
formData.append('document', pdfFile);

// Audio only
formData.append('audio', audioFile);
```

### Settings Management

```javascript
// Get settings
const settings = await fetch(`${API_BASE}/settings`).then(r => r.json());

// Update settings (optional)
await fetch(`${API_BASE}/settings`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tts_enabled: true,
    voice: 'nova'
  })
});
```

## Best Practices

### 1. Error Handling

```javascript
try {
  const response = await sendMessage(text);
  if (response.success) {
    // Handle success
  } else {
    // Handle API error
  }
} catch (error) {
  // Handle network error
}
```

### 2. Loading States

```javascript
const [loading, setLoading] = useState(false);

const handleSend = async () => {
  setLoading(true);
  try {
    const response = await sendMessage(text);
    // Handle response
  } finally {
    setLoading(false);
  }
};
```

### 3. File Validation

```javascript
const validateFile = (file) => {
  const maxSize = 25 * 1024 * 1024; // 25MB
  if (file.size > maxSize) {
    throw new Error('File too large');
  }
  
  const validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
  if (!validTypes.includes(file.type)) {
    throw new Error('Invalid file type');
  }
};
```

### 4. Response Caching

```javascript
const cache = new Map();

const sendMessageCached = async (text) => {
  if (cache.has(text)) {
    return cache.get(text);
  }
  
  const response = await sendMessage(text);
  cache.set(text, response);
  return response;
};
```

### 5. Timeout Handling

```javascript
const sendMessageWithTimeout = async (text, timeout = 30000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(`${API_BASE}/message`, {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
};
```

## UI/UX Recommendations

### 1. Show Detection Status

```javascript
if (response.context.used_legal_search) {
  showBadge("Legal Search Enabled 🔍");
}

if (response.context.auto_detected) {
  showBadge("Auto-Detected by AI ✨");
}
```

### 2. Language Indicator

```javascript
const languageNames = {
  english: "English",
  urdu: "اردو",
  punjabi: "پنجابی",
  sindhi: "سنڌي",
  roman_urdu: "Roman Urdu"
};

showLanguage(languageNames[response.language]);
```

### 3. Audio Playback

```javascript
if (response.audio) {
  const audioBlob = base64ToBlob(response.audio, 'audio/mpeg');
  const audioUrl = URL.createObjectURL(audioBlob);
  playAudio(audioUrl);
}
```

### 4. Markdown Rendering

```javascript
import Markdown from 'react-native-markdown-display';

<Markdown>
  {response.response}
</Markdown>
```

## Performance Optimization

### 1. Request Compression

```javascript
headers: {
  'Accept-Encoding': 'gzip, deflate'
}
```

### 2. Image Compression

```javascript
import ImageResizer from 'react-native-image-resizer';

const compressImage = async (uri) => {
  return await ImageResizer.createResizedImage(
    uri,
    1024,
    1024,
    'JPEG',
    80
  );
};
```

### 3. Lazy Loading

```javascript
const [messages, setMessages] = useState([]);
const [page, setPage] = useState(0);

const loadMore = async () => {
  // Load more messages
};
```

## Testing

### Unit Tests

```javascript
describe('LegalAdvisorAPI', () => {
  it('should send message', async () => {
    const response = await sendMessage('test');
    expect(response.success).toBe(true);
  });
  
  it('should handle errors', async () => {
    await expect(sendMessage('')).rejects.toThrow();
  });
});
```

### Integration Tests

```javascript
describe('Message Flow', () => {
  it('should detect legal query', async () => {
    const response = await sendMessage('What are fundamental rights?');
    expect(response.context.used_legal_search).toBe(true);
  });
});
```

## Troubleshooting

### Network Errors

```javascript
if (error.message === 'Network request failed') {
  // Check internet connection
  // Retry with exponential backoff
}
```

### Timeout Errors

```javascript
if (error.name === 'AbortError') {
  // Request timed out
  // Increase timeout or retry
}
```

### File Upload Errors

```javascript
if (response.status === 400) {
  // Invalid file format or size
  // Validate before upload
}
```

## Resources

- [API Reference](API_REFERENCE.md)
- [Complete Examples](../MOBILE_IMPLEMENTATION.md)
- [Audio Mode Guide](../AUDIO_MODE.md)
- [Features List](FEATURES.md)

## Support

For issues or questions:
- Check [API Reference](API_REFERENCE.md)
- Review error messages
- Test with cURL first
- Contact support
