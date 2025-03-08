from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import hashlib
from sqlalchemy.orm import Session
import json
import math

from backend.core.schemas import (
    DemographicDistribution,
    CategoricalProbabilityWithEnum,
    DistributionData,
    PoliticalAffiliationDistribution,
    DemographicsBase,
    NumericalCharacteristicsDistribution,
    CategoricalCharacteristicsDistribution,
    ProbabilityPoint,
    AgentCharacteristics,
    AgentNumericalCharacteristics,
    AgentCategoricalCharacteristics,
    PoliticalAffiliation,
    AgentCreate
)
from backend.db.models import Agent

class DeterministicRandom:
    """
    A deterministic random number generator that produces the same sequence
    of random numbers for the same seed.
    """
    def __init__(self, seed: str):
        """
        Initialize the deterministic random number generator with a seed.
        
        Args:
            seed: A string seed to initialize the random number generator
        """
        # Create a hash of the seed to get a 32-bit integer
        hash_obj = hashlib.md5(seed.encode())
        seed_int = int(hash_obj.hexdigest(), 16) % (2**32)
        
        # Initialize the numpy random number generator with the seed
        self.rng = np.random.RandomState(seed_int)
    
    def random(self) -> float:
        """
        Generate a random float in the range [0, 1).
        
        Returns:
            A random float
        """
        return self.rng.random()
    
    def randint(self, low: int, high: int) -> int:
        """
        Generate a random integer in the range [low, high).
        
        Args:
            low: The lower bound (inclusive)
            high: The upper bound (exclusive)
            
        Returns:
            A random integer
        """
        return self.rng.randint(low, high)
    
    def choice(self, items: List[Any], p: Optional[List[float]] = None) -> Any:
        """
        Choose a random item from a list, optionally with specified probabilities.
        
        Args:
            items: The list of items to choose from
            p: The probabilities associated with each item
            
        Returns:
            A randomly chosen item
        """
        return self.rng.choice(items, p=p)
    
    def shuffle(self, items: List[Any]) -> None:
        """
        Shuffle a list in-place.
        
        Args:
            items: The list to shuffle
        """
        self.rng.shuffle(items)

def generate_agents(
    demographic: DemographicsBase,
    session_id: int,
    db: Session
) -> List[Agent]:
    """
    Generate agents deterministically based on a demographic split.
    
    This function creates agents with both categorical and numerical characteristics
    based on the demographic split, ensuring that the same input always produces
    the same set of agents.
    
    Args:
        demographic: The demographic split to generate agents from
        session_id: The session ID to associate the agents with
        db: The database session to use for storing the agents
        
    Returns:
        A list of the generated Agent objects
    """
    # Convert the stored characteristics to DemographicDistribution
    demographic_distribution = DemographicDistribution(
        numerical=demographic.numerical_characteristics,
        categorical=demographic.categorical_characteristics
    )
    
    # Create a deterministic random number generator
    # Use the demographic ID and name as the seed for determinism
    seed = f"{demographic.id}_{demographic.name}"
    random = DeterministicRandom(seed)
    
    # Generate the agents
    agents = []
    for i in range(demographic.num_agents):
        # Use a deterministic seed for each agent
        agent_seed = f"{seed}_{i}"
        agent_random = DeterministicRandom(agent_seed)
        
        # Generate the agent's characteristics
        agent_characteristics = generate_agent_characteristics(
            demographic_distribution, agent_random
        )
        
        # Create the agent in the database
        db_agent = create_agent_in_db(
            agent_characteristics, session_id, db
        )
        
        agents.append(db_agent)
    
    return agents

def generate_agent_characteristics(
    demographic: DemographicDistribution,
    random: DeterministicRandom
) -> AgentCharacteristics:
    """
    Generate characteristics for a single agent.
    
    Args:
        demographic: The demographic distribution to sample from
        random: A deterministic random number generator
        
    Returns:
        The agent's characteristics
    """
    # Generate numerical characteristics
    numerical_chars = generate_numerical_characteristics(
        demographic.numerical, random
    )
    
    # Generate categorical characteristics
    categorical_chars = generate_categorical_characteristics(
        demographic.categorical, random
    )
    
    # Combine into AgentCharacteristics
    return AgentCharacteristics(
        numerical=numerical_chars,
        categorical=categorical_chars
    )

def round_to_nearest(value: float, nearest: float) -> float:
    """
    Round a value to the nearest specified increment.
    
    Args:
        value: The value to round
        nearest: The increment to round to
        
    Returns:
        The rounded value
    """
    return round(value / nearest) * nearest

def generate_numerical_characteristics(
    numerical_distribution: NumericalCharacteristicsDistribution,
    random: DeterministicRandom
) -> AgentNumericalCharacteristics:
    """
    Generate numerical characteristics for an agent.
    
    Args:
        numerical_distribution: The numerical distribution to sample from
        random: A deterministic random number generator
        
    Returns:
        The agent's numerical characteristics
    """
    # Sample age from distribution and round to nearest whole number
    age = round(sample_from_distribution(numerical_distribution.age, random))
    
    # Sample income from distribution and round to nearest hundred
    income = round_to_nearest(
        sample_from_distribution(numerical_distribution.income_level, random),
        100
    )
    
    # Sample education from distribution
    education = sample_from_distribution(numerical_distribution.years_of_education, random)
    
    # Sample religiosity from distribution and round to nearest 0.5
    religiosity = round_to_nearest(
        sample_from_distribution(numerical_distribution.religiosity, random),
        0.5
    )
    
    # Sample political affiliation and round to nearest 0.05
    economic = round_to_nearest(
        sample_from_distribution(numerical_distribution.political_affiliation.economic, random),
        0.05
    )
    governance = round_to_nearest(
        sample_from_distribution(numerical_distribution.political_affiliation.governance, random),
        0.05
    )
    cultural = round_to_nearest(
        sample_from_distribution(numerical_distribution.political_affiliation.cultural, random),
        0.05
    )
    
    # Create the political affiliation object
    political_affiliation = PoliticalAffiliation(
        economic=economic,
        governance=governance,
        cultural=cultural
    )
    
    # Create the numerical characteristics object
    return AgentNumericalCharacteristics(
        age=age,
        income_level=income,
        years_of_education=education,
        religiosity=religiosity,
        political_affiliation=political_affiliation
    )

