from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
from collections import defaultdict, Counter
from pydantic import BaseModel
import math
from sklearn.cluster import KMeans

from backend.core.schemas import (
    DemographicDistribution,
    CategoricalProbabilityWithEnum,
    DistributionData,
    PoliticalAffiliationDistribution,
    DemographicsBase,
    NumericalCharacteristicsDistribution,
    CategoricalCharacteristicsDistribution,
    ProbabilityPoint,
    RaceEthnicity,
    Gender,
    Religion,
    Urbanization,
    EducationStyle
)

class RepresentativeProfile(BaseModel):
    """Profile representing a subgroup of the population"""
    name: str
    count: int
    percentage: float
    age_range: Tuple[float, float]
    income_range: Tuple[float, float]
    education_years: float
    political_leaning: Dict[str, float]
    employment: Dict[str, float]
    religion: Dict[str, float]
    race_ethnicity: Dict[str, float]
    gender: Dict[str, float]
    urbanization: Dict[str, float]
    education_style: Dict[str, float]
    
class PopulationBuckets(BaseModel):
    """Representative buckets of a population"""
    total_agents: int
    profiles: List[RepresentativeProfile]

class MultiPopulationBuckets(BaseModel):
    """Representative buckets for multiple demographics"""
    demographic_buckets: Dict[str, PopulationBuckets]
    total_agents: int

def summarize_population(
    characteristics: DemographicDistribution, 
    num_agents: int = 5000,
    num_buckets: int = 4
) -> PopulationBuckets:
    """
    Summarize a demographic split into representative population buckets.
    
    This function groups the population into meaningful buckets that represent
    distinct subgroups with shared profiles, instead of displaying individual
    characteristics separately.
    
    Args:
        characteristics: The demographic characteristics defining the population
        num_agents: The total number of agents to simulate
        num_buckets: The number of representative buckets to create
        
    Returns:
        A structured summary of representative population buckets
    """
    # Generate synthetic agents based on the distributions
    synthetic_agents = generate_synthetic_agents(characteristics, num_agents)
    
    # Group agents into representative buckets
    profiles = create_representative_profiles(synthetic_agents, num_buckets)
    
    return PopulationBuckets(
        total_agents=num_agents,
        profiles=profiles
    )

def summarize_multiple_demographics(
    demographics_list: List[DemographicsBase],
    num_buckets_per_demographic: int = 3
) -> MultiPopulationBuckets:
    """
    Summarize multiple demographic splits into representative population buckets.
    
    Args:
        demographics_list: List of demographic splits to summarize
        num_buckets_per_demographic: Number of buckets to create per demographic
        
    Returns:
        A summary of all demographic splits with representative buckets
    """
    buckets = {}
    total_agents = 0
    
    for demographic in demographics_list:
        # Convert the stored characteristics to DemographicDistribution
        demographic_distribution = DemographicDistribution(
            numerical=demographic.numerical_characteristics,
            categorical=demographic.categorical_characteristics
        )
        
        # Summarize this demographic split
        summary = summarize_population(
            demographic_distribution, 
            demographic.num_agents,
            num_buckets_per_demographic
        )
        
        # Add to the collection of summaries
        buckets[demographic.name] = summary
        total_agents += demographic.num_agents
    
    return MultiPopulationBuckets(
        demographic_buckets=buckets,
        total_agents=total_agents
    )

