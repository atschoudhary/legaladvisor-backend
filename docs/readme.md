# LegalAdvisor API Documentation

Complete documentation for the LegalAdvisor multilingual legal assistant API.

## 📚 Documentation Index

### Getting Started
- **[Getting Started Guide](GETTING_STARTED.md)** - Installation and quick start
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[API Examples](API_EXAMPLES.md)** - Request/response examples for all endpoints
- **[Features](FEATURES.md)** - Complete feature list

### Architecture & Design
- **[Architecture](ARCHITECTURE.md)** - System architecture and design
- **[Settings Architecture](../SETTINGS_ARCHITECTURE.md)** - Settings system design
- **[LLM Detection](../LLM_DETECTION.md)** - AI-powered detection details

### Admin & Management
- **[Admin System](../ADMIN_SYSTEM.md)** - Admin system overview
- **[Admin Setup](../ADMIN_SETUP.md)** - Admin user management
- **[Complete Audit](../COMPLETE_AUDIT.md)** - System audit report

### Integration Guides
- **[Mobile Integration](MOBILE_INTEGRATION.md)** - Mobile app integration
- **[Audio Mode](../AUDIO_MODE.md)** - Audio-only endpoint guide
- **[TTS Implementation](../TTS_IMPLEMENTATION.md)** - Text-to-speech guide

### Deployment
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment guide
- **[Environment Configuration](ENVIRONMENT.md)** - Environment variables reference

## 🚀 Quick Links

### For Developers
1. [Getting Started](GETTING_STARTED.md) - Start here
2. [API Reference](API_REFERENCE.md) - API documentation
3. [Architecture](ARCHITECTURE.md) - System design

### For Administrators
1. [Admin Setup](../ADMIN_SETUP.md) - Create admin accounts
2. [Admin System](../ADMIN_SYSTEM.md) - Manage settings
3. [Deployment Guide](DEPLOYMENT.md) - Deploy to production

### For Mobile Developers
1. [Mobile Integration](MOBILE_INTEGRATION.md) - Integration guide
2. [API Reference](API_REFERENCE.md) - API endpoints
3. [Audio Mode](../AUDIO_MODE.md) - Voice features

## 🎯 Common Tasks

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python create_admin.py init

# Create admin user
python create_admin.py create

# Run server
uvicorn main:app --reload
```

### API Usage
```bash
# Send message
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=What are fundamental rights?"

# Admin login
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass123"}'
```

### Access Points
- **API**: http://localhost:8080/api/v1
- **Web UI**: http://localhost:8080
- **Admin Panel**: http://localhost:8080/admin.html
- **API Docs**: http://localhost:8080/docs

## 📖 Documentation Structure

```
docs/
├── README.md                    # This file
├── GETTING_STARTED.md          # Installation & setup
├── API_REFERENCE.md            # Complete API docs
├── FEATURES.md                 # Feature list
├── ARCHITECTURE.md             # System architecture
├── MOBILE_INTEGRATION.md       # Mobile guide
├── DEPLOYMENT.md               # Deployment guide
└── ENVIRONMENT.md              # Environment config

../
├── ADMIN_SYSTEM.md             # Admin overview
├── ADMIN_SETUP.md              # Admin management
├── SETTINGS_ARCHITECTURE.md    # Settings design
├── LLM_DETECTION.md            # AI detection
├── AUDIO_MODE.md               # Audio endpoint
├── TTS_IMPLEMENTATION.md       # TTS guide
└── COMPLETE_AUDIT.md           # System audit
```

## 🔑 Key Features

### Multilingual Support
- English, Urdu, Punjabi, Sindhi, Roman Urdu
- Automatic language detection
- Responses in user's language

### AI-Powered
- LLM-based legal query detection
- Province auto-detection
- Context-aware responses
- 96% accuracy

### Multi-Modal Input
- Text messages
- Images (with OCR)
- Documents (PDF, DOCX, TXT)
- Audio (Speech-to-Text)

### Voice Features
- Speech-to-Text (Whisper)
- Text-to-Speech (6 voices)
- Audio-only mode

### Admin System
- Secure authentication (JWT + bcrypt)
- Settings management
- Web interface
- Database storage

### Legal Search
- Vector-based search
- Province-specific
- Web enhancement
- AI synthesis

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: PostgreSQL, Qdrant
- **AI**: OpenAI (GPT-4o, Whisper, TTS, Vision)
- **Auth**: JWT, bcrypt
- **Frontend**: HTML/CSS/JavaScript

## 📊 API Endpoints

### Public Endpoints
- `POST /api/v1/message` - Send message
- `POST /api/v1/audio` - Audio mode
- `GET /api/v1/settings` - Get settings
- `POST /api/v1/settings` - Update settings
- `GET /api/v1/health` - Health check

### Admin Endpoints (Protected)
- `POST /api/v1/admin/login` - Login
- `GET /api/v1/admin/settings` - Get settings
- `POST /api/v1/admin/settings` - Update settings
- `GET /api/v1/admin/verify` - Verify token

## 🔒 Security

- JWT authentication
- Bcrypt password hashing
- SSL/TLS support
- Input validation
- SQL injection prevention
- CORS configuration

## 📈 Performance

- Async operations
- Connection pooling
- Efficient queries
- Caching support
- Response time: 2-5s (with legal search)

## 🌐 Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Production
- Deployed on Leapcell
- HTTPS enabled
- Database connected
- Auto-scaling

**Production URL**: https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev

## 📞 Support

- **Documentation**: `/docs` folder
- **API Docs**: http://localhost:8080/docs
- **Issues**: Create GitHub issue
- **Email**: support@legaladvisor.com

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

## 📅 Version

**Current Version**: 2.0.0

**Last Updated**: April 2026

---

**Ready to get started?** → [Getting Started Guide](GETTING_STARTED.md)
