from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# ============================================================================
# Distribution and Characteristic Models (from schema.py)
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

    def validate_distribution(self):
        """Ensure that the sum of probabilities is ~1 for discrete distributions"""
        total_probability = sum(p.probability for p in self.points)
        if not (0.99 <= total_probability <= 1.01):
            raise ValueError("Total probability must sum to approximately 1.")

class CategoricalProbability(BaseModel):
    category: str
    probability: float

class PoliticalAffiliationDistribution(BaseModel):
    economic: DistributionData
    governance: DistributionData
    cultural: DistributionData

class NumericalCharacteristics(BaseModel):
    age: DistributionData
    income_level: DistributionData
    years_of_education: DistributionData
    religiosity: DistributionData
    political_affiliation: PoliticalAffiliationDistribution

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

class CategoricalCharacteristics(BaseModel):
    race_ethnicity: List[CategoricalProbability]
    gender: List[CategoricalProbability]
    religion: List[CategoricalProbability]
    urbanization: List[CategoricalProbability]
    education_style: List[CategoricalProbability]
    employment_style: List[CategoricalProbability]
    location: str = Field(..., example="New York", description="Free-form geographic location")

class AgentCharacteristics(BaseModel):
    numerical: NumericalCharacteristics
    categorical: CategoricalCharacteristics

# ============================================================================
# Database Models (from schemas.py)
# ============================================================================

# Base models (for shared attributes)
class AgentBase(BaseModel):
    numerical_characteristics: Dict[str, Union[int, float]]
    categorical_characteristics: Dict[str, str]


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
    response_type: str
    options: Optional[List[str]] = None


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int
    
    class Config:
        orm_mode = True


class DemographicsBase(BaseModel):
    name: str
    numerical_characteristics: Dict[str, Any]
    categorical_characteristics: Dict[str, Any]


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