"""
Database setup and initialization script for CreatorHub.ai
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base, engine
from app.models.user import User

logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    from urllib.parse import urlparse
    parsed_url = urlparse(settings.DATABASE_URL)
    db_name = parsed_url.path[1:]  # Remove leading slash

    # Create connection without database name
    engine_url = settings.DATABASE_URL.replace(f"/{db_name}", "/postgres")
    temp_engine = create_engine(engine_url)

    try:
        with temp_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )

            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))  # End any transaction
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"✅ Database '{db_name}' created successfully")
            else:
                logger.info(f"✅ Database '{db_name}' already exists")

    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        raise
    finally:
        temp_engine.dispose()

def create_tables():
    """Create all database tables"""
    try:
        logger.info("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully")

        # Verify tables were created
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)).fetchall()

            table_names = [table[0] for table in tables]
            logger.info(f"📋 Created tables: {', '.join(table_names)}")

    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

def create_indexes():
    """Create database indexes for better performance"""
    try:
        logger.info("🔧 Creating database indexes...")
        with engine.connect() as conn:
            # User indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_subscription_plan ON users(subscription_plan)"))

            # Content indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_content_user_id ON generated_content(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_content_type ON generated_content(content_type)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_content_created_at ON generated_content(created_at)"))

            # Analytics indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics_data(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_data(date)"))

            # Brand deals indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_deals_user_id ON brand_deals(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_deals_status ON brand_deals(status)"))

            conn.commit()
            logger.info("✅ Database indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        raise

def seed_initial_data():
    """Seed the database with initial data"""
    try:
        logger.info("🌱 Seeding initial data...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@creatorhub.ai").first()

        if not admin_user:
            from app.core.security import get_password_hash

            admin_user = User(
                email="admin@creatorhub.ai",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_verified=True,
                subscription_plan="enterprise"
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ Admin user created")
        else:
            logger.info("✅ Admin user already exists")

        db.close()

    except Exception as e:
        logger.error(f"❌ Error seeding data: {e}")
        raise

def setup_database():
    """Main database setup function"""
    try:
        logger.info("🚀 Starting database setup...")

        # Step 1: Create database if it doesn't exist
        create_database_if_not_exists()

        # Step 2: Create all tables
        create_tables()

        # Step 3: Create indexes for performance
        create_indexes()

        # Step 4: Seed initial data
        seed_initial_data()

        logger.info("🎉 Database setup completed successfully!")

    except Exception as e:
        logger.error(f"💥 Database setup failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_database()
