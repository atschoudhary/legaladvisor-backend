import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.connection_string = f"host={settings.DB_HOST} port={settings.DB_PORT} dbname={settings.DB_NAME} user={settings.DB_USER} password={settings.DB_PASSWORD} sslmode={settings.DB_SSLMODE}"
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.connection_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def init_tables(self):
        """Initialize database tables"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Create settings table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id SERIAL PRIMARY KEY,
                    top_k INTEGER DEFAULT 5,
                    min_score FLOAT DEFAULT 0.5,
                    voice VARCHAR(50) DEFAULT 'alloy',
                    tts_enabled BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create admin users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default settings if not exists
            cur.execute("SELECT COUNT(*) FROM admin_settings")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute("""
                    INSERT INTO admin_settings (top_k, min_score, voice, tts_enabled)
                    VALUES (5, 0.5, 'alloy', FALSE)
                """)
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize tables: {e}")
            raise
    
    def get_settings(self):
        """Get admin settings from database"""
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("SELECT top_k, min_score, voice, tts_enabled FROM admin_settings ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if result:
                return dict(result)
            else:
                return {
                    "top_k": 5,
                    "min_score": 0.5,
                    "voice": "alloy",
                    "tts_enabled": False
                }
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            # Return defaults on error
            return {
                "top_k": 5,
                "min_score": 0.5,
                "voice": "alloy",
                "tts_enabled": False
            }
    
    def update_settings(self, top_k=None, min_score=None, voice=None, tts_enabled=None):
        """Update admin settings in database"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Get current settings
            cur.execute("SELECT id FROM admin_settings ORDER BY id DESC LIMIT 1")
            result = cur.fetchone()
            
            if result:
                # Update existing
                settings_id = result[0]
                updates = []
                params = []
                
                if top_k is not None:
                    updates.append("top_k = %s")
                    params.append(top_k)
                if min_score is not None:
                    updates.append("min_score = %s")
                    params.append(min_score)
                if voice is not None:
                    updates.append("voice = %s")
                    params.append(voice)
                if tts_enabled is not None:
                    updates.append("tts_enabled = %s")
                    params.append(tts_enabled)
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(settings_id)
                
                query = f"UPDATE admin_settings SET {', '.join(updates)} WHERE id = %s"
                cur.execute(query, params)
            else:
                # Insert new
                cur.execute("""
                    INSERT INTO admin_settings (top_k, min_score, voice, tts_enabled)
                    VALUES (%s, %s, %s, %s)
                """, (
                    top_k or 5,
                    min_score or 0.5,
                    voice or 'alloy',
                    tts_enabled or False
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("Settings updated successfully")
            return self.get_settings()
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            raise

database_service = DatabaseService()
