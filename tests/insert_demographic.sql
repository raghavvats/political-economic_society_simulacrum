INSERT INTO demographics (name, numerical_characteristics, categorical_characteristics, num_agents) VALUES (
  'US Urban Population', 
  '{
    "age": {
      "range": [18, 90],
      "points": [
        {"value": 25, "probability": 0.2},
        {"value": 35, "probability": 0.3},
        {"value": 45, "probability": 0.25},
        {"value": 65, "probability": 0.25}
      ]
    },
    "income_level": {
      "range": [20000, 200000],
      "points": [
        {"value": 30000, "probability": 0.3},
        {"value": 60000, "probability": 0.4},
        {"value": 120000, "probability": 0.3}
      ]
    },
    "years_of_education": {
      "range": [8, 22],
      "points": [
        {"value": 12, "probability": 0.4},
        {"value": 16, "probability": 0.4},
        {"value": 20, "probability": 0.2}
      ]
    },
    "religiosity": {
      "range": [0, 10],
      "points": [
        {"value": 2, "probability": 0.4},
        {"value": 5, "probability": 0.3},
        {"value": 8, "probability": 0.3}
      ]
    },
    "political_affiliation": {
      "economic": {
        "range": [0, 10],
        "points": [
          {"value": 3, "probability": 0.4},
          {"value": 5, "probability": 0.3},
          {"value": 7, "probability": 0.3}
        ]
      },
      "governance": {
        "range": [0, 10],
        "points": [
          {"value": 3, "probability": 0.35},
          {"value": 5, "probability": 0.35},
          {"value": 7, "probability": 0.3}
        ]
      },
      "cultural": {
        "range": [0, 10],
        "points": [
          {"value": 3, "probability": 0.45},
          {"value": 6, "probability": 0.3},
          {"value": 8, "probability": 0.25}
        ]
      }
    }
  }',
  '{
    "race_ethnicity": [
      {"category": "white", "probability": 0.6},
      {"category": "black", "probability": 0.15},
      {"category": "hispanic", "probability": 0.15},
      {"category": "east_asian", "probability": 0.05},
      {"category": "south_asian", "probability": 0.05}
    ],
    "gender": [
      {"category": "male", "probability": 0.48},
      {"category": "female", "probability": 0.48},
      {"category": "nonbinary", "probability": 0.03},
      {"category": "other", "probability": 0.01}
    ],
    "religion": [
      {"category": "christian", "probability": 0.65},
      {"category": "jewish", "probability": 0.05},
      {"category": "muslim", "probability": 0.03},
      {"category": "buddhist", "probability": 0.02},
      {"category": "hindu", "probability": 0.02},
      {"category": "other", "probability": 0.23}
    ],
    "urbanization": [
      {"category": "urban", "probability": 0.8},
      {"category": "suburban", "probability": 0.2}
    ],
    "education_style": [
      {"category": "formal_k12", "probability": 0.3},
      {"category": "formal_k12_university", "probability": 0.6},
      {"category": "vocational", "probability": 0.1}
    ],
    "employment_style": [
      {"category": "white_collar", "probability": 0.5},
      {"category": "blue_collar", "probability": 0.2},
      {"category": "entrepreneur", "probability": 0.1},
      {"category": "self_employed", "probability": 0.1},
      {"category": "executive", "probability": 0.05},
      {"category": "unemployed", "probability": 0.05}
    ],
    "location": "New York City"
  }',
  1000
); 