# Architecture

System architecture and design documentation.

## Overview

LegalAdvisor is a FastAPI-based multilingual legal assistant with AI-powered features.

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │  Mobile  │  │   CLI    │  │   API    │   │
│  │    UI    │  │   App    │  │  Tools   │  │ Clients  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CORS │ Auth │ Validation │ Error Handling │ Logging │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Routers    │  │   Services   │  │   Models     │
│              │  │              │  │              │
│ • unified    │  │ • chat       │  │ • pydantic   │
│ • audio      │  │ • voice      │  │ • schemas    │
│ • admin      │  │ • image      │  │ • types      │
│ • settings   │  │ • document   │  │              │
│ • health     │  │ • embedding  │  │              │
│              │  │ • qdrant     │  │              │
│              │  │ • database   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │   Qdrant     │  │  PostgreSQL  │
│              │  │              │  │              │
│ • GPT-4o     │  │ • Vector DB  │  │ • Settings   │
│ • Whisper    │  │ • Search     │  │ • Users      │
│ • TTS        │  │ • Embeddings │  │ • Auth       │
│ • Vision     │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Layers

### 1. Client Layer

**Components**:
- Web UI (HTML/JS)
- Mobile Apps (iOS/Android)
- CLI Tools (Python)
- API Clients (Any language)

**Responsibilities**:
- User interface
- Request formatting
- Response handling
- Authentication

---

### 2. API Gateway

**Framework**: FastAPI

**Components**:
- CORS middleware
- Authentication middleware
- Request validation
- Error handling
- Logging

**Responsibilities**:
- Route requests
- Validate inputs
- Handle errors
- Log activities
- Enforce security

---

### 3. Router Layer

**Routers**:

#### unified.py
- Main message endpoint
- Multi-modal input handling
- Context integration
- Response synthesis

#### audio.py
- Audio-only endpoint
- Speech-to-text
- Text-to-speech
- Audio processing

#### admin.py
- Admin authentication
- Settings management
- Token verification
- Protected endpoints

#### settings.py
- Public settings endpoint
- Settings retrieval
- Settings update

#### health.py
- Health checks
- System status
- Collection info

**Responsibilities**:
- Endpoint definition
- Request handling
- Response formatting
- Business logic coordination

---

### 4. Service Layer

**Services**:

#### multilingual_chat_service.py
- Language detection
- Chat processing
- Response generation
- Streaming support

#### voice_service.py
- Speech-to-text (Whisper)
- Text-to-speech (TTS)
- Audio processing
- Format conversion

#### image_understanding_service.py
- Image analysis (Vision)
- OCR
- Context-aware processing

#### document_reader_service.py
- PDF extraction
- DOCX extraction
- TXT extraction
- Document analysis

#### embedding_service.py
- Text embedding generation
- OpenAI embeddings
- Vector creation

#### qdrant_service.py
- Vector search
- Collection management
- Result filtering
- Score calculation

#### database_service.py
- Database connection
- Settings CRUD
- User management
- Query execution

#### query_orchestrator.py
- Search strategy
- Province detection
- Collection selection

#### web_search_service.py
- Web search
- Result enhancement
- Source attribution

#### answer_synthesis_service.py
- Answer generation
- Source integration
- Markdown formatting

#### translation_service.py
- Language detection
- Query translation
- Language mapping

**Responsibilities**:
- Business logic
- External API calls
- Data processing
- Error handling

---

### 5. Data Layer

**Databases**:

#### PostgreSQL
- Settings storage
- User management
- Authentication data

**Tables**:
```sql
admin_settings (
    id, top_k, min_score, voice, 
    tts_enabled, updated_at
)

admin_users (
    id, email, password_hash, 
    created_at, updated_at
)
```

#### Qdrant
- Vector storage
- Legal documents
- Embeddings

**Collections**:
- legaladvisor_sindh
- legaladvisor_punjab
- legaladvisor_khyber_pakhtunkhwa
- legaladvisor_balochistan
- legaladvisor_all_pakistan

---

### 6. External Services

#### OpenAI
- **GPT-4o**: Chat, analysis, synthesis
- **GPT-4o-mini**: Language detection, legal detection
- **Whisper**: Speech-to-text
- **TTS**: Text-to-speech
- **Vision**: Image analysis
- **Embeddings**: Text embeddings

#### Qdrant
- Vector database
- Similarity search
- Collection management

---

## Data Flow

### Message Processing Flow

```
User Input
    │
    ▼
┌─────────────────┐
│  Unified Router │
└─────────────────┘
    │
    ├─► Audio? ──► Speech-to-Text ──┐
    │                                │
    ├─► Image? ──► Image Analysis ──┤
    │                                │
    ├─► Document? ──► Extract Text ─┤
    │                                │
    └─────────────────────────────► │
                                     ▼
                            ┌──────────────────┐
                            │ LLM Detection    │
                            │ (Legal Query?)   │
                            └──────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
            ┌──────────────┐                 ┌──────────────┐
            │ Legal Search │                 │ Regular Chat │
            └──────────────┘                 └──────────────┘
                    │                                 │
                    ├─► Embedding                     │
                    ├─► Vector Search                 │
                    ├─► Web Enhancement               │
                    └─► Answer Synthesis              │
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
            ┌──────────────┐                 ┌──────────────┐
            │ TTS Enabled? │                 │   Response   │
            └──────────────┘                 └──────────────┘
                    │
                    ├─► Yes ──► Generate Audio
                    └─► No ───► Text Only
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Return Response │
                            └──────────────────┘
```

