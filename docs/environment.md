# Environment Configuration

Complete guide for configuring environment variables.

## Environment File

Create a `.env` file in the project root with all required variables.

### Template

```env
# ============================================================
# ENVIRONMENT
# ============================================================
ENVIRONMENT=development

# ============================================================
# OPENAI CONFIGURATION
# ============================================================
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-large

# ============================================================
# QDRANT VECTOR DATABASE
# ============================================================
QDRANT_URL=https://your-qdrant-instance.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here

# ============================================================
# POSTGRESQL DATABASE
# ============================================================
DB_HOST=your_database_host.leapcellpool.com
DB_PORT=6438
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_SSLMODE=require

# ============================================================
# JWT AUTHENTICATION
# ============================================================
JWT_SECRET_KEY=your-secret-key-change-in-production-use-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

---

## Variable Reference

### ENVIRONMENT

**Type**: String  
**Required**: Yes  
**Default**: `development`  
**Options**: `development`, `staging`, `production`

Controls application behavior and logging level.

```env
ENVIRONMENT=production
```

**Effects**:
- `development`: Debug mode, auto-reload, verbose logging
- `staging`: Production-like, with debug logs
- `production`: Optimized, minimal logging

---

### OPENAI_API_KEY

**Type**: String  
**Required**: Yes  
**Format**: `sk-...`

Your OpenAI API key for accessing GPT, Whisper, TTS, and Vision models.

```env
OPENAI_API_KEY=sk-proj-abc123...
```

**Get API Key**:
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and save securely

**Models Used**:
- `gpt-4o` - Main chat and synthesis
- `gpt-4o-mini` - Legal query detection
- `whisper-1` - Speech-to-Text
- `tts-1` - Text-to-Speech
- `gpt-4o` (vision) - Image understanding

**Cost Considerations**:
- Monitor usage at https://platform.openai.com/usage
- Set usage limits in OpenAI dashboard
- Consider caching responses

---

### EMBEDDING_MODEL

**Type**: String  
**Required**: Yes  
**Default**: `text-embedding-3-large`  
**Options**: `text-embedding-3-large`, `text-embedding-3-small`, `text-embedding-ada-002`

Model for generating query embeddings for vector search.

```env
EMBEDDING_MODEL=text-embedding-3-large
```

**Comparison**:
| Model | Dimensions | Performance | Cost |
|-------|-----------|-------------|------|
| text-embedding-3-large | 3072 | Best | Higher |
| text-embedding-3-small | 1536 | Good | Lower |
| text-embedding-ada-002 | 1536 | Legacy | Lower |

**Recommendation**: Use `text-embedding-3-large` for best accuracy.

---

### QDRANT_URL

**Type**: String (URL)  
**Required**: Yes  
**Format**: `https://...`

URL of your Qdrant vector database instance.

```env
QDRANT_URL=https://abc123.cloud.qdrant.io
```

**Setup Qdrant**:
1. **Cloud** (Recommended):
   - Visit https://cloud.qdrant.io
   - Create free cluster
   - Copy cluster URL

2. **Self-Hosted**:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
   ```env
   QDRANT_URL=http://localhost:6333
   ```

**Collections Required**:
- `legaladvisor_sindh`
- `legaladvisor_punjab`
- `legaladvisor_khyber_pakhtunkhwa`
- `legaladvisor_balochistan`
- `legaladvisor_all_pakistan`

---

### QDRANT_API_KEY

**Type**: String  
**Required**: Yes (for cloud), No (for local)

API key for authenticating with Qdrant cloud.

```env
QDRANT_API_KEY=your_qdrant_api_key
```

**Get API Key**:
1. Login to Qdrant Cloud
2. Go to cluster settings
3. Copy API key

**Local Development**:
```env
# Leave empty for local Qdrant
QDRANT_API_KEY=
```

---

### DB_HOST

**Type**: String (hostname)  
**Required**: Yes

PostgreSQL database host address.

```env
DB_HOST=abc123.leapcellpool.com
```

**Examples**:
- Leapcell: `abc123.leapcellpool.com`
- AWS RDS: `mydb.abc123.us-east-1.rds.amazonaws.com`
- Heroku: `ec2-1-2-3-4.compute-1.amazonaws.com`
- Local: `localhost`

