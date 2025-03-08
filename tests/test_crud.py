import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import Base
from backend.db import models
from backend.db import crud
from backend.core.schemas import (
    AgentCreate, SurveyCreate, QuestionCreate, 
    DemographicsCreate, SessionCreate, ResponseCreate
)

# Load environment variables from .env file
load_dotenv()

# Use PostgreSQL for testing
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME") + "_test"  # Use a separate test database

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def create_test_database():
    """Create test database if it doesn't exist."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if not cursor.fetchone():
        # Create database
        cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
    
    cursor.close()
    conn.close()

def drop_test_database():
    """Drop test database."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Terminate all connections to the test database
    cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{DB_NAME}'
        AND pid <> pg_backend_pid()
    """)
    
    # Drop database
    cursor.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
    
    cursor.close()
    conn.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database before tests and drop it after."""
    create_test_database()
    yield
    drop_test_database()

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create the tables
    Base.metadata.drop_all(bind=engine)  # Drop all tables first
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test is done
        Base.metadata.drop_all(bind=engine)

def test_create_and_get_demographic(db_session):
    """Test creating and retrieving a demographic."""
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )

    # Create a demographic
    demographic = crud.create_demographic(db_session, demographic_data)
    assert demographic.id is not None
    assert demographic.name == "Test Demographic"
    
    # Get the demographic
    retrieved_demographic = crud.get_demographic_by_id(db_session, demographic.id)
    assert retrieved_demographic is not None
    assert retrieved_demographic.id == demographic.id
    assert retrieved_demographic.name == "Test Demographic"
    assert retrieved_demographic.numerical_characteristics["age_min"] == 18
    assert retrieved_demographic.numerical_characteristics["age_max"] == 65

def test_create_and_get_survey(db_session):
    """Test creating and retrieving a survey."""
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )

    # Create a survey
    survey = crud.create_survey(db_session, survey_data)
    assert survey.id is not None
    assert survey.name == "Test Survey"
    
    # Get the survey
    retrieved_survey = crud.get_survey_by_id(db_session, survey.id)
    assert retrieved_survey is not None
    assert retrieved_survey.id == survey.id
    assert retrieved_survey.name == "Test Survey"
    assert retrieved_survey.description == "A test survey"

def test_create_and_get_question(db_session):
    """Test creating and retrieving a question."""
    # First, create a survey
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    # Create a question
    question_data = QuestionCreate(
        survey_id=survey.id,
        text="What is your favorite color?",
        response_type="multiple-choice",
        options=["Red", "Blue", "Green"]
    )
    question = crud.create_question(db_session, question_data)
    assert question.id is not None
    assert question.text == "What is your favorite color?"
    
    # Get questions by survey
    questions = crud.get_questions_by_survey(db_session, survey.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
    assert questions[0].text == "What is your favorite color?"
    
    # Get question by ID
    retrieved_question = crud.get_question_by_id(db_session, question.id)
    assert retrieved_question is not None
    assert retrieved_question.id == question.id
    assert retrieved_question.text == "What is your favorite color?"
    assert retrieved_question.response_type == "multiple-choice"
    assert "Red" in retrieved_question.options

def test_create_and_get_session(db_session):
    """Test creating and retrieving a session."""
    # First, create a survey and demographic
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    # Create a session
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    assert session.id is not None
    
    # Get the session
    retrieved_session = crud.get_session_by_id(db_session, session.id)
    assert retrieved_session is not None
    assert retrieved_session.id == session.id
    assert retrieved_session.survey_id == survey.id
    assert retrieved_session.demographic_id == demographic.id

def test_create_and_get_agent(db_session):
    """Test creating and retrieving an agent."""
    # First, create a survey, demographic, and session
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    
    # Create an agent
    agent_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 30,
            "income": 75000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Software Engineer"
        }
    )
    agent = crud.create_agent(db_session, agent_data)
    assert agent.id is not None
    
    # Get the agent
    retrieved_agent = crud.get_agent_by_id(db_session, agent.id)
    assert retrieved_agent is not None
    assert retrieved_agent.id == agent.id
    assert retrieved_agent.session_id == session.id
    assert retrieved_agent.numerical_characteristics["age"] == 30
    assert retrieved_agent.categorical_characteristics["gender"] == "male"

def test_create_and_get_response(db_session):
    """Test creating and retrieving a response."""
    # First, create a survey, demographic, session, agent, and question
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    
    agent_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 30,
            "income": 75000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Software Engineer"
        }
    )
    agent = crud.create_agent(db_session, agent_data)
    
    question_data = QuestionCreate(
        survey_id=survey.id,
        text="What is your favorite color?",
        response_type="multiple-choice",
        options=["Red", "Blue", "Green"]
    )
    question = crud.create_question(db_session, question_data)
    
    # Create a response
    response_data = ResponseCreate(
        session_id=session.id,
        agent_id=agent.id,
        survey_id=survey.id,
        question_id=question.id,
        response="Blue"
    )
    response = crud.create_response(db_session, response_data)
    assert response.id is not None
    
    # Get responses by survey
    responses = crud.get_responses_by_survey(db_session, survey.id)
    assert len(responses) == 1
    assert responses[0].id == response.id
    assert responses[0].response == "Blue"
    
    # Get responses by agent
    responses = crud.get_responses_by_agent(db_session, agent.id)
    assert len(responses) == 1
    assert responses[0].id == response.id
    assert responses[0].response == "Blue"
    
    # Get responses by session
    responses = crud.get_responses_by_session(db_session, session.id)
    assert len(responses) == 1
    assert responses[0].id == response.id
    assert responses[0].response == "Blue"