### Authentication Flow

```
Login Request
    │
    ▼
┌─────────────────┐
│  Admin Router   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Get User from   │
│    Database     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Verify Password │
│   (bcrypt)      │
└─────────────────┘
    │
    ├─► Valid ──► Generate JWT ──► Return Token
    │
    └─► Invalid ──► 401 Error
```

### Settings Update Flow

```
Update Request
    │
    ▼
┌─────────────────┐
│ Verify Token    │
└─────────────────┘
    │
    ├─► Valid ──┐
    │           ▼
    │   ┌─────────────────┐
    │   │ Validate Input  │
    │   └─────────────────┘
    │           │
    │           ▼
    │   ┌─────────────────┐
    │   │ Update Database │
    │   └─────────────────┘
    │           │
    │           ▼
    │   ┌─────────────────┐
    │   │ Return Settings │
    │   └─────────────────┘
    │
    └─► Invalid ──► 401 Error
```

---

## Design Patterns

### 1. Service Layer Pattern

**Purpose**: Separate business logic from routing

**Implementation**:
- Services handle business logic
- Routers handle HTTP concerns
- Clean separation of concerns

### 2. Repository Pattern

**Purpose**: Abstract data access

**Implementation**:
- Database service handles all DB operations
- Services use database service
- Easy to swap implementations

### 3. Dependency Injection

**Purpose**: Loose coupling

**Implementation**:
- FastAPI dependency injection
- Service instances created once
- Shared across requests

### 4. Factory Pattern

**Purpose**: Object creation

**Implementation**:
- Service factories
- Connection factories
- Client factories

---

## Security Architecture

### Authentication

```
┌─────────────┐
│   Client    │
└─────────────┘
      │
      │ 1. Login (email/password)
      ▼
┌─────────────┐
│    API      │
└─────────────┘
      │
      │ 2. Verify credentials
      ▼
┌─────────────┐
│  Database   │
└─────────────┘
      │
      │ 3. Generate JWT
      ▼
┌─────────────┐
│   Client    │ (Store token)
└─────────────┘
      │
      │ 4. Request with token
      ▼
┌─────────────┐
│    API      │ (Verify token)
└─────────────┘
```

### Password Security

- **Hashing**: bcrypt with salt
- **Storage**: Hashed in database
- **Verification**: Constant-time comparison

### Token Security

- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Secret**: Environment variable
- **Verification**: On each request

---

## Scalability

### Horizontal Scaling

**Stateless Design**:
- No session storage
- JWT tokens
- Database-backed settings

**Load Balancing**:
- Multiple instances
- Shared database
- Shared Qdrant

### Vertical Scaling

**Resource Optimization**:
- Async operations
- Connection pooling
- Efficient queries

### Caching Strategy

**Cacheable**:
- Settings (database)
- Embeddings (optional)
- Search results (optional)

**Cache Invalidation**:
- Settings update
- Time-based expiry

---

## Monitoring

### Logging

**Levels**:
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures

**Logged**:
- All requests
- Errors
- Admin actions
- Performance metrics

### Health Checks

**Endpoints**:
- `/api/v1/health`
- `/kaithhealthcheck`

**Checks**:
- API status
- Database connection
- Qdrant connection
- Collection availability

---

## Deployment Architecture

### Development

```
┌──────────────┐
│  Developer   │
│   Machine    │
│              │
│ • Python     │
│ • PostgreSQL │
│ • Qdrant     │
└──────────────┘
```

### Production (Leapcell)

```
┌─────────────────────────────────────┐
│          Leapcell Platform          │
│                                     │
│  ┌──────────────────────────────┐  │
│  │      FastAPI Application     │  │
│  │      (Multiple Instances)    │  │
│  └──────────────────────────────┘  │
│                │                    │
│                ▼                    │
│  ┌──────────────────────────────┐  │
│  │      Load Balancer           │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Qdrant │ │  PG    │ │ OpenAI │
│ Cloud  │ │  DB    │ │  API   │
└────────┘ └────────┘ └────────┘
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Server**: Uvicorn
- **Validation**: Pydantic

### Database
- **Primary**: PostgreSQL
- **Vector**: Qdrant
- **ORM**: psycopg2

### AI/ML
- **LLM**: OpenAI GPT-4o
- **Embeddings**: text-embedding-3-large
- **STT**: Whisper
- **TTS**: OpenAI TTS
- **Vision**: GPT-4o Vision

### Authentication
- **Tokens**: JWT
- **Hashing**: bcrypt
- **Library**: PyJWT

### Frontend
- **UI**: HTML/CSS/JavaScript
- **Icons**: Lucide
- **Styling**: Custom CSS

---

## Configuration Management

### Environment Variables

**Storage**: `.env` file

**Categories**:
- API keys
- Database credentials
- JWT configuration
- Feature flags

### Settings

**Storage**: PostgreSQL database

**Management**:
- Admin panel
- API endpoints
- CLI tools

---

## Error Handling Strategy

### Levels

1. **Service Level**: Catch and log
2. **Router Level**: Format and return
3. **Middleware Level**: Global handler

### Response Format

```json
{
  "detail": "Error message"
}
```

### Status Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 500: Server Error

---

## Future Architecture

### Planned Improvements

1. **Microservices**: Split into services
2. **Message Queue**: Async processing
3. **Redis**: Caching layer
4. **GraphQL**: Alternative API
5. **WebSocket**: Real-time updates
6. **CDN**: Static file delivery
7. **Monitoring**: Prometheus/Grafana
8. **Tracing**: OpenTelemetry
