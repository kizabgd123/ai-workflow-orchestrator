import uuid
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class MeeseeksSession(Base):
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True)
    task_objective = Column(Text)
    status = Column(String, default="active") # active, fulfilled, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

class Iteration(Base):
    __tablename__ = 'iterations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    iteration_number = Column(Integer)
    plan = Column(Text)
    code_changes = Column(Text)
    test_results = Column(Text)
    reflection = Column(Text)
    is_success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LoopController:
    def __init__(self, db_url="sqlite:///storage/meeseeks.db"):
        from sqlalchemy import create_engine
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def start_session(self, objective: str) -> str:
        session_id = str(uuid.uuid4())
        with self.Session() as db:
            new_session = MeeseeksSession(id=session_id, task_objective=objective)
            db.add(new_session)
            db.commit()
        return session_id

    def log_iteration(self, session_id: str, iteration_data: dict):
        with self.Session() as db:
            new_iter = Iteration(
                session_id=session_id,
                iteration_number=iteration_data.get('number'),
                plan=iteration_data.get('plan'),
                code_changes=iteration_data.get('code'),
                test_results=iteration_data.get('test'),
                reflection=iteration_data.get('reflection'),
                is_success=iteration_data.get('success', False)
            )
            db.add(new_iter)
            db.commit()

    def complete_session(self, session_id: str):
        with self.Session() as db:
            session = db.query(MeeseeksSession).filter(MeeseeksSession.id == session_id).first()
            if session:
                session.status = "fulfilled"
                session.finished_at = datetime.datetime.utcnow()
                db.commit()
        print(f"Meeseeks Task {session_id} Fulfilled. Existence is pain! Goodbye! 💨")
