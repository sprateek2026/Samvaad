import sqlite3
import os
from .config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        -- Users
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firebase_uid TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            pin_code TEXT NOT NULL,
            address TEXT,
            city TEXT DEFAULT 'Pune',
            state TEXT DEFAULT 'Maharashtra',
            latitude REAL,
            longitude REAL,
            role TEXT CHECK(role IN ('citizen','corporator','admin')) DEFAULT 'citizen',
            ward_id INTEGER,
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ward_id) REFERENCES wards(id)
        );

        -- Wards
        CREATE TABLE IF NOT EXISTS wards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward_number INTEGER UNIQUE NOT NULL,
            ward_name TEXT NOT NULL,
            ward_name_mr TEXT,
            corporator_a_name TEXT,
            corporator_a_party TEXT,
            corporator_b_name TEXT,
            corporator_b_party TEXT,
            corporator_c_name TEXT,
            corporator_c_party TEXT,
            corporator_d_name TEXT,
            corporator_d_party TEXT,
            mla_name TEXT,
            mla_constituency TEXT,
            mla_party TEXT,
            mp_name TEXT,
            mp_constituency TEXT,
            mp_party TEXT,
            geometry TEXT
        );

        -- Complaint Categories
        CREATE TABLE IF NOT EXISTS complaint_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_mr TEXT,
            name_hi TEXT,
            routing_level TEXT CHECK(routing_level IN ('corporator','mla','mp')) NOT NULL,
            sla_hours INTEGER DEFAULT 168,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Complaints
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            citizen_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            description_mr TEXT,
            description_hi TEXT,
            location_lat REAL,
            location_lng REAL,
            location_address TEXT,
            ward_id INTEGER,
            assigned_to INTEGER,
            status TEXT CHECK(status IN (
                'submitted','under_review','assigned','in_progress',
                'escalated','resolved','closed','reopened'
            )) DEFAULT 'submitted',
            priority TEXT CHECK(priority IN ('low','medium','high','urgent')) DEFAULT 'medium',
            ai_category TEXT,
            ai_confidence REAL,
            ai_method TEXT,
            is_duplicate INTEGER DEFAULT 0,
            duplicate_of_id INTEGER,
            sla_deadline TIMESTAMP,
            resolved_at TIMESTAMP,
            citizen_rating INTEGER CHECK(citizen_rating BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (citizen_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES complaint_categories(id),
            FOREIGN KEY (ward_id) REFERENCES wards(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (duplicate_of_id) REFERENCES complaints(id)
        );

        -- Complaint Images
        CREATE TABLE IF NOT EXISTS complaint_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            original_name TEXT,
            mime_type TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
        );

        -- Complaint Status Log
        CREATE TABLE IF NOT EXISTS complaint_status_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            from_status TEXT,
            to_status TEXT NOT NULL,
            changed_by INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id),
            FOREIGN KEY (changed_by) REFERENCES users(id)
        );

        -- Notifications
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            complaint_id INTEGER,
            type TEXT CHECK(type IN ('status_update','escalation','new_complaint','sla_breach','general')),
            title TEXT NOT NULL,
            title_mr TEXT,
            title_hi TEXT,
            message TEXT NOT NULL,
            message_mr TEXT,
            message_hi TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        );

        -- Representative Mapping
        CREATE TABLE IF NOT EXISTS representative_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward_id INTEGER NOT NULL UNIQUE,
            corporator_a_id INTEGER,
            mla_name TEXT NOT NULL,
            mla_constituency TEXT NOT NULL,
            mla_party TEXT,
            mp_name TEXT NOT NULL,
            mp_constituency TEXT NOT NULL,
            mp_party TEXT,
            FOREIGN KEY (ward_id) REFERENCES wards(id),
            FOREIGN KEY (corporator_a_id) REFERENCES users(id)
        );

        -- PIN Code Ward Mapping
        CREATE TABLE IF NOT EXISTS pincode_ward_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin_code TEXT NOT NULL,
            ward_id INTEGER NOT NULL,
            locality TEXT,
            FOREIGN KEY (ward_id) REFERENCES wards(id)
        );
        CREATE INDEX IF NOT EXISTS idx_pincode ON pincode_ward_mapping(pin_code);

        -- Audit Log
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Complaint Sub-Categories
        CREATE TABLE IF NOT EXISTS complaint_sub_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            name_mr TEXT,
            name_hi TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES complaint_categories(id)
        );

        -- Suggestions
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_id INTEGER NOT NULL,
            ward_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (citizen_id) REFERENCES users(id),
            FOREIGN KEY (ward_id) REFERENCES wards(id)
        );

        -- Complaint ID sequence
        CREATE TABLE IF NOT EXISTS complaint_id_seq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            seq INTEGER DEFAULT 0
        );

        -- Representatives (admin-managed Corporator/MLA/MP entries with photos)
        CREATE TABLE IF NOT EXISTS representatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('corporator', 'mla', 'mp')),
            name TEXT NOT NULL,
            party TEXT,
            constituency TEXT,
            photo_path TEXT,
            user_id INTEGER,
            label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ward_id) REFERENCES wards(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # Migrate existing table — drop the old UNIQUE(ward_id, type) constraint
    # SQLite cannot ALTER to drop constraints, so rebuild the table
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='representatives'")
    row = cur.fetchone()
    if row and 'UNIQUE(ward_id, type)' in row[0]:
        cur.executescript("""
            CREATE TABLE representatives_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ward_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('corporator', 'mla', 'mp')),
                name TEXT NOT NULL,
                party TEXT,
                constituency TEXT,
                photo_path TEXT,
                user_id INTEGER,
                label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ward_id) REFERENCES wards(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            INSERT INTO representatives_new (id, ward_id, type, name, party, constituency, photo_path, user_id, label, created_at, updated_at)
                SELECT id, ward_id, type, name, party, constituency, photo_path, user_id, label, created_at, updated_at FROM representatives;
            DROP TABLE representatives;
            ALTER TABLE representatives_new RENAME TO representatives;
        """)

    # Add label column to representatives for corporator slots (A/B/C/D)
    try:
        cur.execute("ALTER TABLE representatives ADD COLUMN label TEXT")
    except sqlite3.OperationalError:
        pass

    # Add sub_category_id to complaints if missing
    try:
        cur.execute("ALTER TABLE complaints ADD COLUMN sub_category_id INTEGER REFERENCES complaint_sub_categories(id)")
    except sqlite3.OperationalError:
        pass

    # Add KYC columns to representatives for Know Your Corporator
    for col in ["contact", "bio", "term", "achievements"]:
        try:
            cur.execute(f"ALTER TABLE representatives ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
