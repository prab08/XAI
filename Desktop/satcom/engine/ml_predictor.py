import numpy as np
from sklearn.ensemble import RandomForestRegressor

def train_satcom_ai():
    """
    Trains a Machine Learning model to predict optimal bandwidth allocation.
    In production, this would be trained on months of historical teleport data.
    """
    # X Training Features: [Priority (1-3), Base Demand (Mbps), Weather Severity (1-3)]
    X_train = np.array([
        [1, 250, 1], [1, 250, 3],  # High Priority, Clear vs Storm
        [2, 180, 1], [2, 180, 2],  # Med Priority, Clear vs Overcast
        [3, 150, 1], [3, 150, 3],  # Low Priority, Clear vs Storm
        [1, 300, 1], [1, 300, 2],  # High Priority, Clear vs Overcast
    ])

    # y Target Labels: [Optimal Bandwidth Allocation (MHz)]
    # Notice how the AI is trained to give MORE bandwidth to Priority 1 links during storms (Severity 3)
    y_train = np.array([
        80.0, 120.0,
        60.0, 75.0,
        45.0, 30.0,   # Low priority gets throttled during storms to save system power
        95.0, 110.0
    ])

    # Initialize and train the Random Forest AI
    ai_model = RandomForestRegressor(n_estimators=50, random_state=42)
    ai_model.fit(X_train, y_train)
    return ai_model

def predict_allocation(ai_model, live_telemetry):
    """Passes live teleport data into the trained AI to predict bandwidth."""
    allocations = {}
    for name, data in live_telemetry.items():
        # Format the live data for the ML model
        features = np.array([[data['priority'], data['base_demand'], data['weather_severity']]])

        # AI makes the prediction
        predicted_bw = ai_model.predict(features)[0]

        allocations[name] = {
            "predicted_bw_mhz": predicted_bw,
            "modcod": data["modcod"],
            "fade_db": data["rain_fade_db"],
            "priority": data["priority"]
        }
    return allocations