---

### DB_PORT

**Type**: Integer  
**Required**: Yes  
**Default**: `5432` (standard PostgreSQL)

PostgreSQL database port.

```env
DB_PORT=6438
```

**Common Ports**:
- Standard PostgreSQL: `5432`
- Leapcell: `6438`
- Custom: Check your provider

---

### DB_NAME

**Type**: String  
**Required**: Yes

PostgreSQL database name.

```env
DB_NAME=legaladvisor_db
```

**Tables Created**:
- `admin_users` - Admin authentication
- `admin_settings` - System settings

---

### DB_USER

**Type**: String  
**Required**: Yes

PostgreSQL database username.

```env
DB_USER=admin_user
```

**Permissions Required**:
- CREATE TABLE
- SELECT, INSERT, UPDATE, DELETE
- CREATE INDEX

---

### DB_PASSWORD

**Type**: String  
**Required**: Yes

PostgreSQL database password.

```env
DB_PASSWORD=secure_password_here
```

**Security**:
- Use strong passwords (16+ characters)
- Include uppercase, lowercase, numbers, symbols
- Never commit to version control
- Rotate regularly

---

### DB_SSLMODE

**Type**: String  
**Required**: Yes  
**Default**: `require`  
**Options**: `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full`

SSL mode for database connection.

```env
DB_SSLMODE=require
```

**Options Explained**:
- `disable` - No SSL (local only)
- `require` - SSL required (recommended for production)
- `verify-ca` - Verify certificate authority
- `verify-full` - Full certificate verification

**Recommendation**: Use `require` for production.

---

### JWT_SECRET_KEY

**Type**: String  
**Required**: Yes  
**Security**: Critical

Secret key for signing JWT tokens.

```env
JWT_SECRET_KEY=your-very-long-random-secret-key-change-this-in-production
```

**Generate Secure Key**:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# OpenSSL
openssl rand -base64 64

# Node.js
node -e "console.log(require('crypto').randomBytes(64).toString('base64'))"
```

**Security Requirements**:
- Minimum 32 characters
- Use random generation
- Never share or commit
- Rotate periodically
- Different for each environment

---

### JWT_ALGORITHM

**Type**: String  
**Required**: Yes  
**Default**: `HS256`  
**Options**: `HS256`, `HS384`, `HS512`, `RS256`

Algorithm for JWT token signing.

```env
JWT_ALGORITHM=HS256
```

**Algorithms**:
- `HS256` - HMAC SHA-256 (recommended, symmetric)
- `HS384` - HMAC SHA-384 (more secure)
- `HS512` - HMAC SHA-512 (most secure)
- `RS256` - RSA SHA-256 (asymmetric, requires key pair)

**Recommendation**: Use `HS256` for simplicity, `RS256` for distributed systems.

---

### JWT_EXPIRATION_HOURS

**Type**: Integer  
**Required**: Yes  
**Default**: `24`

Token expiration time in hours.

```env
JWT_EXPIRATION_HOURS=24
```

**Recommendations**:
- Development: `24` hours
- Production: `1-8` hours
- High security: `1` hour with refresh tokens

**Trade-offs**:
- Shorter: More secure, frequent re-login
- Longer: Better UX, less secure

---

## Environment-Specific Configurations

### Development (.env.development)

```env
ENVIRONMENT=development

# Use test/development keys
OPENAI_API_KEY=sk-test-...

# Local Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Local PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legaladvisor_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_SSLMODE=disable

# Weak key OK for dev
JWT_SECRET_KEY=dev-secret-key-not-for-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
```

### Staging (.env.staging)

```env
ENVIRONMENT=staging

# Staging OpenAI key
OPENAI_API_KEY=sk-staging-...

# Staging Qdrant
QDRANT_URL=https://staging.qdrant.io
QDRANT_API_KEY=staging_key

# Staging database
DB_HOST=staging-db.example.com
DB_PORT=5432
DB_NAME=legaladvisor_staging
DB_USER=staging_user
DB_PASSWORD=staging_secure_password
DB_SSLMODE=require

# Staging JWT
JWT_SECRET_KEY=staging-secret-key-different-from-prod
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Production (.env.production)

