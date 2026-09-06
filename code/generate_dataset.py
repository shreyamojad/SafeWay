import pandas as pd
import random

data = []

for i in range(500):
    crime = random.randint(0, 100)
    lighting = random.randint(0, 100)
    traffic = random.randint(0, 100)
    crowd = random.randint(0, 100)
    time = random.randint(0, 23)
    day = random.randint(1, 7)
    road = random.randint(0, 100)

    safety = (
        (100 - crime) * 0.30
        + lighting * 0.20
        + (100 - traffic) * 0.15
        + (100 - crowd) * 0.15
        + road * 0.20
    )

    safety = round(safety)

    data.append([
        crime,
        lighting,
        traffic,
        crowd,
        time,
        day,
        road,
        safety
    ])

columns = [
    "crime_score",
    "lighting_score",
    "traffic_score",
    "crowd_score",
    "time_of_day",
    "day_of_week",
    "road_condition",
    "safety_score"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("dataset/saferoute_dataset.csv", index=False)

print("Dataset generated successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))