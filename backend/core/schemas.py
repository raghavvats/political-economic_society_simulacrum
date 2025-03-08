from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum

# ============================================================================
# Base Distribution Models
# ============================================================================

class ProbabilityPoint(BaseModel):
    value: float
    probability: float

class DistributionData(BaseModel):
    range: List[float] = Field(
        ..., 
        description="Min and max values for the distribution"
    )
    points: List[ProbabilityPoint] = Field(
        ..., 
        description="List of points defining the probability distribution. Can represent normal, custom, multimodal, etc."
    )

    @validator('range')
    def validate_range(cls, v):
        if len(v) != 2:
            raise ValueError("Range must contain exactly two values: [min, max]")
        if v[0] >= v[1]:
            raise ValueError("Range minimum must be less than maximum")
        return v

    @validator('points')
    def validate_points(cls, v, values):
        if not v:
            raise ValueError("Must have at least one probability point")
        
        # Check if range exists in values
        if 'range' in values:
            min_val, max_val = values['range']
            for point in v:
                if point.value < min_val or point.value > max_val:
                    raise ValueError(f"Point value {point.value} is outside the specified range [{min_val}, {max_val}]")
        
        # Validate total probability
        total_probability = sum(p.probability for p in v)
        if not (0.99 <= total_probability <= 1.01):
            raise ValueError(f"Total probability must sum to approximately 1 (got {total_probability})")
        
        return v

