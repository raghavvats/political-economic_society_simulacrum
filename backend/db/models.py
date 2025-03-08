from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.db.database import Base
import datetime

class Demographics(Base):
    __tablename__ = 'demographics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    numerical_characteristics = Column(JSONB, nullable=False)
    categorical_characteristics = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sessions = relationship("Session", back_populates="demographic")

class Survey(Base):
    __tablename__ = 'surveys'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    questions = relationship("Question", back_populates="survey")
    sessions = relationship("Session", back_populates="survey")
    responses = relationship("Response", back_populates="survey")

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    response_type = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "response_type IN ('multiple-choice', 'free-text', 'likert')",
            name='valid_response_type'
        ),
    )
    
    survey = relationship("Survey", back_populates="questions")
    responses = relationship("Response", back_populates="question")

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False)
    demographic_id = Column(Integer, ForeignKey('demographics.id', ondelete='CASCADE'), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    survey = relationship("Survey", back_populates="sessions")
    demographic = relationship("Demographics", back_populates="sessions")
    agents = relationship("Agent", back_populates="session")
    responses = relationship("Response", back_populates="session")

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    numerical_characteristics = Column(JSONB, nullable=False)
    categorical_characteristics = Column(JSONB, nullable=False)

    __table_args__ = (
        Index('ix_agents_numerical_characteristics', numerical_characteristics, postgresql_using='gin'),
        Index('ix_agents_categorical_characteristics', categorical_characteristics, postgresql_using='gin'),
    )

    session = relationship("Session", back_populates="agents")
    responses = relationship("Response", back_populates="agent")

class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    survey_id = Column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    response = Column(Text, nullable=False)
    
    session = relationship("Session", back_populates="responses")
    agent = relationship("Agent", back_populates="responses")
    survey = relationship("Survey", back_populates="responses")
    question = relationship("Question", back_populates="responses") 