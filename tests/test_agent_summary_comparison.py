import json
import pytest
from collections import Counter, defaultdict
import numpy as np
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO

from backend.core.agent_generator import (
    generate_agent_characteristics,
    DeterministicRandom
)
from backend.core.population_summary import (
    summarize_population,
    format_profile_for_display
)
from backend.core.schemas import (
    DemographicDistribution,
    NumericalCharacteristicsDistribution,
    CategoricalCharacteristicsDistribution,
    DistributionData,
    PoliticalAffiliationDistribution,
    ProbabilityPoint,
    CategoricalProbabilityWithEnum,
    AgentCharacteristics
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

def generate_agents(demographic, num_agents=500):
    """Generate a list of agents based on the demographic distribution"""
    agents = []
    
    for i in range(num_agents):
        # Use a deterministic seed for each agent
        agent_random = DeterministicRandom(f"test_seed_{i}")
        
        # Generate agent characteristics
        agent_characteristics = generate_agent_characteristics(demographic, agent_random)
        
        agents.append(agent_characteristics)
    
    return agents

def analyze_agents(agents):
    """Analyze the generated agents and return statistics"""
    # Count categorical characteristics
    categorical_counts = {
        "race_ethnicity": Counter(),
        "gender": Counter(),
        "religion": Counter(),
        "urbanization": Counter(),
        "education_style": Counter(),
        "employment_style": Counter()
    }
    
    # Collect numerical characteristics
    numerical_values = {
        "age": [],
        "income_level": [],
        "years_of_education": [],
        "religiosity": [],
        "political_economic": [],
        "political_governance": [],
        "political_cultural": []
    }
    
    # Process each agent
    for agent in agents:
        # Process categorical characteristics
        for category in categorical_counts.keys():
            value = getattr(agent.categorical, category)
            categorical_counts[category][value] += 1
        
        # Process numerical characteristics
        numerical_values["age"].append(agent.numerical.age)
        numerical_values["income_level"].append(agent.numerical.income_level)
        numerical_values["years_of_education"].append(agent.numerical.years_of_education)
        numerical_values["religiosity"].append(agent.numerical.religiosity)
        numerical_values["political_economic"].append(agent.numerical.political_affiliation.economic)
        numerical_values["political_governance"].append(agent.numerical.political_affiliation.governance)
        numerical_values["political_cultural"].append(agent.numerical.political_affiliation.cultural)
    
    # Calculate statistics for numerical values
    numerical_stats = {}
    for category, values in numerical_values.items():
        numerical_stats[category] = {
            "mean": np.mean(values),
            "min": min(values),
            "max": max(values),
            "percentiles": {
                "25th": np.percentile(values, 25),
                "50th": np.percentile(values, 50),
                "75th": np.percentile(values, 75)
            },
            "histogram": np.histogram(values, bins=10)[0].tolist()
        }
    
    return {
        "categorical_counts": {k: dict(v) for k, v in categorical_counts.items()},
        "numerical_stats": numerical_stats
    }

def compare_with_summary(agents_stats, demographic, num_agents):
    """Compare the agent statistics with the population summary"""
    # Generate the population summary
    summary = summarize_population(demographic, num_agents, 4)
    
    # Extract expected categorical distributions
    expected_categorical = {}
    for profile in summary.profiles:
        for category in ["race_ethnicity", "gender", "religion", "urbanization", "education_style", "employment"]:
            if category not in expected_categorical:
                expected_categorical[category] = defaultdict(float)
            
            for subcat, percentage in getattr(profile, category).items():
                expected_categorical[category][subcat] += (percentage / 100) * profile.count
    
    # Convert to integer counts
    for category, subcats in expected_categorical.items():
        expected_categorical[category] = {k: round(v) for k, v in subcats.items()}
    
    # Compare categorical distributions
    categorical_comparison = {}
    for category in ["race_ethnicity", "gender", "religion", "urbanization", "education_style"]:
        expected = expected_categorical[category]
        actual = agents_stats["categorical_counts"][category]
        
        # Calculate differences
        differences = {}
        for subcat in set(expected.keys()) | set(actual.keys()):
            expected_count = expected.get(subcat, 0)
            actual_count = actual.get(subcat, 0)
            differences[subcat] = actual_count - expected_count
        
        categorical_comparison[category] = {
            "expected": expected,
            "actual": actual,
            "differences": differences
        }
    
    # Compare numerical distributions
    numerical_comparison = {}
    for category in ["age", "income_level", "years_of_education", "religiosity"]:
        expected_stats = {}  # We would need to extract this from the summary
        actual_stats = agents_stats["numerical_stats"][category]
        
        numerical_comparison[category] = {
            "actual_mean": actual_stats["mean"],
            "actual_min": actual_stats["min"],
            "actual_max": actual_stats["max"],
            "actual_percentiles": actual_stats["percentiles"]
        }
    
    return {
        "categorical_comparison": categorical_comparison,
        "numerical_comparison": numerical_comparison
    }

def test_agent_generation_matches_summary():
    """Test that agent generation matches the population summary"""
    # Create a demographic distribution
    demographic = create_example_demographic()
    
    # Generate agents
    num_agents = 500
    agents = generate_agents(demographic, num_agents)
    
    # Analyze the agents
    agents_stats = analyze_agents(agents)
    
    # Compare with the summary
    comparison = compare_with_summary(agents_stats, demographic, num_agents)
    
    # Check that the categorical distributions are close to expected
    for category, data in comparison["categorical_comparison"].items():
        for subcat, diff in data["differences"].items():
            # Allow for some variation due to randomness
            assert abs(diff) < num_agents * 0.1, f"Difference for {category}.{subcat} is too large: {diff}"
    
    # Check that the numerical distributions are within expected ranges
    for category, data in comparison["numerical_comparison"].items():
        # Check that the mean is within a reasonable range
        if category == "age":
            expected_mean = 0.2 * 20 + 0.3 * 30 + 0.3 * 40 + 0.2 * 60  # Based on the distribution
            assert abs(data["actual_mean"] - expected_mean) < 5, f"Mean for {category} is off: {data['actual_mean']} vs {expected_mean}"
        elif category == "income_level":
            expected_mean = 0.3 * 30000 + 0.4 * 60000 + 0.2 * 100000 + 0.1 * 150000
            assert abs(data["actual_mean"] - expected_mean) < 10000, f"Mean for {category} is off: {data['actual_mean']} vs {expected_mean}"

if __name__ == "__main__":
    # Create a demographic distribution
    demographic = create_example_demographic()
    
    # Generate 500 agents
    num_agents = 500
    agents = generate_agents(demographic, num_agents)
    
    # Analyze the agents
    agents_stats = analyze_agents(agents)
    
    # Compare with the summary
    comparison = compare_with_summary(agents_stats, demographic, num_agents)
    
    # Print the results
    print("\n=== AGENT GENERATION RESULTS ===\n")
    print(f"Generated {num_agents} agents based on the demographic distribution.")
    
    # Print categorical distributions
    print("\n--- Categorical Distributions ---\n")
    for category, counts in agents_stats["categorical_counts"].items():
        print(f"{category.replace('_', ' ').title()}:")
        total = sum(counts.values())
        for subcat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"  {subcat}: {count} ({percentage:.1f}%)")
        print()
    
    # Print numerical statistics
    print("\n--- Numerical Statistics ---\n")
    for category, stats in agents_stats["numerical_stats"].items():
        print(f"{category.replace('_', ' ').title()}:")
        print(f"  Mean: {stats['mean']:.2f}")
        print(f"  Range: {stats['min']} to {stats['max']}")
        print(f"  Percentiles: 25th={stats['percentiles']['25th']:.2f}, " +
              f"50th={stats['percentiles']['50th']:.2f}, " +
              f"75th={stats['percentiles']['75th']:.2f}")
        print()
    
    # Print comparison with summary
    print("\n=== COMPARISON WITH POPULATION SUMMARY ===\n")
    
    # Print categorical comparison
    print("--- Categorical Comparison ---\n")
    for category, data in comparison["categorical_comparison"].items():
        print(f"{category.replace('_', ' ').title()}:")
        print("  Expected vs Actual (Difference):")
        
        # Get all subcategories
        all_subcats = sorted(set(data["expected"].keys()) | set(data["actual"].keys()))
        
        for subcat in all_subcats:
            expected = data["expected"].get(subcat, 0)
            actual = data["actual"].get(subcat, 0)
            diff = data["differences"].get(subcat, 0)
            
            print(f"  {subcat}: {expected} vs {actual} ({diff:+d})")
        print()
    
    # Print numerical comparison
    print("--- Numerical Comparison ---\n")
    for category, data in comparison["numerical_comparison"].items():
        print(f"{category.replace('_', ' ').title()}:")
        print(f"  Actual Mean: {data['actual_mean']:.2f}")
        print(f"  Actual Range: {data['actual_min']} to {data['actual_max']}")
        print(f"  Actual Percentiles: 25th={data['actual_percentiles']['25th']:.2f}, " +
              f"50th={data['actual_percentiles']['50th']:.2f}, " +
              f"75th={data['actual_percentiles']['75th']:.2f}")
        print()
    
    # Print all 500 agents
    print("\n=== ALL 500 AGENTS ===\n")
    
    # Create a DataFrame for easier viewing
    agents_data = []
    for i, agent in enumerate(agents):
        agent_dict = {
            "id": i + 1,
            "age": agent.numerical.age,
            "income": agent.numerical.income_level,
            "education": agent.numerical.years_of_education,
            "religiosity": agent.numerical.religiosity,
            "political_economic": agent.numerical.political_affiliation.economic,
            "political_governance": agent.numerical.political_affiliation.governance,
            "political_cultural": agent.numerical.political_affiliation.cultural,
            "race_ethnicity": agent.categorical.race_ethnicity,
            "gender": agent.categorical.gender,
            "religion": agent.categorical.religion,
            "urbanization": agent.categorical.urbanization,
            "education_style": agent.categorical.education_style,
            "employment_style": agent.categorical.employment_style
        }
        agents_data.append(agent_dict)
    
    # Create a DataFrame
    df = pd.DataFrame(agents_data)
    
    # Print the DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(df.to_string()) 