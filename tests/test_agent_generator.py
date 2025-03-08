import json
import pytest
from backend.core.agent_generator import generate_agent_characteristics, DeterministicRandom
from backend.core.schemas import (
    DemographicDistribution,
    NumericalCharacteristicsDistribution,
    CategoricalCharacteristicsDistribution,
    DistributionData,
    PoliticalAffiliationDistribution,
    ProbabilityPoint,
    CategoricalProbabilityWithEnum
)

def create_example_demographic():
    """Create an example demographic distribution for testing"""
    # Create example probability points for age distribution
    age_points = [
        ProbabilityPoint(value=20, probability=0.2),
        ProbabilityPoint(value=30, probability=0.3),
        ProbabilityPoint(value=40, probability=0.3),
        ProbabilityPoint(value=60, probability=0.2)
    ]
    
    # Create example probability points for income distribution
    income_points = [
        ProbabilityPoint(value=30000, probability=0.3),
        ProbabilityPoint(value=60000, probability=0.4),
        ProbabilityPoint(value=100000, probability=0.2),
        ProbabilityPoint(value=150000, probability=0.1)
    ]
    
    # Create example probability points for education distribution
    education_points = [
        ProbabilityPoint(value=12, probability=0.4),
        ProbabilityPoint(value=16, probability=0.4),
        ProbabilityPoint(value=20, probability=0.2)
    ]
    
    # Create example probability points for religiosity distribution
    religiosity_points = [
        ProbabilityPoint(value=2, probability=0.3),
        ProbabilityPoint(value=5, probability=0.4),
        ProbabilityPoint(value=8, probability=0.3)
    ]
    
    # Create example political distributions
    economic_points = [
        ProbabilityPoint(value=-0.5, probability=0.3),
        ProbabilityPoint(value=0, probability=0.4),
        ProbabilityPoint(value=0.5, probability=0.3)
    ]
    
    governance_points = [
        ProbabilityPoint(value=-0.7, probability=0.2),
        ProbabilityPoint(value=-0.2, probability=0.3),
        ProbabilityPoint(value=0.3, probability=0.3),
        ProbabilityPoint(value=0.8, probability=0.2)
    ]
    
    cultural_points = [
        ProbabilityPoint(value=-0.8, probability=0.25),
        ProbabilityPoint(value=-0.3, probability=0.25),
        ProbabilityPoint(value=0.3, probability=0.25),
        ProbabilityPoint(value=0.8, probability=0.25)
    ]
    
    # Create example categorical distributions
    race_ethnicity = [
        CategoricalProbabilityWithEnum(category="white", probability=0.6),
        CategoricalProbabilityWithEnum(category="black", probability=0.15),
        CategoricalProbabilityWithEnum(category="hispanic", probability=0.15),
        CategoricalProbabilityWithEnum(category="east asian", probability=0.1)
    ]
    
    gender = [
        CategoricalProbabilityWithEnum(category="male", probability=0.48),
        CategoricalProbabilityWithEnum(category="female", probability=0.48),
        CategoricalProbabilityWithEnum(category="nonbinary", probability=0.04)
    ]
    
    religion = [
        CategoricalProbabilityWithEnum(category="christian", probability=0.65),
        CategoricalProbabilityWithEnum(category="jewish", probability=0.05),
        CategoricalProbabilityWithEnum(category="muslim", probability=0.05),
        CategoricalProbabilityWithEnum(category="hindu", probability=0.05),
        CategoricalProbabilityWithEnum(category="buddhist", probability=0.05),
        CategoricalProbabilityWithEnum(category="other", probability=0.15)
    ]
    
    urbanization = [
        CategoricalProbabilityWithEnum(category="urban", probability=0.4),
        CategoricalProbabilityWithEnum(category="suburban", probability=0.4),
        CategoricalProbabilityWithEnum(category="rural", probability=0.2)
    ]
    
    education_style = [
        CategoricalProbabilityWithEnum(category="formal k-12", probability=0.3),
        CategoricalProbabilityWithEnum(category="formal k-12 + university", probability=0.5),
        CategoricalProbabilityWithEnum(category="vocational", probability=0.2)
    ]
    
    employment_style = [
        CategoricalProbabilityWithEnum(category="white-collar", probability=0.4),
        CategoricalProbabilityWithEnum(category="blue-collar", probability=0.3),
        CategoricalProbabilityWithEnum(category="entrepreneur", probability=0.1),
        CategoricalProbabilityWithEnum(category="unemployed", probability=0.1),
        CategoricalProbabilityWithEnum(category="retired", probability=0.1)
    ]
    
    # Create the full demographic distribution
    return DemographicDistribution(
        numerical=NumericalCharacteristicsDistribution(
            age=DistributionData(range=[18, 80], points=age_points),
            income_level=DistributionData(range=[20000, 200000], points=income_points),
            years_of_education=DistributionData(range=[8, 22], points=education_points),
            religiosity=DistributionData(range=[0, 10], points=religiosity_points),
            political_affiliation=PoliticalAffiliationDistribution(
                economic=DistributionData(range=[-1, 1], points=economic_points),
                governance=DistributionData(range=[-1, 1], points=governance_points),
                cultural=DistributionData(range=[-1, 1], points=cultural_points)
            )
        ),
        categorical=CategoricalCharacteristicsDistribution(
            race_ethnicity=race_ethnicity,
            gender=gender,
            religion=religion,
            urbanization=urbanization,
            education_style=education_style,
            employment_style=employment_style,
            location="New York"
        )
    )