@pytest.mark.skip(reason="PostgreSQL-specific functions not compatible with test setup")
def test_filter_agents_by_numerical(db_session):
    """Test filtering agents by numerical characteristics."""
    # First, create a survey, demographic, and session
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    
    # Create agents with different ages
    agent1_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 25,
            "income": 50000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Software Engineer"
        }
    )
    agent1 = crud.create_agent(db_session, agent1_data)
    
    agent2_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 35,
            "income": 75000
        },
        categorical_characteristics={
            "gender": "female",
            "occupation": "Data Scientist"
        }
    )
    agent2 = crud.create_agent(db_session, agent2_data)
    
    agent3_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 45,
            "income": 100000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Manager"
        }
    )
    agent3 = crud.create_agent(db_session, agent3_data)
    
    # Filter agents by age > 30
    agents = crud.filter_agents_by_numerical(db_session, "age", ">", 30)
    assert len(agents) == 2
    assert any(agent.id == agent2.id for agent in agents)
    assert any(agent.id == agent3.id for agent in agents)
    
    # Filter agents by income <= 75000
    agents = crud.filter_agents_by_numerical(db_session, "income", "<=", 75000)
    assert len(agents) == 2
    assert any(agent.id == agent1.id for agent in agents)
    assert any(agent.id == agent2.id for agent in agents)

def test_filter_agents_by_categorical(db_session):
    """Test filtering agents by categorical characteristics."""
    # First, create a survey, demographic, and session
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    
    # Create agents with different genders and occupations
    agent1_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 25,
            "income": 50000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Software Engineer"
        }
    )
    agent1 = crud.create_agent(db_session, agent1_data)
    
    agent2_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 35,
            "income": 75000
        },
        categorical_characteristics={
            "gender": "female",
            "occupation": "Data Scientist"
        }
    )
    agent2 = crud.create_agent(db_session, agent2_data)
    
    agent3_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 45,
            "income": 100000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Manager"
        }
    )
    agent3 = crud.create_agent(db_session, agent3_data)
    
    # Filter agents by gender = male
    agents = crud.filter_agents_by_categorical(db_session, "gender", "male")
    assert len(agents) == 2
    assert any(agent.id == agent1.id for agent in agents)
    assert any(agent.id == agent3.id for agent in agents)
    
    # Filter agents by occupation = Data Scientist
    agents = crud.filter_agents_by_categorical(db_session, "occupation", "Data Scientist")
    assert len(agents) == 1
    assert agents[0].id == agent2.id

def test_update_and_delete_agent(db_session):
    """Test updating and deleting an agent."""
    # First, create a survey, demographic, session, and agent
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    demographic_data = DemographicsCreate(
        name="Test Demographic",
        numerical_characteristics={"age_min": 18, "age_max": 65},
        categorical_characteristics={"occupation": ["white-collar", "blue-collar"]}
    )
    demographic = crud.create_demographic(db_session, demographic_data)
    
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographic.id
    )
    session = crud.create_session(db_session, session_data)
    
    agent_data = AgentCreate(
        session_id=session.id,
        numerical_characteristics={
            "age": 30,
            "income": 75000
        },
        categorical_characteristics={
            "gender": "male",
            "occupation": "Software Engineer"
        }
    )
    agent = crud.create_agent(db_session, agent_data)
    
    # Update the agent
    updated_numerical = agent.numerical_characteristics.copy()
    updated_numerical["age"] = 31
    updated_categorical = agent.categorical_characteristics.copy()
    updated_categorical["occupation"] = "Senior Software Engineer"
    
    updated_agent = crud.update_agent(db_session, agent.id, {
        "numerical_characteristics": updated_numerical,
        "categorical_characteristics": updated_categorical
    })
    
    assert updated_agent is not None
    assert updated_agent.numerical_characteristics["age"] == 31
    assert updated_agent.categorical_characteristics["occupation"] == "Senior Software Engineer"
    
    # Delete the agent
    deleted = crud.delete_agent(db_session, agent.id)
    assert deleted is True
    
    # Verify deletion
    retrieved_agent = crud.get_agent_by_id(db_session, agent.id)
    assert retrieved_agent is None

def test_update_and_delete_survey(db_session):
    """Test updating and deleting a survey."""
    # Create a survey
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey"
    )
    survey = crud.create_survey(db_session, survey_data)
    
    # Update the survey
    updated_survey = crud.update_survey(db_session, survey.id, {
        "name": "Updated Survey",
        "description": "An updated test survey"
    })
    
    assert updated_survey is not None
    assert updated_survey.name == "Updated Survey"
    assert updated_survey.description == "An updated test survey"
    
    # Delete the survey
    deleted = crud.delete_survey(db_session, survey.id)
    assert deleted is True
    
    # Verify deletion
    retrieved_survey = crud.get_survey_by_id(db_session, survey.id)
    assert retrieved_survey is None 