```env
ENVIRONMENT=production

# Production OpenAI key
OPENAI_API_KEY=sk-prod-...
EMBEDDING_MODEL=text-embedding-3-large

# Production Qdrant
QDRANT_URL=https://prod.qdrant.io
QDRANT_API_KEY=prod_secure_key

# Production database
DB_HOST=prod-db.example.com
DB_PORT=6438
DB_NAME=legaladvisor_prod
DB_USER=prod_user
DB_PASSWORD=very_secure_production_password
DB_SSLMODE=require

# Production JWT (rotate regularly)
JWT_SECRET_KEY=production-very-long-random-secret-key-64-chars-minimum
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
```

---

## Security Best Practices

### 1. Never Commit .env Files

Add to `.gitignore`:
```gitignore
.env
.env.*
!.env.example
```

### 2. Use .env.example

Create `.env.example` with dummy values:
```env
ENVIRONMENT=development
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_url_here
# ... etc
```

### 3. Rotate Secrets Regularly

- JWT_SECRET_KEY: Every 3-6 months
- Database passwords: Every 6 months
- API keys: When compromised

### 4. Use Secret Management

**Production Options**:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Environment variables in platform (Heroku, Leapcell)

### 5. Principle of Least Privilege

- Database user: Only required permissions
- API keys: Minimum required scopes
- Separate keys per environment

---

## Validation

### Check Configuration

```python
# config.py validates on startup
from config import settings

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Database: {settings.DB_NAME}")
print(f"Qdrant: {settings.QDRANT_URL}")
```

### Test Connections

```bash
# Test database
python -c "from services.database_service import database_service; database_service.init_tables()"

# Test Qdrant
curl -X GET "${QDRANT_URL}/collections" -H "api-key: ${QDRANT_API_KEY}"

# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer ${OPENAI_API_KEY}"
```

---

## Troubleshooting

### Missing Variables

**Error**: `KeyError: 'OPENAI_API_KEY'`

**Solution**: Ensure all required variables are set in `.env`

### Invalid Database Connection

**Error**: `psycopg2.OperationalError: could not connect`

**Check**:
1. DB_HOST is correct
2. DB_PORT is correct
3. DB_SSLMODE matches server config
4. Network connectivity

### Invalid OpenAI Key

**Error**: `AuthenticationError: Incorrect API key`

**Check**:
1. Key starts with `sk-`
2. No extra spaces
3. Key is active in OpenAI dashboard
4. Billing is enabled

### Qdrant Connection Failed

**Error**: `QdrantException: Connection failed`

**Check**:
1. QDRANT_URL is correct
2. QDRANT_API_KEY is valid
3. Collections exist
4. Network connectivity

---

## Loading Environment Variables

### Python (python-dotenv)

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

### Docker

```bash
docker run --env-file .env legaladvisor-api
```

### Docker Compose

```yaml
services:
  api:
    env_file:
      - .env
```

### Heroku

```bash
heroku config:set OPENAI_API_KEY=sk-...
```

### AWS

Use AWS Systems Manager Parameter Store or Secrets Manager.

---

## Quick Reference

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| ENVIRONMENT | Yes | development | production |
| OPENAI_API_KEY | Yes | - | sk-proj-... |
| EMBEDDING_MODEL | Yes | text-embedding-3-large | text-embedding-3-large |
| QDRANT_URL | Yes | - | https://abc.qdrant.io |
| QDRANT_API_KEY | Yes* | - | your_key |
| DB_HOST | Yes | - | localhost |
| DB_PORT | Yes | 5432 | 6438 |
| DB_NAME | Yes | - | legaladvisor |
| DB_USER | Yes | - | admin |
| DB_PASSWORD | Yes | - | password |
| DB_SSLMODE | Yes | require | require |
| JWT_SECRET_KEY | Yes | - | random_64_chars |
| JWT_ALGORITHM | Yes | HS256 | HS256 |
| JWT_EXPIRATION_HOURS | Yes | 24 | 24 |

*Not required for local Qdrant

---

## Next Steps

1. Copy `.env.example` to `.env`
2. Fill in all required values
3. Test configuration: `python -c "from config import settings; print('OK')"`
4. Initialize database: `python create_admin.py init`
5. Run application: `uvicorn main:app --reload`

For deployment, see [Deployment Guide](DEPLOYMENT.md).
