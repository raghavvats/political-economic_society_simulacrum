from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, cast, Float, Integer
from typing import Dict, List, Optional, Any, Union
from backend.db import models
from backend.core.schemas import AgentCreate, SurveyCreate, QuestionCreate, DemographicsCreate, SessionCreate, ResponseCreate


# CRUD operations for Agents
def create_agent(db: Session, agent_data: AgentCreate) -> models.Agent:
    """
    Create a new agent in the database.
    
    Args:
        db: Database session
        agent_data: Pydantic model containing agent data
    
    Returns:
        The created agent object
    """
    db_agent = models.Agent(
        session_id=agent_data.session_id,
        numerical_characteristics=agent_data.numerical_characteristics,
        categorical_characteristics=agent_data.categorical_characteristics
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Agent]:
    """
    Retrieve all agents with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of agent objects
    """
    return db.query(models.Agent).offset(skip).limit(limit).all()


def get_agent_by_id(db: Session, agent_id: int) -> Optional[models.Agent]:
    """
    Retrieve an agent by its ID.
    
    Args:
        db: Database session
        agent_id: ID of the agent to retrieve
    
    Returns:
        Agent object if found, None otherwise
    """
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def update_agent(db: Session, agent_id: int, agent_data: Dict[str, Any]) -> Optional[models.Agent]:
    """
    Update an existing agent.
    
    Args:
        db: Database session
        agent_id: ID of the agent to update
        agent_data: Dictionary containing updated agent data
    
    Returns:
        Updated agent object if found, None otherwise
    """
    db_agent = get_agent_by_id(db, agent_id)
    if db_agent:
        for key, value in agent_data.items():
            setattr(db_agent, key, value)
        db.commit()
        db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> bool:
    """
    Delete an agent by its ID.
    
    Args:
        db: Database session
        agent_id: ID of the agent to delete
    
    Returns:
        True if agent was deleted, False otherwise
    """
    db_agent = get_agent_by_id(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False


def filter_agents_by_numerical(
    db: Session, 
    field: str, 
    operator: str, 
    value: Union[int, float],
    skip: int = 0, 
    limit: int = 100
) -> List[models.Agent]:
    """
    Filter agents by a numerical characteristic.
    
    Args:
        db: Database session
        field: The name of the numerical field to filter on
        operator: One of '>', '<', '>=', '<=', '='
        value: The value to compare against
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of agent objects matching the filter
    """
    # Determine the appropriate cast type based on the value type
    cast_type = Integer if isinstance(value, int) else Float
    
    # Extract the field value and cast it to the appropriate type
    field_value = cast(func.jsonb_extract_path_text(models.Agent.numerical_characteristics, field), cast_type)
    
    # Apply the appropriate operator
    if operator == '>':
        query = db.query(models.Agent).filter(field_value > value)
    elif operator == '<':
        query = db.query(models.Agent).filter(field_value < value)
    elif operator == '>=':
        query = db.query(models.Agent).filter(field_value >= value)
    elif operator == '<=':
        query = db.query(models.Agent).filter(field_value <= value)
    else:  # '='
        query = db.query(models.Agent).filter(field_value == value)
    
    return query.offset(skip).limit(limit).all()


def filter_agents_by_categorical(
    db: Session, 
    field: str, 
    value: str,
    skip: int = 0, 
    limit: int = 100
) -> List[models.Agent]:
    """
    Filter agents by a categorical characteristic.
    
    Args:
        db: Database session
        field: The name of the categorical field to filter on
        value: The value to match
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of agent objects matching the filter
    """
    # Use the JSONB containment operator @> for more efficient filtering with GIN index
    filter_json = {field: value}
    query = db.query(models.Agent).filter(
        models.Agent.categorical_characteristics.contains(filter_json)
    )
    
    return query.offset(skip).limit(limit).all()


# CRUD operations for Surveys
def create_survey(db: Session, survey_data: SurveyCreate) -> models.Survey:
    """
    Create a new survey in the database.
    
    Args:
        db: Database session
        survey_data: Pydantic model containing survey data
    
    Returns:
        The created survey object
    """
    db_survey = models.Survey(
        name=survey_data.name,
        description=survey_data.description
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


def get_surveys(db: Session, skip: int = 0, limit: int = 100) -> List[models.Survey]:
    """
    Retrieve all surveys with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of survey objects
    """
    return db.query(models.Survey).offset(skip).limit(limit).all()


def get_survey_by_id(db: Session, survey_id: int) -> Optional[models.Survey]:
    """
    Retrieve a survey by its ID.
    
    Args:
        db: Database session
        survey_id: ID of the survey to retrieve
    
    Returns:
        Survey object if found, None otherwise
    """
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()


def update_survey(db: Session, survey_id: int, survey_data: Dict[str, Any]) -> Optional[models.Survey]:
    """
    Update an existing survey.
    
    Args:
        db: Database session
        survey_id: ID of the survey to update
        survey_data: Dictionary containing updated survey data
    
    Returns:
        Updated survey object if found, None otherwise
    """
    db_survey = get_survey_by_id(db, survey_id)
    if db_survey:
        for key, value in survey_data.items():
            setattr(db_survey, key, value)
        db.commit()
        db.refresh(db_survey)
    return db_survey


def delete_survey(db: Session, survey_id: int) -> bool:
    """
    Delete a survey by its ID.
    
    Args:
        db: Database session
        survey_id: ID of the survey to delete
    
    Returns:
        True if survey was deleted, False otherwise
    """
    db_survey = get_survey_by_id(db, survey_id)
    if db_survey:
        db.delete(db_survey)
        db.commit()
        return True
    return False


# CRUD operations for Questions
def create_question(db: Session, question_data: QuestionCreate) -> models.Question:
    """
    Create a new question in the database.
    
    Args:
        db: Database session
        question_data: Pydantic model containing question data
    
    Returns:
        The created question object
    """
    db_question = models.Question(
        survey_id=question_data.survey_id,
        text=question_data.text,
        response_type=question_data.response_type,
        options=question_data.options
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def get_questions_by_survey(db: Session, survey_id: int, skip: int = 0, limit: int = 100) -> List[models.Question]:
    """
    Retrieve all questions for a specific survey with pagination.
    
    Args:
        db: Database session
        survey_id: ID of the survey
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of question objects
    """
    return db.query(models.Question).filter(
        models.Question.survey_id == survey_id
    ).offset(skip).limit(limit).all()


def get_question_by_id(db: Session, question_id: int) -> Optional[models.Question]:
    """
    Retrieve a question by its ID.
    
    Args:
        db: Database session
        question_id: ID of the question to retrieve
    
    Returns:
        Question object if found, None otherwise
    """
    return db.query(models.Question).filter(models.Question.id == question_id).first()


# CRUD operations for Demographics
def create_demographic(db: Session, demographic_data: DemographicsCreate) -> models.Demographics:
    """
    Create a new demographic in the database.
    
    Args:
        db: Database session
        demographic_data: Pydantic model containing demographic data
    
    Returns:
        The created demographic object
    """
    db_demographic = models.Demographics(
        name=demographic_data.name,
        numerical_characteristics=demographic_data.numerical_characteristics,
        categorical_characteristics=demographic_data.categorical_characteristics
    )
    db.add(db_demographic)
    db.commit()
    db.refresh(db_demographic)
    return db_demographic


def get_demographics(db: Session, skip: int = 0, limit: int = 100) -> List[models.Demographics]:
    """
    Retrieve all demographics with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of demographic objects
    """
    return db.query(models.Demographics).offset(skip).limit(limit).all()


def get_demographic_by_id(db: Session, demographic_id: int) -> Optional[models.Demographics]:
    """
    Retrieve a demographic by its ID.
    
    Args:
        db: Database session
        demographic_id: ID of the demographic to retrieve
    
    Returns:
        Demographic object if found, None otherwise
    """
    return db.query(models.Demographics).filter(models.Demographics.id == demographic_id).first()


# CRUD operations for Sessions
def create_session(db: Session, session_data: SessionCreate) -> models.Session:
    """
    Create a new session in the database.
    
    Args:
        db: Database session
        session_data: Pydantic model containing session data
    
    Returns:
        The created session object
    """
    db_session = models.Session(
        survey_id=session_data.survey_id,
        demographic_id=session_data.demographic_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Session]:
    """
    Retrieve all sessions with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of session objects
    """
    return db.query(models.Session).offset(skip).limit(limit).all()


def get_session_by_id(db: Session, session_id: int) -> Optional[models.Session]:
    """
    Retrieve a session by its ID.
    
    Args:
        db: Database session
        session_id: ID of the session to retrieve
    
    Returns:
        Session object if found, None otherwise
    """
    return db.query(models.Session).filter(models.Session.id == session_id).first()


# CRUD operations for Responses
def create_response(db: Session, response_data: ResponseCreate) -> models.Response:
    """
    Create a new response in the database.
    
    Args:
        db: Database session
        response_data: Pydantic model containing response data
    
    Returns:
        The created response object
    """
    db_response = models.Response(
        session_id=response_data.session_id,
        agent_id=response_data.agent_id,
        survey_id=response_data.survey_id,
        question_id=response_data.question_id,
        response=response_data.response
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response


def get_responses_by_survey(db: Session, survey_id: int, skip: int = 0, limit: int = 100) -> List[models.Response]:
    """
    Retrieve all responses for a specific survey with pagination.
    
    Args:
        db: Database session
        survey_id: ID of the survey
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of response objects
    """
    return db.query(models.Response).filter(
        models.Response.survey_id == survey_id
    ).offset(skip).limit(limit).all()


def get_responses_by_agent(db: Session, agent_id: int, skip: int = 0, limit: int = 100) -> List[models.Response]:
    """
    Retrieve all responses for a specific agent with pagination.
    
    Args:
        db: Database session
        agent_id: ID of the agent
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of response objects
    """
    return db.query(models.Response).filter(
        models.Response.agent_id == agent_id
    ).offset(skip).limit(limit).all()


def get_responses_by_session(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[models.Response]:
    """
    Retrieve all responses for a specific session with pagination.
    
    Args:
        db: Database session
        session_id: ID of the session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of response objects
    """
    return db.query(models.Response).filter(
        models.Response.session_id == session_id
    ).offset(skip).limit(limit).all()


def get_responses_by_agent_characteristics(
    db: Session,
    numerical_filters: Optional[List[Dict[str, Any]]] = None,
    categorical_filters: Optional[List[Dict[str, Any]]] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Response]:
    """
    Retrieve responses based on agent characteristics (both numerical and categorical).
    
    Args:
        db: Database session
        numerical_filters: List of dictionaries with keys 'field', 'operator', and 'value'
                          for filtering numerical characteristics
        categorical_filters: List of dictionaries with keys 'field' and 'value'
                            for filtering categorical characteristics
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of response objects from agents matching the specified characteristics
    """
    # Start with a base query joining responses with agents
    query = db.query(models.Response).join(models.Agent, models.Response.agent_id == models.Agent.id)
    
    # Apply numerical filters if provided
    if numerical_filters:
        for filter_item in numerical_filters:
            field = filter_item['field']
            operator = filter_item.get('operator', '=')
            value = filter_item['value']
            
            # Determine the appropriate cast type based on the value type
            cast_type = Integer if isinstance(value, int) else Float
            
            # Extract the field value and cast it to the appropriate type
            field_value = cast(func.jsonb_extract_path_text(models.Agent.numerical_characteristics, field), cast_type)
            
            # Apply the appropriate operator
            if operator == '>':
                query = query.filter(field_value > value)
            elif operator == '<':
                query = query.filter(field_value < value)
            elif operator == '>=':
                query = query.filter(field_value >= value)
            elif operator == '<=':
                query = query.filter(field_value <= value)
            else:  # '='
                query = query.filter(field_value == value)
    
    # Apply categorical filters if provided
    if categorical_filters:
        for filter_item in categorical_filters:
            field = filter_item['field']
            value = filter_item['value']
            
            # Use the JSONB containment operator @> for more efficient filtering with GIN index
            filter_json = {field: value}
            query = query.filter(models.Agent.categorical_characteristics.contains(filter_json))
    
    return query.offset(skip).limit(limit).all() 