#!/usr/bin/env python3
"""
Admin User Management Script
Creates or updates admin user credentials in the database
"""

import psycopg2
import bcrypt
import sys
import getpass
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6438")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

def get_connection():
    """Get database connection"""
    connection_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} sslmode={DB_SSLMODE}"
    return psycopg2.connect(connection_string)

def init_admin_table():
    """Create admin users table if not exists"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Admin users table initialized")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin(email: str, password: str):
    """Create new admin user"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if email already exists
    cur.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
    existing = cur.fetchone()
    
    if existing:
        print(f"✗ Admin with email '{email}' already exists")
        print("  Use update command to change password")
        cur.close()
        conn.close()
        return False
    
    # Hash password
    password_hash = hash_password(password)
    
    # Insert admin
    cur.execute("""
        INSERT INTO admin_users (email, password_hash)
        VALUES (%s, %s)
    """, (email, password_hash))
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✓ Admin user created successfully")
    print(f"  Email: {email}")
    return True

def update_admin_password(email: str, new_password: str):
    """Update admin password"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if admin exists
    cur.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
    existing = cur.fetchone()
    
    if not existing:
        print(f"✗ Admin with email '{email}' not found")
        cur.close()
        conn.close()
        return False
    
    # Hash new password
    password_hash = hash_password(new_password)
    
    # Update password
    cur.execute("""
        UPDATE admin_users 
        SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
        WHERE email = %s
    """, (password_hash, email))
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✓ Password updated successfully for {email}")
    return True

def list_admins():
    """List all admin users"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, created_at, updated_at FROM admin_users ORDER BY id")
    admins = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not admins:
        print("No admin users found")
        return
    
    print("\nAdmin Users:")
    print("-" * 80)
    print(f"{'ID':<5} {'Email':<40} {'Created':<20} {'Updated':<20}")
    print("-" * 80)
    
    for admin in admins:
        admin_id, email, created_at, updated_at = admin
        print(f"{admin_id:<5} {email:<40} {str(created_at):<20} {str(updated_at):<20}")
    
    print("-" * 80)

def delete_admin(email: str):
    """Delete admin user"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if admin exists
    cur.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
    existing = cur.fetchone()
    
    if not existing:
        print(f"✗ Admin with email '{email}' not found")
        cur.close()
        conn.close()
        return False
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete admin '{email}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled")
        cur.close()
        conn.close()
        return False
    
    # Delete admin
    cur.execute("DELETE FROM admin_users WHERE email = %s", (email,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✓ Admin user '{email}' deleted successfully")
    return True

def interactive_create():
    """Interactive admin creation"""
    print("\n=== Create New Admin User ===\n")
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("✗ Email cannot be empty")
        return
    
    password = getpass.getpass("Enter password: ")
    if not password:
        print("✗ Password cannot be empty")
        return
    
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("✗ Passwords do not match")
        return
    
    if len(password) < 8:
        print("✗ Password must be at least 8 characters")
        return
    
    create_admin(email, password)

def interactive_update():
    """Interactive password update"""
    print("\n=== Update Admin Password ===\n")
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("✗ Email cannot be empty")
        return
    
    new_password = getpass.getpass("Enter new password: ")
    if not new_password:
        print("✗ Password cannot be empty")
        return
    
    password_confirm = getpass.getpass("Confirm new password: ")
    if new_password != password_confirm:
        print("✗ Passwords do not match")
        return
    
    if len(new_password) < 8:
        print("✗ Password must be at least 8 characters")
        return
    
    update_admin_password(email, new_password)

def print_usage():
    """Print usage instructions"""
    print("""
Admin User Management Script

Usage:
    python create_admin.py <command> [options]

Commands:
    init                Initialize admin users table
    create              Create new admin user (interactive)
    update              Update admin password (interactive)
    list                List all admin users
    delete <email>      Delete admin user
    help                Show this help message

Examples:
    python create_admin.py init
    python create_admin.py create
    python create_admin.py update
    python create_admin.py list
    python create_admin.py delete admin@example.com
""")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "init":
            init_admin_table()
        
        elif command == "create":
            init_admin_table()  # Ensure table exists
            interactive_create()
        
        elif command == "update":
            interactive_update()
        
        elif command == "list":
            list_admins()
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("✗ Please provide email address")
                print("Usage: python create_admin.py delete <email>")
                return
            email = sys.argv[2]
            delete_admin(email)
        
        elif command == "help":
            print_usage()
        
        else:
            print(f"✗ Unknown command: {command}")
            print_usage()
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
