import asyncpg
from sqlalchemy.engine.url import make_url
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def create_async_database():
    url = make_url(DATABASE_URL)
    
    conn_params = {
        "host": url.host,
        "port": url.port,
        "user": url.username,
        "password": url.password,
        "database": "postgres"
    }
    
    try:
        conn = await asyncpg.connect(**conn_params)
        
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            url.database
        )
        
        if not db_exists:
            await conn.execute(
                f"CREATE DATABASE {url.database} ENCODING 'UTF8'"
            )
            print(f"БД {url.database} создана")
        else:
            print(f"БД {url.database} уже существует")
            
    except asyncpg.PostgresError as e:
        print(f"Ошибка PostgreSQL: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_async_database())