def format_agent_characteristics(agent_characteristics):
    """Format agent characteristics for display"""
    numerical = agent_characteristics.numerical
    categorical = agent_characteristics.categorical
    
    # Format numerical characteristics
    formatted_numerical = {
        "age": numerical.age,
        "income_level": f"${numerical.income_level:,.0f}",
        "years_of_education": numerical.years_of_education,
        "religiosity": numerical.religiosity,
        "political_affiliation": {
            "economic": numerical.political_affiliation.economic,
            "governance": numerical.political_affiliation.governance,
            "cultural": numerical.political_affiliation.cultural
        }
    }
    
    # Format categorical characteristics
    formatted_categorical = {
        "race_ethnicity": categorical.race_ethnicity,
        "gender": categorical.gender,
        "religion": categorical.religion,
        "urbanization": categorical.urbanization,
        "education_style": categorical.education_style,
        "employment_style": categorical.employment_style,
        "location": categorical.location
    }
    
    return {
        "numerical": formatted_numerical,
        "categorical": formatted_categorical
    }

def test_generate_agent_characteristics():
    """Test that agent characteristics are generated correctly"""
    # Create an example demographic distribution
    demographic = create_example_demographic()
    
    # Create a deterministic random number generator with a fixed seed
    random = DeterministicRandom("test_seed_1")
    
    # Generate agent characteristics
    agent_characteristics = generate_agent_characteristics(demographic, random)
    
    # Check that the agent has all the required characteristics
    assert agent_characteristics.numerical is not None
    assert agent_characteristics.categorical is not None
    
    # Check numerical characteristics
    numerical = agent_characteristics.numerical
    assert 18 <= numerical.age <= 80
    assert 20000 <= numerical.income_level <= 200000
    assert 8 <= numerical.years_of_education <= 22
    assert 0 <= numerical.religiosity <= 10
    assert -1 <= numerical.political_affiliation.economic <= 1
    assert -1 <= numerical.political_affiliation.governance <= 1
    assert -1 <= numerical.political_affiliation.cultural <= 1
    
    # Check categorical characteristics
    categorical = agent_characteristics.categorical
    assert categorical.race_ethnicity in ["white", "black", "hispanic", "east asian", "south asian", "indigenous", "mena", "mixed/other"]
    assert categorical.gender in ["male", "female", "nonbinary", "other"]
    assert categorical.religion in ["hindu", "christian", "muslim", "jewish", "buddhist", "other"]
    assert categorical.urbanization in ["suburban", "urban", "rural"]
    assert categorical.education_style in ["formal k-12", "formal k-12 + university", "vocational", "religious", "self-taught"]
    assert categorical.employment_style in ["unemployed", "part-time", "white-collar", "blue-collar", "entrepreneur", "self-employed", "executive/upper management", "retired"]
    assert categorical.location == "New York"

