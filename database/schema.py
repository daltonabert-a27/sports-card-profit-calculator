"""Database schema creation and seeding."""

import sqlite3

from config.defaults import (
    DEFAULT_FEE_PROFILES,
    DEFAULT_GRADING_SERVICES,
    DEFAULT_SHIPPING_OPTIONS,
)

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS cards (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id         TEXT UNIQUE NOT NULL,
        description     TEXT NOT NULL,
        year            INTEGER,
        set_name        TEXT,
        player_name     TEXT,
        card_number     TEXT,
        parallel        TEXT,
        sport           TEXT DEFAULT 'Basketball',
        is_graded       INTEGER DEFAULT 0,
        grading_company TEXT,
        grade           TEXT,
        status          TEXT DEFAULT 'Inventory',
        notes           TEXT,
        created_at      TEXT DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id         TEXT NOT NULL REFERENCES cards(card_id),
        purchase_date   TEXT NOT NULL,
        purchase_price  REAL NOT NULL,
        sales_tax_paid  REAL DEFAULT 0.0,
        shipping_paid   REAL DEFAULT 0.0,
        grading_cost    REAL DEFAULT 0.0,
        grading_company TEXT,
        grading_tier    TEXT,
        source          TEXT,
        total_cost_basis REAL GENERATED ALWAYS AS (
            purchase_price + sales_tax_paid + shipping_paid + grading_cost
        ) STORED,
        notes           TEXT,
        created_at      TEXT DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sales (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id             TEXT NOT NULL REFERENCES cards(card_id),
        sale_date           TEXT NOT NULL,
        sale_price          REAL NOT NULL,
        shipping_charged    REAL DEFAULT 0.0,
        shipping_cost       REAL DEFAULT 0.0,
        shipping_method     TEXT,
        ebay_fvf_rate       REAL DEFAULT 0.1325,
        ebay_fvf_amount     REAL,
        ebay_per_order_fee  REAL DEFAULT 0.30,
        ebay_intl_fee_rate  REAL DEFAULT 0.0,
        ebay_intl_fee_amount REAL DEFAULT 0.0,
        total_fees          REAL,
        net_proceeds        REAL,
        platform            TEXT DEFAULT 'eBay',
        buyer_state         TEXT,
        notes               TEXT,
        created_at          TEXT DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS comps (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        search_query    TEXT NOT NULL,
        card_id         TEXT REFERENCES cards(card_id),
        title           TEXT NOT NULL,
        sold_price      REAL NOT NULL,
        shipping_price  REAL DEFAULT 0.0,
        sold_date       TEXT,
        condition       TEXT,
        item_url        TEXT,
        source          TEXT DEFAULT 'manual',
        fetched_at      TEXT DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS grading_services (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        company         TEXT NOT NULL,
        tier_name       TEXT NOT NULL,
        cost_per_card   REAL NOT NULL,
        turnaround_days INTEGER,
        max_declared_value REAL,
        is_active       INTEGER DEFAULT 1,
        UNIQUE(company, tier_name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fee_profiles (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_name        TEXT UNIQUE NOT NULL,
        platform            TEXT DEFAULT 'eBay',
        fvf_rate            REAL NOT NULL,
        fvf_cap_amount      REAL DEFAULT 7500.0,
        fvf_rate_above_cap  REAL DEFAULT 0.0235,
        per_order_fee_low   REAL DEFAULT 0.30,
        per_order_fee_high  REAL DEFAULT 0.40,
        per_order_threshold REAL DEFAULT 10.0,
        intl_fee_rate       REAL DEFAULT 0.0165,
        is_default          INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS shipping_options (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        method_name     TEXT UNIQUE NOT NULL,
        carrier         TEXT NOT NULL,
        cost            REAL NOT NULL,
        max_weight_oz   REAL,
        max_value       REAL,
        graded_eligible INTEGER DEFAULT 1,
        notes           TEXT,
        is_active       INTEGER DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS settings (
        key     TEXT PRIMARY KEY,
        value   TEXT NOT NULL
    )
    """,
]


def initialize_database(conn: sqlite3.Connection):
    """Create all tables and seed default data."""
    cursor = conn.cursor()

    for table_sql in TABLES:
        cursor.execute(table_sql)

    # Seed grading services
    for gs in DEFAULT_GRADING_SERVICES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO grading_services
                (company, tier_name, cost_per_card, turnaround_days, max_declared_value)
            VALUES (?, ?, ?, ?, ?)
            """,
            (gs["company"], gs["tier"], gs["cost"], gs["days"], gs["max_value"]),
        )

    # Seed shipping options
    for so in DEFAULT_SHIPPING_OPTIONS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO shipping_options
                (method_name, carrier, cost, max_weight_oz, max_value, graded_eligible, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                so["method_name"],
                so["carrier"],
                so["cost"],
                so["max_weight_oz"],
                so["max_value"],
                int(so["graded_eligible"]),
                so["notes"],
            ),
        )

    # Seed fee profiles
    for fp in DEFAULT_FEE_PROFILES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO fee_profiles
                (profile_name, platform, fvf_rate, fvf_cap_amount, fvf_rate_above_cap,
                 per_order_fee_low, per_order_fee_high, per_order_threshold,
                 intl_fee_rate, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fp["profile_name"],
                fp["platform"],
                fp["fvf_rate"],
                fp["fvf_cap_amount"],
                fp["fvf_rate_above_cap"],
                fp["per_order_fee_low"],
                fp["per_order_fee_high"],
                fp["per_order_threshold"],
                fp["intl_fee_rate"],
                int(fp["is_default"]),
            ),
        )

    conn.commit()
