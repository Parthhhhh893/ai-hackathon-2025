import os
import pandas as pd
import numpy as np
import joblib
import json
import shap
from flask import Flask, request, jsonify, render_template
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)


# Load the model and related artifacts
def load_model_artifacts():
    try:
        model = joblib.load('models/risk_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        explainer = joblib.load('models/shap_explainer.pkl')

        with open('models/feature_names.txt', 'r') as f:
            feature_names = [line.strip() for line in f.readlines()]

        return model, scaler, explainer, feature_names
    except Exception as e:
        print(f"Error loading model artifacts: {e}")
        return None, None, None, None


model, scaler, explainer, feature_names = load_model_artifacts()


@app.route('/api/predict', methods=['POST'])
def predict_risk():
    """
    API endpoint for risk prediction
    Input: JSON with buyer financial data
    Output: Risk score, approval decision, and feature importance
    """
    try:
        # Get data from request
        data = request.json

        # Convert to DataFrame
        buyer_data = pd.DataFrame([data])

        # Add derived features if not present
        if 'overdue_percent' not in buyer_data.columns and 'overdue_amount' in buyer_data.columns and 'outstanding_amount' in buyer_data.columns:
            buyer_data['overdue_percent'] = buyer_data['overdue_amount'] / buyer_data['outstanding_amount'] * 100

        if 'limit_to_sales_ratio' not in buyer_data.columns and 'limits_requested' in buyer_data.columns and 'sales_last_12m' in buyer_data.columns:
            buyer_data['limit_to_sales_ratio'] = buyer_data['limits_requested'] / buyer_data['sales_last_12m']

        if 'profit_margin' not in buyer_data.columns and 'net_profit' in buyer_data.columns and 'revenue' in buyer_data.columns:
            buyer_data['profit_margin'] = buyer_data['net_profit'] / buyer_data['revenue'] * 100

        # Select only features used by the model
        features_to_use = [f for f in feature_names if f in buyer_data.columns]
        missing_features = [f for f in feature_names if f not in buyer_data.columns]

        if missing_features:
            print(f"Warning: Missing features: {missing_features}")
            # Fill missing features with zeros
            for feature in missing_features:
                buyer_data[feature] = 0

        # Prepare features in the correct order
        features = buyer_data[feature_names].values

        # Scale features
        scaled_features = scaler.transform(features)

        # Make prediction
        probability = model.predict_proba(scaled_features)[0, 1]
        prediction = 1 if probability >= 0.5 else 0

        # Get SHAP values for explanation
        shap_values = explainer.shap_values(scaled_features)

        # Prepare SHAP values for response
        if isinstance(shap_values, list):  # For RandomForest
            shap_values_to_use = shap_values[1][0]
        else:  # For XGBoost
            shap_values_to_use = shap_values[0]

        # Create feature importance dictionary
        importance_dict = {}
        for i, feature in enumerate(feature_names):
            importance_dict[feature] = float(shap_values_to_use[i])

        # Sort by absolute importance
        sorted_importance = sorted(
            importance_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Get top factors
        top_factors = [
            {
                "feature": item[0],
                "impact": item[1],
                "direction": "increases risk" if item[1] < 0 else "decreases risk"
            }
            for item in sorted_importance[:5]  # Top 5 factors
        ]

        # Generate risk score (0-100)
        risk_score = min(100, max(0, int(probability * 100)))

        # Determine risk level
        risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 70 else "High"

        # Create response
        response = {
            "buyer_id": data.get("buyer_id", "Unknown"),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "approval_recommendation": "APPROVED" if prediction == 1 else "NOT_APPROVED",
            "approval_probability": float(probability),
            "top_factors": top_factors,
            "all_factors": dict(sorted_importance)
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    """
    API endpoint for batch risk prediction
    Input: JSON with array of buyer data
    Output: Array of risk predictions
    """
    try:
        # Get data from request
        data = request.json

        # Convert to DataFrame
        buyers_data = pd.DataFrame(data)

        # Process each buyer
        results = []
        for _, buyer in buyers_data.iterrows():
            # Convert Series to dict for individual prediction
            buyer_dict = buyer.to_dict()

            # Make prediction by calling the single prediction function
            response = predict_risk_internal(buyer_dict)
            results.append(response)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def predict_risk_internal(data):
    """
    Internal function for risk prediction
    """
    # Convert to DataFrame
    buyer_data = pd.DataFrame([data])

    # Add derived features if not present
    if 'overdue_percent' not in buyer_data.columns and 'overdue_amount' in buyer_data.columns and 'outstanding_amount' in buyer_data.columns:
        buyer_data['overdue_percent'] = buyer_data['overdue_amount'] / buyer_data['outstanding_amount'] * 100

    if 'limit_to_sales_ratio' not in buyer_data.columns and 'limits_requested' in buyer_data.columns and 'sales_last_12m' in buyer_data.columns:
        buyer_data['limit_to_sales_ratio'] = buyer_data['limits_requested'] / buyer_data['sales_last_12m']

    if 'profit_margin' not in buyer_data.columns and 'net_profit' in buyer_data.columns and 'revenue' in buyer_data.columns:
        buyer_data['profit_margin'] = buyer_data['net_profit'] / buyer_data['revenue'] * 100

    # Fill missing features with zeros
    for feature in feature_names:
        if feature not in buyer_data.columns:
            buyer_data[feature] = 0

    # Prepare features in the correct order
    features = buyer_data[feature_names].values

    # Scale features
    scaled_features = scaler.transform(features)

    # Make prediction
    probability = model.predict_proba(scaled_features)[0, 1]
    prediction = 1 if probability >= 0.5 else 0

    # Generate risk score (0-100)
    risk_score = min(100, max(0, int(probability * 100)))

    # Determine risk level
    risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 70 else "High"

    # Create response
    response = {
        "buyer_id": data.get("buyer_id", "Unknown"),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "approval_recommendation": "APPROVED" if prediction == 1 else "NOT_APPROVED",
        "approval_probability": float(probability)
    }

    return response


@app.route('/api/generate_explanation', methods=['POST'])
def generate_explanation():
    """
    Generate visual explanation for a specific buyer
    """
    try:
        # Get data from request
        data = request.json

        # Convert to DataFrame
        buyer_data = pd.DataFrame([data])

        # Add derived features
        if 'overdue_percent' not in buyer_data.columns and 'overdue_amount' in buyer_data.columns and 'outstanding_amount' in buyer_data.columns:
            buyer_data['overdue_percent'] = buyer_data['overdue_amount'] / buyer_data['outstanding_amount'] * 100

        if 'limit_to_sales_ratio' not in buyer_data.columns and 'limits_requested' in buyer_data.columns and 'sales_last_12m' in buyer_data.columns:
            buyer_data['limit_to_sales_ratio'] = buyer_data['limits_requested'] / buyer_data['sales_last_12m']

        if 'profit_margin' not in buyer_data.columns and 'net_profit' in buyer_data.columns and 'revenue' in buyer_data.columns:
            buyer_data['profit_margin'] = buyer_data['net_profit'] / buyer_data['revenue'] * 100

        # Fill missing features with zeros
        for feature in feature_names:
            if feature not in buyer_data.columns:
                buyer_data[feature] = 0

        # Prepare features
        features = buyer_data[feature_names].values

        # Scale features
        scaled_features = scaler.transform(features)

        # Get SHAP values
        shap_values = explainer.shap_values(scaled_features)

        # Create force plot
        plt.figure(figsize=(10, 3))
        if isinstance(shap_values, list):  # For RandomForest
            plot = shap.force_plot(
                explainer.expected_value[1],
                shap_values[1][0],
                buyer_data[feature_names].iloc[0],
                matplotlib=True,
                show=False
            )
        else:  # For XGBoost
            plot = shap.force_plot(
                explainer.expected_value,
                shap_values[0],
                buyer_data[feature_names].iloc[0],
                matplotlib=True,
                show=False
            )

        # Convert plot to image
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)

        # Convert to base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({"explanation_image": image_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    """
    Demo page for risk prediction
    """
    return render_template('index.html')


if __name__ == '__main__':
    # Make sure model is loaded
    if model is None:
        print("Error: Model could not be loaded. Please run the training script first.")
    else:
        # Start API server
        app.run(debug=True, port=5000)