#!/usr/bin/env python3
"""
Test script to verify Agent CRUD operations.
"""
import pytest
import uuid
from backend.core.schemas import AgentCreate, SurveyCreate, DemographicsCreate, SessionCreate
from backend.db import crud

@pytest.fixture
def test_environment(db):
    """Set up test environment with required related entities."""
    # Create a test survey
    survey_data = SurveyCreate(
        name="Test Survey",
        description="A test survey for CRUD operations"
    )
    survey = crud.create_survey(db, survey_data)
    print(f"✅ Created test survey with ID: {survey.id}")
    
    # Create test demographics
    demographics_data = DemographicsCreate(
        name="Test Demographics",
        numerical_characteristics={
            "age_mean": 35,
            "income_mean": 50000
        },
        categorical_characteristics={
            "gender_distribution": {"male": 0.5, "female": 0.5}
        }
    )
    demographics = crud.create_demographic(db, demographics_data)
    print(f"✅ Created test demographics with ID: {demographics.id}")
    
    # Create a test session
    session_data = SessionCreate(
        survey_id=survey.id,
        demographic_id=demographics.id
    )
    session = crud.create_session(db, session_data)
    print(f"✅ Created test session with ID: {session.id}")
    
    env = {
        "survey": survey,
        "demographics": demographics,
        "session": session
    }
    
    yield env
    
    # Note: We're not cleaning up the test environment (survey, demographics, session)
    # because the delete functions don't exist in the crud module.
    # In a real application, you would want to clean up these entities.
    print("\nNote: Test environment (survey, demographics, session) not cleaned up.")
    print("These entities will remain in the database for future tests.")

def test_agent_crud(db, test_environment):
    """Test CRUD operations for the Agent model."""
    # Generate a unique identifier for this test run
    test_id = str(uuid.uuid4())[:8]
    
    # Create a test agent
    print(f"\nCreating test agent with ID: {test_id}...")
    agent_data = AgentCreate(
        session_id=test_environment["session"].id,
        numerical_characteristics={
            "age": 30,
            "income": 75000,
            "years_of_education": 16,
            "political_leaning": 0.2,
            "economic_leaning": -0.3,
            "social_leaning": 0.5
        },
        categorical_characteristics={
            "gender": "male",
            "race": "white",
            "occupation": "Software Engineer",
            "education_level": "Masters"
        }
    )
    
    # Create the agent
    created_agent = crud.create_agent(db, agent_data)
    print(f"✅ Agent created with ID: {created_agent.id}")
    assert created_agent is not None
    assert created_agent.id is not None
    
    # Read the agent
    print("Reading agent...")
    read_agent = crud.get_agent_by_id(db, created_agent.id)
    print(f"✅ Agent read successfully: ID {read_agent.id}")
    assert read_agent is not None
    assert read_agent.id == created_agent.id
    
    # Update the agent
    print("Updating agent...")
    updated_characteristics = created_agent.numerical_characteristics.copy()
    updated_characteristics["age"] = 31
    updated_agent = crud.update_agent(
        db, 
        created_agent.id, 
        {"numerical_characteristics": updated_characteristics}
    )
    print(f"✅ Agent updated successfully: Age now {updated_agent.numerical_characteristics['age']}")
    assert updated_agent is not None
    assert updated_agent.numerical_characteristics["age"] == 31
    
    # Delete the agent
    print("Deleting agent...")
    deleted = crud.delete_agent(db, created_agent.id)
    print("✅ Agent deleted successfully")
    assert deleted is True
    
    # Verify deletion
    deleted_agent = crud.get_agent_by_id(db, created_agent.id)
    print("✅ Verified agent no longer exists")
    assert deleted_agent is None

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 