def generate_synthetic_agents(
    characteristics: DemographicDistribution, 
    num_agents: int
) -> List[Dict[str, Any]]:
    """
    Generate synthetic agents based on the demographic distribution.
    
    This doesn't create full agent objects but rather simplified representations
    for the purpose of clustering and summarization.
    
    Args:
        characteristics: The demographic characteristics
        num_agents: Number of agents to generate
        
    Returns:
        List of synthetic agents with their characteristics
    """
    agents = []
    
    # Generate numerical characteristics
    numerical_chars = characteristics.numerical
    
    # Sample from distributions
    ages = sample_from_distribution(numerical_chars.age, num_agents)
    incomes = sample_from_distribution(numerical_chars.income_level, num_agents)
    education_years = sample_from_distribution(numerical_chars.years_of_education, num_agents)
    religiosity = sample_from_distribution(numerical_chars.religiosity, num_agents)
    
    # Political affiliation
    economic = sample_from_distribution(numerical_chars.political_affiliation.economic, num_agents)
    governance = sample_from_distribution(numerical_chars.political_affiliation.governance, num_agents)
    cultural = sample_from_distribution(numerical_chars.political_affiliation.cultural, num_agents)
    
    # Generate categorical characteristics
    categorical_chars = characteristics.categorical
    
    # Sample from categorical distributions
    race_ethnicities = sample_from_categorical(categorical_chars.race_ethnicity, num_agents)
    genders = sample_from_categorical(categorical_chars.gender, num_agents)
    religions = sample_from_categorical(categorical_chars.religion, num_agents)
    urbanizations = sample_from_categorical(categorical_chars.urbanization, num_agents)
    education_styles = sample_from_categorical(categorical_chars.education_style, num_agents)
    employment_styles = sample_from_categorical(categorical_chars.employment_style, num_agents)
    
    # Combine all characteristics into agents
    for i in range(num_agents):
        agent = {
            "age": ages[i],
            "income": incomes[i],
            "education_years": education_years[i],
            "religiosity": religiosity[i],
            "political_economic": economic[i],
            "political_governance": governance[i],
            "political_cultural": cultural[i],
            "race_ethnicity": race_ethnicities[i],
            "gender": genders[i],
            "religion": religions[i],
            "urbanization": urbanizations[i],
            "education_style": education_styles[i],
            "employment_style": employment_styles[i],
            "location": categorical_chars.location
        }
        agents.append(agent)
    
    return agents

def sample_from_distribution(
    distribution: DistributionData, 
    num_samples: int
) -> List[float]:
    """
    Sample values from a distribution deterministically.
    
    Args:
        distribution: The probability distribution
        num_samples: Number of samples to generate
        
    Returns:
        List of sampled values
    """
    values = []
    
    # Calculate how many samples to generate for each point
    for point in distribution.points:
        count = round(point.probability * num_samples)
        values.extend([point.value] * count)
    
    # Adjust for rounding errors
    while len(values) < num_samples:
        # Add values from the highest probability point
        max_prob_point = max(distribution.points, key=lambda p: p.probability)
        values.append(max_prob_point.value)
    
    # If we have too many values, remove some
    if len(values) > num_samples:
        values = values[:num_samples]
    
    return values

def sample_from_categorical(
    distribution: List[CategoricalProbabilityWithEnum], 
    num_samples: int
) -> List[str]:
    """
    Sample categories from a categorical distribution deterministically.
    
    Args:
        distribution: The categorical probability distribution
        num_samples: Number of samples to generate
        
    Returns:
        List of sampled categories
    """
    categories = []
    
    # Calculate how many samples to generate for each category
    for cat_prob in distribution:
        count = round(cat_prob.probability * num_samples)
        categories.extend([cat_prob.category] * count)
    
    # Adjust for rounding errors
    while len(categories) < num_samples:
        # Add categories from the highest probability category
        max_prob_cat = max(distribution, key=lambda c: c.probability)
        categories.append(max_prob_cat.category)
    
    # If we have too many categories, remove some
    if len(categories) > num_samples:
        categories = categories[:num_samples]
    
    return categories

