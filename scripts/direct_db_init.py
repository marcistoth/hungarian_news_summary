import os
import asyncio
from dotenv import load_dotenv
import asyncpg

# Load environment variables from root .env file
load_dotenv()

# Get the database URL from the environment variable
db_url = os.getenv("DATABASE_URL")

async def create_tables():
    """Create database tables directly using asyncpg."""
    print(f"Using DATABASE_URL: {db_url}")
    
    if not db_url:
        print("Error: DATABASE_URL not set in environment")
        return
    
    # PostgreSQL connection URL format: postgresql://user:password@host:port/dbname
    # Extract connection parameters from URL
    user_pass, host_db = db_url.replace("postgresql://", "").split("@")
    user, password = user_pass.split(":")
    
    if "/" in host_db:
        host_port, dbname = host_db.split("/", 1)
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host, port = host_port, "5432"
    else:
        print("Invalid database URL format")
        return
    
    # Remove any query parameters from dbname
    if "?" in dbname:
        dbname = dbname.split("?")[0]
    
    print(f"Connecting to database: {dbname} on host: {host}")
    
    # Create connection
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=dbname,
        host=host,
        port=port
    )
    
    # Create the tables
    print("Creating tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS summaries (
        id SERIAL PRIMARY KEY,
        domain VARCHAR(255) NOT NULL,
        language VARCHAR(5) NOT NULL,
        date DATE NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS scraped_articles (
        id SERIAL PRIMARY KEY,
        url VARCHAR(512) NOT NULL,
        domain VARCHAR(255) NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        publication_date DATE,
        scraped_at TIMESTAMP NOT NULL
    )
    ''')
    
    print("Database tables created successfully!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())