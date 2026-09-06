import pandas as pd
import joblib

# Load the trained AI model
model = joblib.load("model/saferoute_model.pkl")


def predict_safety(
    crime_score,
    lighting_score,
    traffic_score,
    crowd_score,
    time_of_day,
    day_of_week,
    road_condition
):
    new_location = pd.DataFrame([{
        "crime_score": crime_score,
        "lighting_score": lighting_score,
        "traffic_score": traffic_score,
        "crowd_score": crowd_score,
        "time_of_day": time_of_day,
        "day_of_week": day_of_week,
        "road_condition": road_condition
    }])

    prediction = model.predict(new_location)

    return round(prediction[0], 2)