def create_representative_profiles(
    agents: List[Dict[str, Any]], 
    num_profiles: int
) -> List[RepresentativeProfile]:
    """
    Create representative profiles from synthetic agents.
    
    This function uses clustering to group similar agents together and
    then creates a representative profile for each cluster.
    
    Args:
        agents: List of synthetic agents
        num_profiles: Number of representative profiles to create
        
    Returns:
        List of representative profiles
    """
    # Extract numerical features for clustering
    features = []
    for agent in agents:
        # Normalize features to have similar scales
        feature = [
            agent["age"] / 100,  # Normalize age
            agent["income"] / 100000,  # Normalize income
            agent["education_years"] / 20,  # Normalize education
            agent["political_economic"],  # Already in range [-1, 1]
            agent["political_governance"],  # Already in range [-1, 1]
            agent["political_cultural"],  # Already in range [-1, 1]
            agent["religiosity"] / 10  # Normalize religiosity
        ]
        features.append(feature)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=num_profiles, random_state=42)
    cluster_labels = kmeans.fit_predict(features)
    
    # Group agents by cluster
    clusters = defaultdict(list)
    for i, label in enumerate(cluster_labels):
        clusters[label].append(agents[i])
    
    # Create representative profiles
    profiles = []
    total_agents = len(agents)
    
    for cluster_id, cluster_agents in clusters.items():
        # Calculate cluster size
        cluster_size = len(cluster_agents)
        percentage = (cluster_size / total_agents) * 100
        
        # Calculate age range
        ages = [agent["age"] for agent in cluster_agents]
        age_min, age_max = min(ages), max(ages)
        
        # Calculate income range
        incomes = [agent["income"] for agent in cluster_agents]
        income_min, income_max = min(incomes), max(incomes)
        
        # Calculate average education years
        avg_education = sum(agent["education_years"] for agent in cluster_agents) / cluster_size
        
        # Calculate average political leaning
        avg_economic = sum(agent["political_economic"] for agent in cluster_agents) / cluster_size
        avg_governance = sum(agent["political_governance"] for agent in cluster_agents) / cluster_size
        avg_cultural = sum(agent["political_cultural"] for agent in cluster_agents) / cluster_size
        
        # Count categorical characteristics
        employment_counter = Counter([agent["employment_style"] for agent in cluster_agents])
        religion_counter = Counter([agent["religion"] for agent in cluster_agents])
        race_counter = Counter([agent["race_ethnicity"] for agent in cluster_agents])
        gender_counter = Counter([agent["gender"] for agent in cluster_agents])
        urbanization_counter = Counter([agent["urbanization"] for agent in cluster_agents])
        education_style_counter = Counter([agent["education_style"] for agent in cluster_agents])
        
        # Convert counters to percentages
        employment_pct = {k: (v / cluster_size) * 100 for k, v in employment_counter.items()}
        religion_pct = {k: (v / cluster_size) * 100 for k, v in religion_counter.items()}
        race_pct = {k: (v / cluster_size) * 100 for k, v in race_counter.items()}
        gender_pct = {k: (v / cluster_size) * 100 for k, v in gender_counter.items()}
        urbanization_pct = {k: (v / cluster_size) * 100 for k, v in urbanization_counter.items()}
        education_style_pct = {k: (v / cluster_size) * 100 for k, v in education_style_counter.items()}
        
        # Determine cluster name based on dominant characteristics
        dominant_employment = max(employment_counter.items(), key=lambda x: x[1])[0]
        dominant_age = "Young" if age_max < 35 else "Middle-Aged" if age_max < 60 else "Senior"
        dominant_urbanization = max(urbanization_counter.items(), key=lambda x: x[1])[0]
        
        # Political leaning description
        political_desc = ""
        if abs(avg_economic) < 0.2 and abs(avg_cultural) < 0.2:
            political_desc = "Centrist"
        elif avg_economic < -0.2 and avg_cultural < -0.2:
            political_desc = "Progressive"
        elif avg_economic > 0.2 and avg_cultural > 0.2:
            political_desc = "Conservative"
        elif avg_economic < -0.2 and avg_cultural > 0.2:
            political_desc = "Socially Conservative, Economically Liberal"
        elif avg_economic > 0.2 and avg_cultural < -0.2:
            political_desc = "Socially Liberal, Economically Conservative"
        else:
            political_desc = "Mixed Political Views"
        
        # Create profile name
        profile_name = f"{dominant_age} {dominant_urbanization.title()} {dominant_employment.title()} ({political_desc})"
        
        # Create the profile
        profile = RepresentativeProfile(
            name=profile_name,
            count=cluster_size,
            percentage=percentage,
            age_range=(age_min, age_max),
            income_range=(income_min, income_max),
            education_years=avg_education,
            political_leaning={
                "economic": avg_economic,
                "governance": avg_governance,
                "cultural": avg_cultural
            },
            employment=employment_pct,
            religion=religion_pct,
            race_ethnicity=race_pct,
            gender=gender_pct,
            urbanization=urbanization_pct,
            education_style=education_style_pct
        )
        
        profiles.append(profile)
    
    # Sort profiles by size (descending)
    profiles.sort(key=lambda p: p.count, reverse=True)
    
    return profiles

