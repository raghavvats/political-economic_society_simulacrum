"""
Utility functions for working with agent and demographic data.
"""
from typing import Dict, Any, List, Union
import random
from backend.core.schemas import (
    AgentCharacteristics, 
    AgentNumericalCharacteristics,
    AgentCategoricalCharacteristics,
    PoliticalAffiliation,
    DemographicDistribution,
    NumericalCharacteristicsDistribution,
    CategoricalCharacteristicsDistribution,
    PoliticalAffiliationDistribution,
    DistributionData,
    CategoricalProbability,
    CategoricalProbabilityWithEnum,
    # Import enums
    RaceEthnicity,
    Gender,
    Religion,
    Urbanization,
    EducationStyle,
    EmploymentStyle
)

def convert_agent_characteristics_to_db(agent_chars: AgentCharacteristics) -> Dict[str, Dict[str, Any]]:
    """
    Convert structured AgentCharacteristics to the format stored in the database.
    
    Args:
        agent_chars: Structured agent characteristics
        
    Returns:
        Dictionary with numerical_characteristics and categorical_characteristics
    """
    numerical = {
        "age": agent_chars.numerical.age,
        "income_level": agent_chars.numerical.income_level,
        "years_of_education": agent_chars.numerical.years_of_education,
        "religiosity": agent_chars.numerical.religiosity,
        "political_affiliation": {
            "economic": agent_chars.numerical.political_affiliation.economic,
            "governance": agent_chars.numerical.political_affiliation.governance,
            "cultural": agent_chars.numerical.political_affiliation.cultural,
        }
    }
    
    categorical = {
        "race_ethnicity": agent_chars.categorical.race_ethnicity.value,
        "gender": agent_chars.categorical.gender.value,
        "religion": agent_chars.categorical.religion.value,
        "urbanization": agent_chars.categorical.urbanization.value,
        "education_style": agent_chars.categorical.education_style.value,
        "employment_style": agent_chars.categorical.employment_style.value,
        "location": agent_chars.categorical.location,
    }
    
    return {
        "numerical_characteristics": numerical,
        "categorical_characteristics": categorical
    }

def convert_db_to_agent_characteristics(db_data: Dict[str, Any]) -> AgentCharacteristics:
    """
    Convert database format to structured AgentCharacteristics.
    
    Args:
        db_data: Dictionary with numerical_characteristics and categorical_characteristics
        
    Returns:
        Structured agent characteristics
    """
    num_data = db_data["numerical_characteristics"]
    cat_data = db_data["categorical_characteristics"]
    
    political = PoliticalAffiliation(
        economic=num_data["political_affiliation"]["economic"],
        governance=num_data["political_affiliation"]["governance"],
        cultural=num_data["political_affiliation"]["cultural"]
    )
    
    numerical = AgentNumericalCharacteristics(
        age=num_data["age"],
        income_level=num_data["income_level"],
        years_of_education=num_data["years_of_education"],
        religiosity=num_data["religiosity"],
        political_affiliation=political
    )
    
    categorical = AgentCategoricalCharacteristics(
        race_ethnicity=RaceEthnicity(cat_data["race_ethnicity"]),
        gender=Gender(cat_data["gender"]),
        religion=Religion(cat_data["religion"]),
        urbanization=Urbanization(cat_data["urbanization"]),
        education_style=EducationStyle(cat_data["education_style"]),
        employment_style=EmploymentStyle(cat_data["employment_style"]),
        location=cat_data["location"]
    )
    
    return AgentCharacteristics(
        numerical=numerical,
        categorical=categorical
    )

def convert_demographic_distribution_to_db(demo_dist: DemographicDistribution) -> Dict[str, Dict[str, Any]]:
    """
    Convert structured DemographicDistribution to the format stored in the database.
    
    Args:
        demo_dist: Structured demographic distribution
        
    Returns:
        Dictionary with numerical_characteristics and categorical_characteristics
    """
    numerical = {
        "age": {
            "range": demo_dist.numerical.age.range,
            "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.age.points]
        },
        "income_level": {
            "range": demo_dist.numerical.income_level.range,
            "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.income_level.points]
        },
        "years_of_education": {
            "range": demo_dist.numerical.years_of_education.range,
            "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.years_of_education.points]
        },
        "religiosity": {
            "range": demo_dist.numerical.religiosity.range,
            "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.religiosity.points]
        },
        "political_affiliation": {
            "economic": {
                "range": demo_dist.numerical.political_affiliation.economic.range,
                "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.political_affiliation.economic.points]
            },
            "governance": {
                "range": demo_dist.numerical.political_affiliation.governance.range,
                "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.political_affiliation.governance.points]
            },
            "cultural": {
                "range": demo_dist.numerical.political_affiliation.cultural.range,
                "points": [{"value": p.value, "probability": p.probability} for p in demo_dist.numerical.political_affiliation.cultural.points]
            }
        }
    }
    
    categorical = {
        "race_ethnicity": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.race_ethnicity],
        "gender": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.gender],
        "religion": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.religion],
        "urbanization": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.urbanization],
        "education_style": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.education_style],
        "employment_style": [{"category": c.category, "probability": c.probability} for c in demo_dist.categorical.employment_style],
        "location": demo_dist.categorical.location
    }
    
    return {
        "numerical_characteristics": numerical,
        "categorical_characteristics": categorical
    }

