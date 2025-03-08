import json
import pytest
import os
import csv
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
    AgentCharacteristics,
    RaceEthnicity,
    Gender,
    Religion,
    Urbanization,
    EducationStyle,
    EmploymentStyle
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

def save_agents_to_csv(agents, csv_path):
    """Save the generated agents to a CSV file"""
    # Create a list of dictionaries for each agent
    agents_data = []
    for i, agent in enumerate(agents):
        agent_dict = {
            "id": i + 1,
            "age": agent.numerical.age,
            "income_level": agent.numerical.income_level,
            "years_of_education": agent.numerical.years_of_education,
            "religiosity": agent.numerical.religiosity,
            "political_economic": agent.numerical.political_affiliation.economic,
            "political_governance": agent.numerical.political_affiliation.governance,
            "political_cultural": agent.numerical.political_affiliation.cultural,
            "race_ethnicity": agent.categorical.race_ethnicity,
            "gender": agent.categorical.gender,
            "religion": agent.categorical.religion,
            "urbanization": agent.categorical.urbanization,
            "education_style": agent.categorical.education_style,
            "employment_style": agent.categorical.employment_style,
            "location": agent.categorical.location
        }
        agents_data.append(agent_dict)
    
    # Write to CSV
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = agents_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for agent_data in agents_data:
            writer.writerow(agent_data)
    
    return agents_data

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
    
    # Calculate expected numerical statistics from the demographic distribution
    expected_numerical = {}
    
    # Age
    age_points = demographic.numerical.age.points
    expected_age_mean = sum(p.value * p.probability for p in age_points)
    expected_numerical["age"] = {"mean": expected_age_mean}
    
    # Income
    income_points = demographic.numerical.income_level.points
    expected_income_mean = sum(p.value * p.probability for p in income_points)
    expected_numerical["income_level"] = {"mean": expected_income_mean}
    
    # Education
    education_points = demographic.numerical.years_of_education.points
    expected_education_mean = sum(p.value * p.probability for p in education_points)
    expected_numerical["years_of_education"] = {"mean": expected_education_mean}
    
    # Religiosity
    religiosity_points = demographic.numerical.religiosity.points
    expected_religiosity_mean = sum(p.value * p.probability for p in religiosity_points)
    expected_numerical["religiosity"] = {"mean": expected_religiosity_mean}
    
    # Political affiliations
    economic_points = demographic.numerical.political_affiliation.economic.points
    expected_economic_mean = sum(p.value * p.probability for p in economic_points)
    expected_numerical["political_economic"] = {"mean": expected_economic_mean}
    
    governance_points = demographic.numerical.political_affiliation.governance.points
    expected_governance_mean = sum(p.value * p.probability for p in governance_points)
    expected_numerical["political_governance"] = {"mean": expected_governance_mean}
    
    cultural_points = demographic.numerical.political_affiliation.cultural.points
    expected_cultural_mean = sum(p.value * p.probability for p in cultural_points)
    expected_numerical["political_cultural"] = {"mean": expected_cultural_mean}
    
    # Compare numerical statistics
    for category in ["age", "income_level", "years_of_education", "religiosity", "political_economic", "political_governance", "political_cultural"]:
        expected_stats = expected_numerical.get(category, {})
        actual_stats = agents_stats["numerical_stats"][category]
        
        numerical_comparison[category] = {
            "expected_mean": expected_stats.get("mean"),
            "actual_mean": actual_stats["mean"],
            "actual_min": actual_stats["min"],
            "actual_max": actual_stats["max"],
            "actual_percentiles": actual_stats["percentiles"]
        }
    
    return {
        "categorical_comparison": categorical_comparison,
        "numerical_comparison": numerical_comparison,
        "summary_profiles": [
            {
                "name": profile.name,
                "count": profile.count,
                "percentage": profile.percentage
            }
            for profile in summary.profiles
        ]
    }

def test_agent_generation_and_csv_export():
    """Test that agent generation matches the population summary and exports to CSV"""
    # Create a demographic distribution
    demographic = create_example_demographic()
    
    # Generate agents
    num_agents = 500
    agents = generate_agents(demographic, num_agents)
    
    # Save agents to CSV
    csv_path = "generated_agents.csv"
    save_agents_to_csv(agents, csv_path)
    
    # Verify the CSV file exists
    assert os.path.exists(csv_path), f"CSV file {csv_path} was not created"
    
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
        if data["expected_mean"] is not None:
            # Check that the mean is within a reasonable range of the expected mean
            if category == "age":
                assert abs(data["actual_mean"] - data["expected_mean"]) < 5, f"Mean for {category} is off: {data['actual_mean']} vs {data['expected_mean']}"
            elif category == "income_level":
                # Allow for a larger difference in income level (up to 15000)
                assert abs(data["actual_mean"] - data["expected_mean"]) < 15000, f"Mean for {category} is off: {data['actual_mean']} vs {data['expected_mean']}"
            elif category == "years_of_education":
                assert abs(data["actual_mean"] - data["expected_mean"]) < 2, f"Mean for {category} is off: {data['actual_mean']} vs {data['expected_mean']}"
            elif category == "religiosity":
                assert abs(data["actual_mean"] - data["expected_mean"]) < 1, f"Mean for {category} is off: {data['actual_mean']} vs {data['expected_mean']}"
            else:  # Political dimensions
                # Allow for a larger difference in political dimensions (up to 0.3)
                assert abs(data["actual_mean"] - data["expected_mean"]) < 0.3, f"Mean for {category} is off: {data['actual_mean']} vs {data['expected_mean']}"

