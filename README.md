# LegalAdvisor Backend API

FastAPI backend for LegalAdvisor - A unified multilingual AI-powered legal assistant for Pakistani law.

## Overview

Simple, unified API with just **3 endpoints** for all functionality:
- Send messages (text, image, document, audio)
- Manage settings
- Health check

## Features

### Unified Message Endpoint
One endpoint handles everything:
- ✅ Text chat in multiple languages
- ✅ Image analysis and OCR
- ✅ Document analysis (PDF, DOCX, TXT)
- ✅ Voice transcription (Speech-to-Text)
- ✅ Legal document search
- ✅ Web search enhancement
- ✅ AI-powered answer synthesis
- ✅ Optional Text-to-Speech responses

### Supported Languages
- **English** - Full support
- **Urdu** - اردو - Full support
- **Punjabi** - پنجابی (Shahmukhi script) - Full support
- **Sindhi** - سنڌي - Full support
- **Roman Urdu** - Urdu in English alphabet - Full support

### Supported File Formats
- **Documents**: PDF, DOCX, TXT
- **Images**: JPG, JPEG, PNG, GIF, WebP
- **Audio**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM

## API Endpoints

### 1. Send Message
```
POST /api/v1/message
```
Unified endpoint for all interactions. Accepts text, images, documents, and audio.

**Parameters** (multipart/form-data):
- `message` (string, required*) - Text message/query
- `image` (file, optional) - Image file
- `document` (file, optional) - Document file
- `audio` (file, optional) - Audio file

*Required unless audio is provided (audio will be transcribed)

**Response**:
```json
{
  "success": true,
  "message": "User's message",
  "response": "AI answer in markdown",
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

### 2. Update Settings
```
POST /api/v1/settings
```
Configure admin preferences.

**Body** (application/json):
```json
{
  "top_k": 5,
  "min_score": 0.5,
  "voice": "alloy",
  "tts_enabled": false
}
```

**Admin Settings Options**:
- `top_k` (integer) - Number of results (1-20)
- `min_score` (float) - Minimum relevance score (0.0-1.0)
- `voice` (string) - TTS voice (alloy, echo, fable, onyx, nova, shimmer)
- `tts_enabled` (boolean) - Enable audio responses

**Auto-Detected (Cannot be configured)**:
- `use_legal_search` - Automatically enabled when legal keywords are detected
- `province` - Automatically detected from query content

### 3. Get Settings
```
GET /api/v1/settings
```
Retrieve current settings.

### 4. Health Check
```
GET /api/v1/health
```
Check API status and available collections.

## Installation

### 1. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
ENVIRONMENT=development
```

### 4. Run Server
```powershell
cd backend
uvicorn main:app --reload
```

Server will be available at `http://localhost:8080`

## Documentation

### Interactive API Documentation
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Testing UI**: http://localhost:8080

### Complete Documentation
For comprehensive documentation, see the **[docs/](docs/)** folder:

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and setup guide
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[API Examples](docs/API_EXAMPLES.md)** - Request/response examples
- **[Features](docs/FEATURES.md)** - Complete feature list
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Environment](docs/ENVIRONMENT.md)** - Environment configuration
- **[Mobile Integration](docs/MOBILE_INTEGRATION.md)** - Mobile app integration

**Quick Start**: [docs/README.md](docs/README.md)

## Usage Examples

### Simple Text Query
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What are fundamental rights in Pakistan?"
```

### Query with Image
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What is in this image?" \
  -F "image=@photo.jpg"
```

### Document Analysis
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Summarize this document" \
  -F "document=@contract.pdf"
```

### Voice Query
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=" \
  -F "audio=@recording.mp3"
```

### Update Settings
```bash
curl -X POST http://localhost:8080/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{"tts_enabled": true, "voice": "nova", "top_k": 10}'
```

## Project Structure

```
backend/
├── main.py                              # FastAPI application
├── config.py                            # Configuration
├── models.py                            # Pydantic models
├── requirements.txt                     # Dependencies
├── routers/
│   ├── health.py                       # Health check
│   └── unified.py                      # Unified message endpoint
├── services/
│   ├── embedding_service.py            # OpenAI embeddings
│   ├── qdrant_service.py              # Vector search
│   ├── translation_service.py         # Language detection
│   ├── query_orchestrator.py          # Collection selection
│   ├── web_search_service.py          # Web enhancement
│   ├── answer_synthesis_service.py    # AI synthesis
│   ├── multilingual_chat_service.py   # Chat functionality
│   ├── document_reader_service.py     # Document processing
│   ├── voice_service.py               # Speech processing
│   └── image_understanding_service.py # Image analysis
└── static/
    └── index.html                      # Testing UI
```

## Technologies

- **FastAPI** - Modern web framework
- **OpenAI API** - AI capabilities (GPT-4o, Whisper, TTS, Vision)
- **Qdrant** - Vector database
- **PyPDF2** - PDF extraction
- **python-docx** - DOCX extraction
- **Pydantic** - Data validation

## Mobile Integration

The unified endpoint is designed for seamless mobile integration:

1. **Configure admin settings once** (on app start or in settings screen)
2. **Send any combination** of text, image, document, or audio
3. **System automatically detects** legal queries and province
4. **Receive unified response** with optional TTS audio

See [MOBILE_IMPLEMENTATION.md](MOBILE_IMPLEMENTATION.md) for detailed mobile integration guide.

## Error Handling

All errors return:
```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad request (invalid file, missing params)
- `500` - Server error

## Notes

- Backend is independent from Phase 1 ingestion code
- All AI features use OpenAI API
- Vector search uses Qdrant Cloud
- Settings are stored in memory (use database in production)
- Optimized for mobile app integration
- Supports both regular and streaming responses (chat)

## Development

Run with auto-reload:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Use the web interface at `http://localhost:8080` to test all features before mobile implementation.
