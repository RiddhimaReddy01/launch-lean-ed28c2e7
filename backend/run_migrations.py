#!/usr/bin/env python3
"""
Run Supabase migrations to create cache tables.
Execute from backend directory: python run_migrations.py

Note: This script requires psql (PostgreSQL CLI) installed locally.
Alternative: Use Supabase SQL Editor in dashboard.
"""

import os
import sys
import subprocess

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables.")

SUPABASE_URL = os.getenv("SUPABASE_URL")

if not SUPABASE_URL:
    print("❌ Error: SUPABASE_URL required in .env")
    sys.exit(1)

# Extract database connection string from SUPABASE_URL
# Format: https://<project-id>.supabase.co
# Database URL format: postgres://postgres:<password>@db.<project-id>.supabase.co:5432/postgres

print("=" * 70)
print("[!] SUPABASE MIGRATION SETUP")
print("=" * 70)
print(f"\n[*] Supabase Project: {SUPABASE_URL}")
print("\n[*] This script requires manual setup. Choose one option:\n")

print("OPTION 1: Use Supabase SQL Editor (Easiest)")
print("-" * 70)
print("1. Go to: https://app.supabase.com/projects")
print("2. Select your project (from URL above)")
print("3. Click 'SQL Editor' in left sidebar")
print("4. Click 'New Query'")
print("5. Copy & paste the SQL below:")
print("-" * 70)

# Read and display migration SQL
migration_file = "migrations/001_create_cache_tables.sql"
if not os.path.exists(migration_file):
    print(f"❌ Error: {migration_file} not found")
    sys.exit(1)

with open(migration_file, "r") as f:
    sql = f.read()

print("\n" + sql)
print("\n" + "-" * 70)
print("6. Click 'Run' button")
print("7. You should see 'Success' messages")
print("\n" + "=" * 70)
print("\nOPTION 2: Use psql CLI (Advanced)")
print("-" * 70)
print("Run: psql <your-database-url> < migrations/001_create_cache_tables.sql")
print("\n" + "=" * 70)
print("\n[OK] After running the migration, verify in Supabase:")
print("   - Check 'Table Editor' -> you should see 2 new tables")
print("   - decompose_cache")
print("   - discover_insights_cache")
print("\n")