def print_demographic_and_summary_statistics():
    """Print the demographic distribution and summary statistics for the generated agents"""
    # Create a demographic distribution
    demographic = create_example_demographic()
    
    # Generate agents
    num_agents = 500
    agents = generate_agents(demographic, num_agents)
    
    # Save agents to CSV
    csv_path = "generated_agents.csv"
    save_agents_to_csv(agents, csv_path)
    
    # Analyze the agents
    agents_stats = analyze_agents(agents)
    
    # Compare with the summary
    comparison = compare_with_summary(agents_stats, demographic, num_agents)
    
    # Print the demographic distribution
    print("\n=== DEMOGRAPHIC DISTRIBUTION ===\n")
    
    # Print numerical distributions
    print("--- Numerical Distributions ---\n")
    
    print("Age Distribution:")
    for point in demographic.numerical.age.points:
        print(f"  {point.value}: {point.probability * 100:.1f}%")
    print()
    
    print("Income Distribution:")
    for point in demographic.numerical.income_level.points:
        print(f"  ${point.value:,.0f}: {point.probability * 100:.1f}%")
    print()
    
    print("Education Years Distribution:")
    for point in demographic.numerical.years_of_education.points:
        print(f"  {point.value} years: {point.probability * 100:.1f}%")
    print()
    
    print("Religiosity Distribution:")
    for point in demographic.numerical.religiosity.points:
        print(f"  {point.value}: {point.probability * 100:.1f}%")
    print()
    
    print("Political Economic Distribution:")
    for point in demographic.numerical.political_affiliation.economic.points:
        print(f"  {point.value}: {point.probability * 100:.1f}%")
    print()
    
    print("Political Governance Distribution:")
    for point in demographic.numerical.political_affiliation.governance.points:
        print(f"  {point.value}: {point.probability * 100:.1f}%")
    print()
    
    print("Political Cultural Distribution:")
    for point in demographic.numerical.political_affiliation.cultural.points:
        print(f"  {point.value}: {point.probability * 100:.1f}%")
    print()
    
    # Print categorical distributions
    print("--- Categorical Distributions ---\n")
    
    print("Race/Ethnicity Distribution:")
    for cat in demographic.categorical.race_ethnicity:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    print("Gender Distribution:")
    for cat in demographic.categorical.gender:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    print("Religion Distribution:")
    for cat in demographic.categorical.religion:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    print("Urbanization Distribution:")
    for cat in demographic.categorical.urbanization:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    print("Education Style Distribution:")
    for cat in demographic.categorical.education_style:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    print("Employment Style Distribution:")
    for cat in demographic.categorical.employment_style:
        print(f"  {cat.category}: {cat.probability * 100:.1f}%")
    print()
    
    # Print summary profiles
    print("\n=== SUMMARY PROFILES ===\n")
    
    for profile in comparison["summary_profiles"]:
        print(f"Profile: {profile['name']}")
        print(f"  Count: {profile['count']} ({profile['percentage']:.1f}%)")
        print()
    
    # Print agent statistics
    print("\n=== AGENT STATISTICS ===\n")
    
    # Print categorical distributions
    print("--- Categorical Distributions ---\n")
    for category, counts in agents_stats["categorical_counts"].items():
        print(f"{category.replace('_', ' ').title()}:")
        total = sum(counts.values())
        for subcat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"  {subcat}: {count} ({percentage:.1f}%)")
        print()
    
    # Print numerical statistics
    print("--- Numerical Statistics ---\n")
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
        if data["expected_mean"] is not None:
            print(f"  Expected Mean: {data['expected_mean']:.2f}")
        print(f"  Actual Mean: {data['actual_mean']:.2f}")
        print(f"  Actual Range: {data['actual_min']} to {data['actual_max']}")
        print(f"  Actual Percentiles: 25th={data['actual_percentiles']['25th']:.2f}, " +
              f"50th={data['actual_percentiles']['50th']:.2f}, " +
              f"75th={data['actual_percentiles']['75th']:.2f}")
        print()
    
    print(f"\nAgents have been saved to {csv_path}")

if __name__ == "__main__":
    print_demographic_and_summary_statistics() 