def convert_db_to_demographic_distribution(db_data: Dict[str, Any]) -> DemographicDistribution:
    """
    Convert database format to structured DemographicDistribution.
    
    Args:
        db_data: Dictionary with numerical_characteristics and categorical_characteristics
        
    Returns:
        Structured demographic distribution
    """
    num_data = db_data["numerical_characteristics"]
    cat_data = db_data["categorical_characteristics"]
    
    # Convert numerical characteristics
    age_dist = DistributionData(
        range=num_data["age"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["age"]["points"]]
    )
    
    income_dist = DistributionData(
        range=num_data["income_level"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["income_level"]["points"]]
    )
    
    education_dist = DistributionData(
        range=num_data["years_of_education"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["years_of_education"]["points"]]
    )
    
    religiosity_dist = DistributionData(
        range=num_data["religiosity"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["religiosity"]["points"]]
    )
    
    # Political affiliation distributions
    economic_dist = DistributionData(
        range=num_data["political_affiliation"]["economic"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["political_affiliation"]["economic"]["points"]]
    )
    
    governance_dist = DistributionData(
        range=num_data["political_affiliation"]["governance"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["political_affiliation"]["governance"]["points"]]
    )
    
    cultural_dist = DistributionData(
        range=num_data["political_affiliation"]["cultural"]["range"],
        points=[{"value": p["value"], "probability": p["probability"]} for p in num_data["political_affiliation"]["cultural"]["points"]]
    )
    
    political_dist = PoliticalAffiliationDistribution(
        economic=economic_dist,
        governance=governance_dist,
        cultural=cultural_dist
    )
    
    numerical = NumericalCharacteristicsDistribution(
        age=age_dist,
        income_level=income_dist,
        years_of_education=education_dist,
        religiosity=religiosity_dist,
        political_affiliation=political_dist
    )
    
    # Convert categorical characteristics
    race_ethnicity = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["race_ethnicity"]]
    gender = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["gender"]]
    religion = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["religion"]]
    urbanization = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["urbanization"]]
    education_style = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["education_style"]]
    employment_style = [CategoricalProbabilityWithEnum(category=c["category"], probability=c["probability"]) for c in cat_data["employment_style"]]
    
    categorical = CategoricalCharacteristicsDistribution(
        race_ethnicity=race_ethnicity,
        gender=gender,
        religion=religion,
        urbanization=urbanization,
        education_style=education_style,
        employment_style=employment_style,
        location=cat_data["location"]
    )
    
    return DemographicDistribution(
        numerical=numerical,
        categorical=categorical
    )

def sample_from_distribution(distribution: DistributionData) -> float:
    """
    Sample a value from a probability distribution.
    
    Args:
        distribution: The distribution to sample from
        
    Returns:
        A sampled value
    """
    # Simple discrete sampling based on the provided points
    r = random.random()
    cumulative = 0
    
    for point in distribution.points:
        cumulative += point.probability
        if r <= cumulative:
            return point.value
    
    # Fallback to the last point if we somehow didn't select one
    return distribution.points[-1].value

def sample_from_categorical(categories: List[CategoricalProbabilityWithEnum]) -> str:
    """
    Sample a category from a list of categorical probabilities.
    
    Args:
        categories: List of categories with probabilities
        
    Returns:
        A sampled category
    """
    r = random.random()
    cumulative = 0
    
    for cat in categories:
        cumulative += cat.probability
        if r <= cumulative:
            return cat.category
    
    # Fallback to the last category if we somehow didn't select one
    return categories[-1].category

def generate_agent_from_demographic(demographic: DemographicDistribution) -> AgentCharacteristics:
    """
    Generate an agent with characteristics sampled from a demographic distribution.
    
    Args:
        demographic: The demographic distribution to sample from
        
    Returns:
        An agent with sampled characteristics
    """
    # Sample numerical characteristics
    age = sample_from_distribution(demographic.numerical.age)
    income_level = sample_from_distribution(demographic.numerical.income_level)
    years_of_education = sample_from_distribution(demographic.numerical.years_of_education)
    religiosity = sample_from_distribution(demographic.numerical.religiosity)
    
    # Sample political affiliation
    economic = sample_from_distribution(demographic.numerical.political_affiliation.economic)
    governance = sample_from_distribution(demographic.numerical.political_affiliation.governance)
    cultural = sample_from_distribution(demographic.numerical.political_affiliation.cultural)
    
    political = PoliticalAffiliation(
        economic=economic,
        governance=governance,
        cultural=cultural
    )
    
    numerical = AgentNumericalCharacteristics(
        age=age,
        income_level=income_level,
        years_of_education=years_of_education,
        religiosity=religiosity,
        political_affiliation=political
    )
    
    # Sample categorical characteristics
    race_ethnicity_val = sample_from_categorical(demographic.categorical.race_ethnicity)
    gender_val = sample_from_categorical(demographic.categorical.gender)
    religion_val = sample_from_categorical(demographic.categorical.religion)
    urbanization_val = sample_from_categorical(demographic.categorical.urbanization)
    education_style_val = sample_from_categorical(demographic.categorical.education_style)
    employment_style_val = sample_from_categorical(demographic.categorical.employment_style)
    
    categorical = AgentCategoricalCharacteristics(
        race_ethnicity=RaceEthnicity(race_ethnicity_val),
        gender=Gender(gender_val),
        religion=Religion(religion_val),
        urbanization=Urbanization(urbanization_val),
        education_style=EducationStyle(education_style_val),
        employment_style=EmploymentStyle(employment_style_val),
        location=demographic.categorical.location
    )
    
    return AgentCharacteristics(
        numerical=numerical,
        categorical=categorical
    ) 