def format_profile_for_display(profile: RepresentativeProfile) -> str:
    """
    Format a representative profile for display.
    
    Args:
        profile: The representative profile
        
    Returns:
        Formatted string representation of the profile
    """
    # Format age range
    age_range = f"{int(profile.age_range[0])}-{int(profile.age_range[1])}"
    
    # Format income range (in thousands)
    income_min_k = f"${int(profile.income_range[0]/1000)}K"
    income_max_k = f"${int(profile.income_range[1]/1000)}K"
    income_range = f"{income_min_k}-{income_max_k}"
    
    # Format education
    education = f"{profile.education_years:.1f} years"
    
    # Format political leaning
    economic = profile.political_leaning["economic"]
    cultural = profile.political_leaning["cultural"]
    governance = profile.political_leaning["governance"]
    political = f"Economic: {economic:.1f}, Cultural: {cultural:.1f}, Governance: {governance:.1f}"
    
    # Format top 3 categories for each categorical characteristic
    def format_top_categories(categories: Dict[str, float], limit: int = 3) -> str:
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:limit]
        return ", ".join([f"{cat} {pct:.0f}%" for cat, pct in sorted_cats])
    
    employment = format_top_categories(profile.employment)
    religion = format_top_categories(profile.religion)
    race = format_top_categories(profile.race_ethnicity)
    gender = format_top_categories(profile.gender)
    urbanization = format_top_categories(profile.urbanization)
    education_style = format_top_categories(profile.education_style)
    
    # Build the formatted string
    formatted = f"""**{profile.name} ({profile.count} agents, {profile.percentage:.1f}%)**
   - Age: {age_range}
   - Income: {income_range}
   - Education: {education}
   - Political Leaning: {political}
   - Employment: {employment}
   - Religion: {religion}
   - Race/Ethnicity: {race}
   - Gender: {gender}
   - Urbanization: {urbanization}
   - Education Style: {education_style}
"""
    
    return formatted

