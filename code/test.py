import pandas as pd
import joblib

model = joblib.load("model/saferoute_model.pkl")

new_location = pd.DataFrame([{
    "crime_score": 30,
    "lighting_score": 80,
    "traffic_score": 40,
    "crowd_score": 30,
    "time_of_day": 18,
    "day_of_week": 3,
    "road_condition": 85
}])

prediction = model.predict(new_location)

print("Predicted Safety Score:", round(prediction[0], 2))