def test_deterministic_generation():
    """Test that agent generation is deterministic"""
    # Create an example demographic distribution
    demographic = create_example_demographic()
    
    # Generate the first agent with a fixed seed
    fixed_random1 = DeterministicRandom("fixed_seed")
    agent1 = generate_agent_characteristics(demographic, fixed_random1)
    
    # Generate another agent with the same seed
    fixed_random2 = DeterministicRandom("fixed_seed")
    agent2 = generate_agent_characteristics(demographic, fixed_random2)
    
    # Check that the agents are identical
    assert agent1.numerical.age == agent2.numerical.age
    assert agent1.numerical.income_level == agent2.numerical.income_level
    assert agent1.numerical.years_of_education == agent2.numerical.years_of_education
    assert agent1.numerical.religiosity == agent2.numerical.religiosity
    assert agent1.numerical.political_affiliation.economic == agent2.numerical.political_affiliation.economic
    assert agent1.numerical.political_affiliation.governance == agent2.numerical.political_affiliation.governance
    assert agent1.numerical.political_affiliation.cultural == agent2.numerical.political_affiliation.cultural
    
    assert agent1.categorical.race_ethnicity == agent2.categorical.race_ethnicity
    assert agent1.categorical.gender == agent2.categorical.gender
    assert agent1.categorical.religion == agent2.categorical.religion
    assert agent1.categorical.urbanization == agent2.categorical.urbanization
    assert agent1.categorical.education_style == agent2.categorical.education_style
    assert agent1.categorical.employment_style == agent2.categorical.employment_style
    assert agent1.categorical.location == agent2.categorical.location

def test_distribution_sampling():
    """Test that distribution sampling works correctly"""
    # Create a simple distribution
    distribution = DistributionData(
        range=[0, 100],
        points=[
            ProbabilityPoint(value=25, probability=0.5),
            ProbabilityPoint(value=75, probability=0.5)
        ]
    )
    
    # Sample from the distribution multiple times
    random = DeterministicRandom("test_seed")
    samples = [generate_agent_characteristics(create_example_demographic(), DeterministicRandom(f"test_seed_{i}")) for i in range(100)]
    
    # Check that the samples follow the expected distribution
    # For example, check that we have a mix of different categorical values
    race_counts = {}
    gender_counts = {}
    
    for sample in samples:
        race = sample.categorical.race_ethnicity
        gender = sample.categorical.gender
        
        race_counts[race] = race_counts.get(race, 0) + 1
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    
    # Check that we have at least 3 different races and 2 different genders
    assert len(race_counts) >= 3
    assert len(gender_counts) >= 2

if __name__ == "__main__":
    # Run the tests
    demographic = create_example_demographic()
    
    # Generate and display 5 agents
    print("\n=== DETERMINISTICALLY GENERATED AGENTS ===\n")
    for i in range(5):
        # Use a different seed for each agent
        agent_random = DeterministicRandom(f"test_seed_{i}")
        
        # Generate agent characteristics
        agent_characteristics = generate_agent_characteristics(demographic, agent_random)
        
        # Format and print the agent's characteristics
        formatted = format_agent_characteristics(agent_characteristics)
        print(f"Agent {i+1}:")
        print(f"  Numerical Characteristics:")
        for key, value in formatted["numerical"].items():
            if key == "political_affiliation":
                print(f"    {key.replace('_', ' ').title()}:")
                for pol_key, pol_value in value.items():
                    print(f"      {pol_key.title()}: {pol_value:.2f}")
            else:
                print(f"    {key.replace('_', ' ').title()}: {value}")
        
        print(f"  Categorical Characteristics:")
        for key, value in formatted["categorical"].items():
            print(f"    {key.replace('_', ' ').title()}: {value}")
        
        print()
    
    # Demonstrate determinism
    print("\n=== DEMONSTRATING DETERMINISM ===\n")
    
    # Generate the first agent with a fixed seed
    fixed_random = DeterministicRandom("fixed_seed")
    agent1 = generate_agent_characteristics(demographic, fixed_random)
    
    # Generate another agent with the same seed
    fixed_random2 = DeterministicRandom("fixed_seed")
    agent2 = generate_agent_characteristics(demographic, fixed_random2)
    
    # Format and print both agents
    formatted1 = format_agent_characteristics(agent1)
    formatted2 = format_agent_characteristics(agent2)
    
    print("Agent 1:")
    print(json.dumps(formatted1, indent=2))
    print("\nAgent 2 (same seed):")
    print(json.dumps(formatted2, indent=2))
    
    # Check if they are identical
    are_identical = (
        formatted1["numerical"]["age"] == formatted2["numerical"]["age"] and
        formatted1["numerical"]["income_level"] == formatted2["numerical"]["income_level"] and
        formatted1["categorical"]["race_ethnicity"] == formatted2["categorical"]["race_ethnicity"] and
        formatted1["categorical"]["gender"] == formatted2["categorical"]["gender"]
    )
    
    print(f"\nAgents are identical: {are_identical}") 