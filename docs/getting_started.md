# Getting Started

Quick start guide for LegalAdvisor API.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key
- Qdrant vector database

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:
```env
# Environment
ENVIRONMENT=development

# OpenAI
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-large

# Qdrant
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

# Database
DB_HOST=your_db_host
DB_PORT=6438
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_SSLMODE=require

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 5. Initialize Database
```bash
python create_admin.py init
```

### 6. Create Admin User
```bash
python create_admin.py create
# Enter email: admin@example.com
# Enter password: ********
```

### 7. Run Server
```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Production
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Quick Test

### 1. Check Health
```bash
curl http://localhost:8080/api/v1/health
```

### 2. Send Test Message
```bash
curl -X POST http://localhost:8080/api/v1/message \
  -F "message=Hello, how are you?"
```

### 3. Test Admin Login
```bash
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}'
```

### 4. Access Web UI
Open browser: http://localhost:8080

### 5. Access Admin Panel
Open browser: http://localhost:8080/admin.html

## Next Steps

1. Read [API Reference](API_REFERENCE.md)
2. Explore [Features](FEATURES.md)
3. Review [Architecture](ARCHITECTURE.md)
4. Check [Deployment Guide](DEPLOYMENT.md)
5. See [Mobile Integration](MOBILE_INTEGRATION.md)

## Common Issues

### Database Connection Failed
- Check database credentials in `.env`
- Verify network connectivity
- Ensure SSL mode is correct

### OpenAI API Error
- Verify API key is valid
- Check API quota/limits
- Ensure correct model names

### Port Already in Use
```bash
# Change port in command
uvicorn main:app --port 8081
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

### 1. Make Changes
Edit code in your preferred editor

### 2. Test Locally
```bash
uvicorn main:app --reload
```

### 3. Run Tests
```bash
# Test endpoints
curl http://localhost:8080/api/v1/health
```

### 4. Check Logs
Monitor console output for errors

### 5. Deploy
Follow [Deployment Guide](DEPLOYMENT.md)

## Support

- Documentation: `/docs` folder
- API Docs: http://localhost:8080/docs
- Issues: Create GitHub issue
