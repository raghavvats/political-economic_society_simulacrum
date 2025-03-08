import json
import pytest
from backend.core.population_summary import (
    summarize_population,
    summarize_multiple_demographics,
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
    DemographicsBase
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

def create_example_demographics_base():
    """Create example DemographicsBase objects for testing"""
    demographic1 = DemographicsBase(
        name="Urban Professionals",
        numerical_characteristics=create_example_demographic().numerical.dict(),
        categorical_characteristics=create_example_demographic().categorical.dict(),
        num_agents=1000,
        id=1
    )
    
    # Create a second demographic with different characteristics
    demographic2 = DemographicsBase(
        name="Rural Conservatives",
        numerical_characteristics={
            "age": {
                "range": [18, 80],
                "points": [
                    {"value": 25, "probability": 0.4},
                    {"value": 45, "probability": 0.4},
                    {"value": 65, "probability": 0.2}
                ]
            },
            "income_level": {
                "range": [20000, 200000],
                "points": [
                    {"value": 40000, "probability": 0.5},
                    {"value": 80000, "probability": 0.3},
                    {"value": 120000, "probability": 0.2}
                ]
            },
            "years_of_education": {
                "range": [8, 22],
                "points": [
                    {"value": 10, "probability": 0.2},
                    {"value": 14, "probability": 0.5},
                    {"value": 18, "probability": 0.3}
                ]
            },
            "religiosity": {
                "range": [0, 10],
                "points": [
                    {"value": 3, "probability": 0.4},
                    {"value": 7, "probability": 0.6}
                ]
            },
            "political_affiliation": {
                "economic": {
                    "range": [-1, 1],
                    "points": [
                        {"value": -0.7, "probability": 0.6},
                        {"value": 0.3, "probability": 0.4}
                    ]
                },
                "governance": {
                    "range": [-1, 1],
                    "points": [
                        {"value": -0.5, "probability": 0.5},
                        {"value": 0.5, "probability": 0.5}
                    ]
                },
                "cultural": {
                    "range": [-1, 1],
                    "points": [
                        {"value": -0.6, "probability": 0.7},
                        {"value": 0.4, "probability": 0.3}
                    ]
                }
            }
        },
        categorical_characteristics={
            "race_ethnicity": [
                {"category": "white", "probability": 0.7},
                {"category": "black", "probability": 0.2},
                {"category": "hispanic", "probability": 0.1}
            ],
            "gender": [
                {"category": "male", "probability": 0.5},
                {"category": "female", "probability": 0.5}
            ],
            "religion": [
                {"category": "christian", "probability": 0.8},
                {"category": "other", "probability": 0.2}
            ],
            "urbanization": [
                {"category": "rural", "probability": 0.7},
                {"category": "suburban", "probability": 0.3}
            ],
            "education_style": [
                {"category": "formal k-12", "probability": 0.6},
                {"category": "vocational", "probability": 0.4}
            ],
            "employment_style": [
                {"category": "blue-collar", "probability": 0.6},
                {"category": "white-collar", "probability": 0.2},
                {"category": "retired", "probability": 0.2}
            ],
            "location": "Rural Midwest"
        },
        num_agents=500,
        id=2
    )
    
    return [demographic1, demographic2]

def test_summarize_population():
    """Test that population summary works correctly"""
    # Create an example demographic distribution
    demographic = create_example_demographic()
    
    # Generate a summary
    summary = summarize_population(demographic, 1000, 4)
    
    # Check that the summary has the expected structure
    assert summary.total_agents == 1000
    assert len(summary.profiles) == 4
    
    # Check that the profiles have the expected structure
    for profile in summary.profiles:
        assert profile.name is not None
        assert profile.count > 0
        assert 0 < profile.percentage <= 100
        assert profile.age_range[0] <= profile.age_range[1]
        assert profile.income_range[0] <= profile.income_range[1]
        assert profile.education_years > 0
        assert "economic" in profile.political_leaning
        assert "governance" in profile.political_leaning
        assert "cultural" in profile.political_leaning
        assert len(profile.employment) > 0
        assert len(profile.religion) > 0
        assert len(profile.race_ethnicity) > 0
        assert len(profile.gender) > 0
        assert len(profile.urbanization) > 0
        assert len(profile.education_style) > 0

def test_summarize_multiple_demographics():
    """Test that multiple demographics summary works correctly"""
    # Create example demographics
    demographics = create_example_demographics_base()
    
    # Generate a summary
    summary = summarize_multiple_demographics(demographics, 3)
    
    # Check that the summary has the expected structure
    assert summary.total_agents == 1500  # 1000 + 500
    assert len(summary.demographic_buckets) == 2
    assert "Urban Professionals" in summary.demographic_buckets
    assert "Rural Conservatives" in summary.demographic_buckets
    
    # Check that each demographic bucket has the expected structure
    for name, bucket in summary.demographic_buckets.items():
        assert bucket.total_agents in [1000, 500]
        assert len(bucket.profiles) == 3

if __name__ == "__main__":
    # Run the demo
    demographic = create_example_demographic()
    
    # Generate a summary for 1000 agents with 4 representative buckets
    summary = summarize_population(demographic, 1000, 4)
    
    # Print the summary
    print("\n=== REPRESENTATIVE POPULATION BUCKETS ===\n")
    print(f"Total Agents: {summary.total_agents}")
    
    # Print representative profiles
    print("\n--- Representative Profiles ---\n")
    for profile in summary.profiles:
        print(format_profile_for_display(profile))
    
    # Generate a multi-demographic summary
    demographics = create_example_demographics_base()
    multi_summary = summarize_multiple_demographics(demographics, 3)
    
    # Print the multi-demographic summary
    print("\n=== MULTI-DEMOGRAPHIC REPRESENTATIVE BUCKETS ===\n")
    print(f"Total Agents Across All Demographics: {multi_summary.total_agents}")
    
    for demo_name, bucket in multi_summary.demographic_buckets.items():
        print(f"\n--- {demo_name} ---\n")
        for profile in bucket.profiles:
            print(format_profile_for_display(profile)) 