def generate_categorical_characteristics(
    categorical_distribution: CategoricalCharacteristicsDistribution,
    random: DeterministicRandom
) -> AgentCategoricalCharacteristics:
    """
    Generate categorical characteristics for an agent.
    
    Args:
        categorical_distribution: The categorical distribution to sample from
        random: A deterministic random number generator
        
    Returns:
        The agent's categorical characteristics
    """
    # Sample race/ethnicity
    race_ethnicity = sample_from_categorical(
        categorical_distribution.race_ethnicity, random
    )
    
    # Sample gender
    gender = sample_from_categorical(
        categorical_distribution.gender, random
    )
    
    # Sample religion
    religion = sample_from_categorical(
        categorical_distribution.religion, random
    )
    
    # Sample urbanization
    urbanization = sample_from_categorical(
        categorical_distribution.urbanization, random
    )
    
    # Sample education style
    education_style = sample_from_categorical(
        categorical_distribution.education_style, random
    )
    
    # Sample employment style
    employment_style = sample_from_categorical(
        categorical_distribution.employment_style, random
    )
    
    # Create the categorical characteristics object
    return AgentCategoricalCharacteristics(
        race_ethnicity=race_ethnicity,
        gender=gender,
        religion=religion,
        urbanization=urbanization,
        education_style=education_style,
        employment_style=employment_style,
        location=categorical_distribution.location
    )

def sample_from_distribution(
    distribution: DistributionData,
    random: DeterministicRandom
) -> float:
    """
    Sample a value from a distribution deterministically.
    
    Args:
        distribution: The probability distribution
        random: A deterministic random number generator
        
    Returns:
        A sampled value
    """
    # Extract the distribution parameters
    min_val, max_val = distribution.range
    points = distribution.points
    
    # Sort points by value for quantile-based sampling
    sorted_points = sorted(points, key=lambda p: p.value)
    
    # Calculate cumulative probabilities
    cumulative_probs = []
    cumulative_prob = 0
    for point in sorted_points:
        cumulative_prob += point.probability
        cumulative_probs.append(cumulative_prob)
    
    # Generate a random value between 0 and 1
    r = random.random()
    
    # Find the appropriate quantile
    for i, cum_prob in enumerate(cumulative_probs):
        if r <= cum_prob:
            # If this is the first point or r is exactly at the cumulative probability,
            # return the exact value
            if i == 0 or r == cum_prob:
                return sorted_points[i].value
            
            # Otherwise, interpolate between this point and the previous one
            prev_cum_prob = cumulative_probs[i-1]
            prev_value = sorted_points[i-1].value
            curr_value = sorted_points[i].value
            
            # Calculate the position of r within the probability range
            prob_range = cum_prob - prev_cum_prob
            prob_position = (r - prev_cum_prob) / prob_range
            
            # Interpolate the value
            value = prev_value + prob_position * (curr_value - prev_value)
            
            return value
    
    # If we get here, there was a rounding error and r > 1
    # Return the last point's value
    return sorted_points[-1].value

def sample_from_categorical(
    distribution: List[CategoricalProbabilityWithEnum],
    random: DeterministicRandom
) -> str:
    """
    Sample a category from a categorical distribution deterministically.
    
    Args:
        distribution: The categorical probability distribution
        random: A deterministic random number generator
        
    Returns:
        A sampled category
    """
    # Extract categories and probabilities
    categories = [cat_prob.category for cat_prob in distribution]
    probabilities = [cat_prob.probability for cat_prob in distribution]
    
    # Choose a category based on the probabilities
    return random.choice(categories, p=probabilities)

def create_agent_in_db(
    agent_characteristics: AgentCharacteristics,
    session_id: int,
    db: Session
) -> Agent:
    """
    Create an agent in the database.
    
    Args:
        agent_characteristics: The agent's characteristics
        session_id: The session ID to associate the agent with
        db: The database session to use
        
    Returns:
        The created Agent object
    """
    # Convert the agent characteristics to dictionaries for JSONB storage
    numerical_characteristics = agent_characteristics.numerical.dict()
    categorical_characteristics = agent_characteristics.categorical.dict()
    
    # Create the agent
    agent_create = AgentCreate(
        session_id=session_id,
        numerical_characteristics=numerical_characteristics,
        categorical_characteristics=categorical_characteristics
    )
    
    # Create the database model
    db_agent = Agent(
        session_id=agent_create.session_id,
        numerical_characteristics=agent_create.numerical_characteristics,
        categorical_characteristics=agent_create.categorical_characteristics
    )
    
    # Add to the database
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return db_agent

def generate_agents_for_session(
    demographics: List[DemographicsBase],
    session_id: int,
    db: Session
) -> List[Agent]:
    """
    Generate agents for a session based on multiple demographic splits.
    
    Args:
        demographics: The demographic splits to generate agents from
        session_id: The session ID to associate the agents with
        db: The database session to use
        
    Returns:
        A list of the generated Agent objects
    """
    all_agents = []
    
    for demographic in demographics:
        agents = generate_agents(demographic, session_id, db)
        all_agents.extend(agents)
    
    return all_agents 