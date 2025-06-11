"""
Create chatbot tables in Supabase database
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from database import VoiceDatabase

def create_chatbot_tables():
    """Create the chatbot tables in Supabase"""
    try:
        print("Connecting to Supabase database...")
        db = VoiceDatabase()
        
        # Read the SQL script
        sql_file_path = Path(__file__).parent / "sql" / "create_chatbot_tables.sql"
        
        if not sql_file_path.exists():
            print(f"Error: SQL file not found at {sql_file_path}")
            return False
        
        print(f"Reading SQL script from {sql_file_path}")
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    print(f"Executing statement {i}/{len(statements)}...")
                    result = db.client.query(statement + ';').execute()
                    print(f"✓ Statement {i} executed successfully")
                except Exception as e:
                    print(f"✗ Error executing statement {i}: {str(e)}")
                    print(f"Statement: {statement[:100]}...")
                    if "already exists" not in str(e).lower():
                        return False
        
        print("\n✅ All chatbot tables created successfully!")
        
        # Test the tables by listing them
        print("\nTesting table creation...")
        test_queries = [
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('conversations', 'messages', 'audio_transcripts')",
        ]
        
        for query in test_queries:
            try:
                result = db.client.query(query).execute()
                tables = [row['table_name'] for row in result.data]
                print(f"✓ Found tables: {tables}")
            except Exception as e:
                print(f"✗ Error testing tables: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating chatbot tables: {e}")
        return False

if __name__ == "__main__":
    success = create_chatbot_tables()
    if success:
        print("\n🎉 Chatbot database setup completed successfully!")
    else:
        print("\n❌ Chatbot database setup failed!")
        sys.exit(1)