# Example usage and output demonstration
def example_summary():
    """
    Demonstrate how the population summary functions work with example data.
    
    Returns:
        An example summary of a demographic split with representative buckets
    """
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
    characteristics = DemographicDistribution(
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
    
    # Generate the summary for 1000 agents with 4 representative buckets
    summary = summarize_population(characteristics, 1000, 4)
    
    # Create a second demographic for demonstration
    characteristics2 = DemographicDistribution(
        numerical=NumericalCharacteristicsDistribution(
            age=DistributionData(range=[18, 80], points=[
                ProbabilityPoint(value=25, probability=0.4),
                ProbabilityPoint(value=45, probability=0.4),
                ProbabilityPoint(value=65, probability=0.2)
            ]),
            income_level=DistributionData(range=[20000, 200000], points=[
                ProbabilityPoint(value=40000, probability=0.5),
                ProbabilityPoint(value=80000, probability=0.3),
                ProbabilityPoint(value=120000, probability=0.2)
            ]),
            years_of_education=DistributionData(range=[8, 22], points=[
                ProbabilityPoint(value=10, probability=0.2),
                ProbabilityPoint(value=14, probability=0.5),
                ProbabilityPoint(value=18, probability=0.3)
            ]),
            religiosity=DistributionData(range=[0, 10], points=[
                ProbabilityPoint(value=3, probability=0.4),
                ProbabilityPoint(value=7, probability=0.6)
            ]),
            political_affiliation=PoliticalAffiliationDistribution(
                economic=DistributionData(range=[-1, 1], points=[
                    ProbabilityPoint(value=-0.7, probability=0.6),
                    ProbabilityPoint(value=0.3, probability=0.4)
                ]),
                governance=DistributionData(range=[-1, 1], points=[
                    ProbabilityPoint(value=-0.5, probability=0.5),
                    ProbabilityPoint(value=0.5, probability=0.5)
                ]),
                cultural=DistributionData(range=[-1, 1], points=[
                    ProbabilityPoint(value=-0.6, probability=0.7),
                    ProbabilityPoint(value=0.4, probability=0.3)
                ])
            )
        ),
        categorical=CategoricalCharacteristicsDistribution(
            race_ethnicity=[
                CategoricalProbabilityWithEnum(category="white", probability=0.7),
                CategoricalProbabilityWithEnum(category="black", probability=0.2),
                CategoricalProbabilityWithEnum(category="hispanic", probability=0.1)
            ],
            gender=[
                CategoricalProbabilityWithEnum(category="male", probability=0.5),
                CategoricalProbabilityWithEnum(category="female", probability=0.5)
            ],
            religion=[
                CategoricalProbabilityWithEnum(category="christian", probability=0.8),
                CategoricalProbabilityWithEnum(category="other", probability=0.2)
            ],
            urbanization=[
                CategoricalProbabilityWithEnum(category="rural", probability=0.7),
                CategoricalProbabilityWithEnum(category="suburban", probability=0.3)
            ],
            education_style=[
                CategoricalProbabilityWithEnum(category="formal k-12", probability=0.6),
                CategoricalProbabilityWithEnum(category="vocational", probability=0.4)
            ],
            employment_style=[
                CategoricalProbabilityWithEnum(category="blue-collar", probability=0.6),
                CategoricalProbabilityWithEnum(category="white-collar", probability=0.2),
                CategoricalProbabilityWithEnum(category="retired", probability=0.2)
            ],
            location="Rural Midwest"
        )
    )
    
    # Create example demographics
    demographics1 = DemographicsBase(
        name="Urban Professionals",
        numerical_characteristics=characteristics.numerical.dict(),
        categorical_characteristics=characteristics.categorical.dict(),
        num_agents=1000
    )
    
    demographics2 = DemographicsBase(
        name="Rural Conservatives",
        numerical_characteristics=characteristics2.numerical.dict(),
        categorical_characteristics=characteristics2.categorical.dict(),
        num_agents=500
    )
    
    # Generate multi-demographic summary
    multi_summary = summarize_multiple_demographics([demographics1, demographics2], 3)
    
    # Format the profiles for display
    formatted_profiles = []
    for profile in summary.profiles:
        formatted_profiles.append(format_profile_for_display(profile))
    
    # Format the multi-demographic profiles
    formatted_multi_profiles = {}
    for demo_name, demo_buckets in multi_summary.demographic_buckets.items():
        formatted_multi_profiles[demo_name] = []
        for profile in demo_buckets.profiles:
            formatted_multi_profiles[demo_name].append(format_profile_for_display(profile))
    
    # Return both for demonstration
    return {
        "single_demographic_summary": {
            "total_agents": summary.total_agents,
            "profiles": formatted_profiles
        },
        "multi_demographic_summary": {
            "total_agents": multi_summary.total_agents,
            "demographics": formatted_multi_profiles
        }
    } 