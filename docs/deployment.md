# Deployment Guide

Complete guide for deploying LegalAdvisor API to production.

## Deployment Platforms

### Leapcell (Current Production)

**Production URL**: https://legaladvisor-backend-ats1563-fcq5tdhe.leapcell.dev

#### Prerequisites
- Leapcell account
- PostgreSQL database
- Qdrant vector database
- OpenAI API key

#### Configuration

1. **Environment Variables**
   Set all required environment variables in Leapcell dashboard:
   ```env
   ENVIRONMENT=production
   OPENAI_API_KEY=your_key
   QDRANT_URL=your_url
   QDRANT_API_KEY=your_key
   DB_HOST=your_host
   DB_PORT=6438
   DB_NAME=your_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_SSLMODE=require
   JWT_SECRET_KEY=your_secret
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ```

2. **Port Configuration**
   - Application must listen on port **8080**
   - Leapcell requires `/kaithhealthcheck` endpoint
   - Already configured in `main.py`

3. **Database Setup**
   ```bash
   # Run locally to initialize database
   python create_admin.py init
   python create_admin.py create
   ```

4. **Deploy**
   - Push code to repository
   - Leapcell auto-deploys on push
   - Monitor logs for startup

#### Health Check

Leapcell checks these endpoints:
- `GET /kaithhealthcheck` - Platform health check
- `GET /api/v1/health` - API health check

Both must respond within 9800ms.

#### Troubleshooting

**Connection Failed Error**:
```
[Connection Failed] Could not connect to the application server at http://127.0.0.1:8080/kaithheathcheck
```

Solutions:
1. Verify app listens on port 8080
2. Check `/kaithhealthcheck` endpoint exists
3. Ensure response time < 9800ms
4. Check logs for startup errors

**Database Connection Issues**:
- Verify SSL mode is `require`
- Check database credentials
- Ensure network connectivity
- Verify database is initialized

---

## Alternative Platforms

### Heroku

#### Setup
```bash
# Install Heroku CLI
heroku login

# Create app
heroku create legaladvisor-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set QDRANT_URL=your_url
# ... set all other variables

# Deploy
git push heroku main
```

#### Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Initialize Database
```bash
heroku run python create_admin.py init
heroku run python create_admin.py create
```

---

### AWS (EC2 + RDS)

#### EC2 Setup
```bash
# SSH into EC2
ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone repository
git clone <repo-url>
cd backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# Add all environment variables

# Initialize database
python create_admin.py init
python create_admin.py create
```

#### Systemd Service
Create `/etc/systemd/system/legaladvisor.service`:
```ini
[Unit]
Description=LegalAdvisor API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
Environment="PATH=/home/ubuntu/backend/venv/bin"
ExecStart=/home/ubuntu/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable legaladvisor
sudo systemctl start legaladvisor
sudo systemctl status legaladvisor
```

#### Nginx Configuration
Create `/etc/nginx/sites-available/legaladvisor`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/legaladvisor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_SSLMODE=${DB_SSLMODE}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=legaladvisor
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Build and Run
```bash
# Build
docker build -t legaladvisor-api .

# Run
docker run -p 8080:8080 --env-file .env legaladvisor-api

# Or with docker-compose
docker-compose up -d
```

---

## Production Checklist

### Security
- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Use HTTPS/SSL in production
- [ ] Configure CORS for specific origins
- [ ] Enable rate limiting
- [ ] Set secure password policies
- [ ] Regular security audits

### Database
- [ ] Initialize database tables
- [ ] Create admin user
- [ ] Setup database backups
- [ ] Configure connection pooling
- [ ] Monitor database performance

### Monitoring
- [ ] Setup logging (CloudWatch, Datadog, etc.)
- [ ] Configure error tracking (Sentry)
- [ ] Setup uptime monitoring
- [ ] Monitor API response times
- [ ] Track API usage metrics

### Performance
- [ ] Enable caching where appropriate
- [ ] Optimize database queries
- [ ] Configure connection pooling
- [ ] Setup CDN for static files
- [ ] Load testing

### Backup & Recovery
- [ ] Database backup strategy
- [ ] Environment variables backup
- [ ] Disaster recovery plan
- [ ] Regular backup testing

---

## Environment-Specific Configuration

### Development
```python
# config.py
ENVIRONMENT = "development"
DEBUG = True
RELOAD = True
```

### Staging
```python
ENVIRONMENT = "staging"
DEBUG = True
RELOAD = False
```

### Production
```python
ENVIRONMENT = "production"
DEBUG = False
RELOAD = False
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (AWS ALB, Nginx)
- Multiple API instances
- Shared database and Qdrant
- Session management with JWT (stateless)

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Enable caching
- Use async operations

### Database Scaling
- Read replicas for queries
- Connection pooling
- Query optimization
- Indexing

---

## Monitoring & Logging

### Application Logs
```python
# Already configured in main.py
import logging
logging.basicConfig(level=logging.INFO)
```

### Health Monitoring
```bash
# Check health endpoint
curl https://your-domain.com/api/v1/health

# Check Leapcell health
curl https://your-domain.com/kaithhealthcheck
```

### Error Tracking
Consider integrating:
- Sentry for error tracking
- CloudWatch for AWS
- Datadog for metrics
- New Relic for APM

---

## Rollback Strategy

### Quick Rollback
```bash
# Heroku
heroku rollback

# Git-based
git revert HEAD
git push origin main

# Docker
docker pull legaladvisor-api:previous-tag
docker-compose up -d
```

### Database Rollback
```bash
# Restore from backup
pg_restore -d legaladvisor backup.sql
```

---

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Review and rotate API keys quarterly
- Database maintenance (VACUUM, ANALYZE)
- Log rotation and cleanup
- Security patches

### Backup Schedule
- Database: Daily automated backups
- Environment config: Weekly
- Code: Git repository

---

## Support & Troubleshooting

### Common Issues

**High Response Times**:
- Check database connection pool
- Monitor Qdrant performance
- Review OpenAI API latency
- Check network connectivity

**Memory Issues**:
- Monitor application memory usage
- Check for memory leaks
- Optimize file uploads
- Configure proper limits

**Database Connection Errors**:
- Check connection pool settings
- Verify credentials
- Check SSL configuration
- Monitor connection count

### Getting Help
- Check logs first
- Review [API Reference](API_REFERENCE.md)
- Check [Architecture](ARCHITECTURE.md)
- Create GitHub issue

---

## Version History

**v2.0.0** (April 2026)
- Unified endpoint
- LLM-based detection
- Audio mode
- Admin system
- Database integration

**v1.0.0** (Initial Release)
- Basic multilingual chat
- Document reader
- Voice support
- Image understanding

---

## Next Steps

After deployment:
1. Test all endpoints
2. Create admin user
3. Configure settings
4. Monitor logs
5. Setup monitoring
6. Document any custom configuration

For detailed API usage, see [API Reference](API_REFERENCE.md).
