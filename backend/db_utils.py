
from sqlalchemy import create_engine, Table, MetaData, insert, select
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

def log_move(table_name, move_data):
    metadata.reflect(bind=engine)
    table = Table(table_name, metadata, autoload_with=engine)
    with engine.connect() as conn:
        stmt = insert(table).values(**move_data)
        conn.execute(stmt)
        conn.commit()

def get_case(case_id):
    metadata.reflect(bind=engine)
    cases = Table("cases", metadata, autoload_with=engine)
    with engine.connect() as conn:
        stmt = select(cases).where(cases.c.id == case_id)
        result = conn.execute(stmt).fetchone()
        return dict(result) if result else None