class CategoricalProbability(BaseModel):
    category: str
    probability: float
    
    @validator('probability')
    def validate_probability(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Probability must be between 0 and 1")
        return v

# ============================================================================
# Enums for Categorical Values
# ============================================================================

class RaceEthnicity(str, Enum):
    white = "white"
    black = "black"
    hispanic = "hispanic"
    south_asian = "south asian"
    east_asian = "east asian"
    indigenous = "indigenous"
    mena = "mena"
    mixed_other = "mixed/other"

class Gender(str, Enum):
    male = "male"
    female = "female"
    nonbinary = "nonbinary"
    other = "other"

class Religion(str, Enum):
    hindu = "hindu"
    christian = "christian"
    muslim = "muslim"
    jewish = "jewish"
    buddhist = "buddhist"
    other = "other"

class Urbanization(str, Enum):
    suburban = "suburban"
    urban = "urban"
    rural = "rural"

class EducationStyle(str, Enum):
    formal_k12 = "formal k-12"
    formal_k12_university = "formal k-12 + university"
    vocational = "vocational"
    religious = "religious"
    self_taught = "self-taught"

class EmploymentStyle(str, Enum):
    unemployed = "unemployed"
    part_time = "part-time"
    white_collar = "white-collar"
    blue_collar = "blue-collar"
    entrepreneur = "entrepreneur"
    self_employed = "self-employed"
    executive = "executive/upper management"
    retired = "retired"

# ============================================================================
# Demographic Distribution Models (for population characteristics)
# ============================================================================

class PoliticalAffiliationDistribution(BaseModel):
    """Distribution of political affiliation dimensions for a demographic"""
    economic: DistributionData
    governance: DistributionData
    cultural: DistributionData
    
    @validator('economic', 'governance', 'cultural')
    def validate_political_range(cls, v):
        if v.range[0] < -1 or v.range[1] > 1:
            raise ValueError("Political affiliation values must be between -1 and 1")
        return v

class NumericalCharacteristicsDistribution(BaseModel):
    """Distributions of numerical characteristics for a demographic"""
    age: DistributionData
    income_level: DistributionData
    years_of_education: DistributionData
    religiosity: DistributionData
    political_affiliation: PoliticalAffiliationDistribution
    
    @validator('age')
    def validate_age_range(cls, v):
        if v.range[0] < 1 or v.range[1] > 120:
            raise ValueError("Age must be between 1 and 120")
        return v
    
    @validator('income_level')
    def validate_income_range(cls, v):
        if v.range[0] < 0 or v.range[1] > 10000000:  # 10 million
            raise ValueError("Income must be between 0 and 10,000,000")
        return v
    
    @validator('years_of_education')
    def validate_education_range(cls, v):
        if v.range[0] < 0 or v.range[1] > 22:
            raise ValueError("Years of education must be between 0 and 22")
        return v
    
    @validator('religiosity')
    def validate_religiosity_range(cls, v):
        if v.range[0] < 0 or v.range[1] > 10:
            raise ValueError("Religiosity must be between 0 and 10")
        return v

class CategoricalProbabilityWithEnum(BaseModel):
    """A categorical probability with enum validation"""
    category: str
    probability: float
    
    @validator('probability')
    def validate_probability(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Probability must be between 0 and 1")
        return v

class CategoricalCharacteristicsDistribution(BaseModel):
    """Distributions of categorical characteristics for a demographic"""
    race_ethnicity: List[CategoricalProbabilityWithEnum]
    gender: List[CategoricalProbabilityWithEnum]
    religion: List[CategoricalProbabilityWithEnum]
    urbanization: List[CategoricalProbabilityWithEnum]
    education_style: List[CategoricalProbabilityWithEnum]
    employment_style: List[CategoricalProbabilityWithEnum]
    location: str = Field(..., example="New York", description="Free-form geographic location")
    
    @validator('race_ethnicity')
    def validate_race_ethnicity(cls, v):
        for item in v:
            if item.category not in [e.value for e in RaceEthnicity]:
                raise ValueError(f"Invalid race/ethnicity: {item.category}")
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        for item in v:
            if item.category not in [e.value for e in Gender]:
                raise ValueError(f"Invalid gender: {item.category}")
        return v
    
    @validator('religion')
    def validate_religion(cls, v):
        for item in v:
            if item.category not in [e.value for e in Religion]:
                raise ValueError(f"Invalid religion: {item.category}")
        return v
    
    @validator('urbanization')
    def validate_urbanization(cls, v):
        for item in v:
            if item.category not in [e.value for e in Urbanization]:
                raise ValueError(f"Invalid urbanization: {item.category}")
        return v
    
    @validator('education_style')
    def validate_education_style(cls, v):
        for item in v:
            if item.category not in [e.value for e in EducationStyle]:
                raise ValueError(f"Invalid education style: {item.category}")
        return v
    
    @validator('employment_style')
    def validate_employment_style(cls, v):
        for item in v:
            if item.category not in [e.value for e in EmploymentStyle]:
                raise ValueError(f"Invalid employment style: {item.category}")
        return v
    
    @validator('race_ethnicity', 'gender', 'religion', 'urbanization', 'education_style', 'employment_style')
    def validate_total_probability(cls, v):
        total = sum(item.probability for item in v)
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Total probability must sum to approximately 1 (got {total})")
        return v

class DemographicDistribution(BaseModel):
    """Complete distribution model for a demographic"""
    numerical: NumericalCharacteristicsDistribution
    categorical: CategoricalCharacteristicsDistribution

# ============================================================================
# Individual Agent Characteristic Models (for single agents)
# ============================================================================

class PoliticalAffiliation(BaseModel):
    """Political affiliation values for an individual agent"""
    economic: float = Field(..., ge=-1, le=1)
    governance: float = Field(..., ge=-1, le=1)
    cultural: float = Field(..., ge=-1, le=1)

class AgentNumericalCharacteristics(BaseModel):
    """Numerical characteristics for an individual agent"""
    age: float = Field(..., ge=1, le=120)
    income_level: float = Field(..., ge=0, le=10000000)
    years_of_education: float = Field(..., ge=0, le=22)
    religiosity: float = Field(..., ge=0, le=10)
    political_affiliation: PoliticalAffiliation

class AgentCategoricalCharacteristics(BaseModel):
    """Categorical characteristics for an individual agent"""
    race_ethnicity: RaceEthnicity
    gender: Gender
    religion: Religion
    urbanization: Urbanization
    education_style: EducationStyle
    employment_style: EmploymentStyle
    location: str

class AgentCharacteristics(BaseModel):
    """Complete characteristics model for an individual agent"""
    numerical: AgentNumericalCharacteristics
    categorical: AgentCategoricalCharacteristics

# ============================================================================
# Database Models (for API and ORM)
# ============================================================================

class AgentBase(BaseModel):
    """Base model for agent database representation"""
    numerical_characteristics: Dict[str, Any]  # Will store AgentNumericalCharacteristics as JSON
    categorical_characteristics: Dict[str, str]  # Will store AgentCategoricalCharacteristics as JSON

class AgentCreate(AgentBase):
    session_id: int

class Agent(AgentBase):
    id: int
    session_id: int
    
    class Config:
        orm_mode = True

class SurveyBase(BaseModel):
    name: str
    description: Optional[str] = None

class SurveyCreate(SurveyBase):
    pass

class Survey(SurveyBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    survey_id: int
    text: str
    response_type: Literal["multiple-choice", "free-text", "likert"]
    options: Optional[List[str]] = None

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    
    class Config:
        orm_mode = True

class DemographicsBase(BaseModel):
    """Base model for demographics database representation"""
    name: str
    numerical_characteristics: Dict[str, Any]  # Will store NumericalCharacteristicsDistribution as JSON
    categorical_characteristics: Dict[str, Any]  # Will store CategoricalCharacteristicsDistribution as JSON
    num_agents: int = Field(100, ge=1, le=10000)

class DemographicsCreate(DemographicsBase):
    pass

class Demographics(DemographicsBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    survey_id: int
    demographic_id: int

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    started_at: datetime
    
    class Config:
        orm_mode = True

class ResponseBase(BaseModel):
    session_id: int
    agent_id: int
    survey_id: int
    question_id: int
    response: str

class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    
    class Config:
        orm_mode = True 