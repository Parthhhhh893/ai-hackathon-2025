import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from datetime import datetime
import os
import sys

# Add the project root to the path so we can import from the models directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)


# Load the sample data
def load_sample_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['buyers']


# Extract features from financial data
def extract_features(buyer):
    features = {}

    # Basic buyer information
    features['years_in_business'] = buyer['years_in_business']
    features['requested_credit_limit'] = buyer['requested_credit_limit']
    features['requested_payment_terms'] = buyer['requested_payment_terms']

    # Latest year financial ratios (2024)
    latest_year = '2024'
    bs = buyer['financials'][latest_year]['balance_sheet']
    is_stmt = buyer['financials'][latest_year]['income_statement']
    cf = buyer['financials'][latest_year]['cash_flow']

    # Liquidity ratios
    features['current_ratio'] = bs['assets']['current_assets']['total_current_assets'] / \
                                bs['liabilities']['current_liabilities']['total_current_liabilities']
    features['quick_ratio'] = (bs['assets']['current_assets']['total_current_assets'] - bs['assets']['current_assets'][
        'inventory']) / bs['liabilities']['current_liabilities']['total_current_liabilities']

    # Solvency ratios
    features['debt_to_equity'] = bs['liabilities']['total_liabilities'] / bs['equity']['total_equity']
    features['debt_to_assets'] = bs['liabilities']['total_liabilities'] / bs['assets']['total_assets']

    # Profitability ratios
    features['gross_margin'] = is_stmt['gross_profit'] / is_stmt['revenue']
    features['net_margin'] = is_stmt['net_income'] / is_stmt['revenue']
    features['return_on_assets'] = is_stmt['net_income'] / bs['assets']['total_assets']
    features['return_on_equity'] = is_stmt['net_income'] / bs['equity']['total_equity']

    # Efficiency ratios
    features['asset_turnover'] = is_stmt['revenue'] / bs['assets']['total_assets']

    # Cash flow indicators
    features['operating_cash_flow_ratio'] = cf['operating_activities']['net_cash_from_operating'] / \
                                            bs['liabilities']['current_liabilities']['total_current_liabilities']
    features['cash_flow_to_debt'] = cf['operating_activities']['net_cash_from_operating'] / bs['liabilities'][
        'total_liabilities']

    # Year-over-year growth (2023 to 2024)
    prev_year = '2023'
    prev_is = buyer['financials'][prev_year]['income_statement']
    features['revenue_growth'] = (is_stmt['revenue'] - prev_is['revenue']) / prev_is['revenue']
    features['profit_growth'] = (is_stmt['net_income'] - prev_is['net_income']) / abs(prev_is['net_income']) if prev_is[
                                                                                                                    'net_income'] != 0 else 0

    # Payment behavior from bank statements
    features['avg_days_to_pay'] = buyer['bank_statements']['payment_patterns']['average_days_to_pay']
    features['payment_delays_count'] = buyer['bank_statements']['payment_patterns']['payment_delays_count']
    features['maximum_delay_days'] = buyer['bank_statements']['payment_patterns']['maximum_delay_days']

    # Bank statement indicators
    monthly_balances = [month['ending_balance'] for month in buyer['bank_statements']['monthly_balances']]
    features['avg_bank_balance'] = sum(monthly_balances) / len(monthly_balances)
    features['min_bank_balance'] = min(monthly_balances)
    features['balance_volatility'] = np.std(monthly_balances) / np.mean(monthly_balances) if np.mean(
        monthly_balances) > 0 else 0

    # Check if balance is declining
    first_half = monthly_balances[6:]  # More recent 6 months
    second_half = monthly_balances[:6]  # Older 6 months
    features['is_balance_declining'] = 1 if np.mean(first_half) < np.mean(second_half) else 0

    return features


# Build a simple risk model
def build_risk_model(buyers):
    # Extract features for all buyers
    X = []
    for buyer in buyers:
        features = extract_features(buyer)
        X.append(list(features.values()))

    # This is a simplified model - in a real scenario, you'd have labeled data
    # Here we're just building a sample model based on some rules
    # Note: This is not trained on real data, just for demonstration

    # Create a simple model (in reality, you'd train this on historical data)
    model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Create some synthetic labels based on rules (this is just for demonstration)
    # In reality, you'd use actual historical default data
    y = []
    for buyer in buyers:
        features = extract_features(buyer)

        # Simple rule-based risk assessment (for demonstration)
        risk_score = 0

        # Penalize high debt
        if features['debt_to_equity'] > 1.5:
            risk_score += 20

        # Penalize low liquidity
        if features['current_ratio'] < 1.0:
            risk_score += 15

        # Penalize payment delays
        risk_score += min(features['payment_delays_count'] * 5, 20)

        # Penalize declining cash balance
        if features['is_balance_declining']:
            risk_score += 10

        # Reward profitability
        if features['net_margin'] > 0.08:
            risk_score -= 10

        # Reward positive cash flow
        if features['operating_cash_flow_ratio'] > 0.2:
            risk_score -= 10

        # Normalize to 0-100 scale and add some randomness for demonstration
        risk_score = max(0, min(100, risk_score + 40 + np.random.randint(-10, 10)))

        y.append(1 if risk_score > 50 else 0)  # High risk = 1, Low risk = 0

    # Fit the model with our synthetic data
    model.fit(X, y)

    return model


# Function to calculate risk score for a buyer
def calculate_risk_score(buyer, model):
    features = extract_features(buyer)
    feature_values = list(features.values())

    # Get probability of default
    prob_default = model.predict_proba([feature_values])[0][1]

    # Convert to risk score (0-100)
    risk_score = int(prob_default * 100)

    # Risk level
    if risk_score < 30:
        risk_level = "Low"
        approval = "APPROVED"
    elif risk_score < 70:
        risk_level = "Medium"
        approval = "APPROVED WITH CAUTION"
    else:
        risk_level = "High"
        approval = "NOT APPROVED"

    # Calculate suggested credit limit based on risk
    requested_limit = buyer['requested_credit_limit']

    if risk_score < 30:
        suggested_limit = requested_limit  # Full amount for low risk
    elif risk_score < 50:
        suggested_limit = int(requested_limit * 0.8)  # 80% for medium-low risk
    elif risk_score < 70:
        suggested_limit = int(requested_limit * 0.6)  # 60% for medium-high risk
    else:
        suggested_limit = int(requested_limit * 0.3)  # 30% for high risk, if approved at all

    # Top risk factors (just examples for demonstration)
    risk_factors = []
    if features['debt_to_equity'] > 1.5:
        risk_factors.append(f"High debt-equity ratio ({features['debt_to_equity']:.1f})")
    if features['current_ratio'] < 1.2:
        risk_factors.append(f"Low current ratio ({features['current_ratio']:.1f})")
    if features['payment_delays_count'] > 2:
        risk_factors.append(f"Recent payment delays ({features['payment_delays_count']} occurrences)")
    if features['maximum_delay_days'] > 15:
        risk_factors.append(f"Long payment delays (up to {features['maximum_delay_days']} days)")
    if features['is_balance_declining']:
        risk_factors.append("Declining cash balance trend")
    if features['revenue_growth'] < 0:
        risk_factors.append(f"Negative revenue growth ({features['revenue_growth'] * 100:.1f}%)")

    # Add positive factors too
    positive_factors = []
    if features['net_margin'] > 0.08:
        positive_factors.append(f"Strong net margin ({features['net_margin'] * 100:.1f}%)")
    if features['operating_cash_flow_ratio'] > 0.2:
        positive_factors.append("Positive cash flow from operations")
    if features['revenue_growth'] > 0.1:
        positive_factors.append(f"Strong revenue growth ({features['revenue_growth'] * 100:.1f}%)")
    if features['current_ratio'] > 1.5:
        positive_factors.append(f"Healthy current ratio ({features['current_ratio']:.1f})")

    # Combine results
    result = {
        "buyer_id": buyer['buyer_id'],
        "buyer_name": buyer['buyer_name'],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "approval_recommendation": approval,
        "suggested_credit_limit": suggested_limit,
        "requested_credit_limit": requested_limit,
        "risk_factors": risk_factors[:4],  # Top 4 risk factors
        "positive_factors": positive_factors[:4]  # Top 4 positive factors
    }

    return result


def main():
    try:
        # Path to the sample data file
        sample_data_path = os.path.join(current_dir, 'sample_financial_data.json')

        print("Loading sample data...")
        buyers = load_sample_data(sample_data_path)

        print(f"Loaded {len(buyers)} buyer records")

        print("Building risk model...")
        model = build_risk_model(buyers)

        print("Model built successfully. Testing risk scoring...")

        # Test risk scoring for each buyer
        for i, buyer in enumerate(buyers):
            result = calculate_risk_score(buyer, model)

            print(f"\n--- Buyer {i + 1}: {result['buyer_name']} ---")
            print(f"Risk Score: {result['risk_score']}")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Recommendation: {result['approval_recommendation']}")
            print(
                f"Suggested Credit Limit: ${result['suggested_credit_limit']:,} (Requested: ${result['requested_credit_limit']:,})")

            print("Risk Factors:")
            for factor in result['risk_factors']:
                print(f"  - {factor}")

            print("Positive Factors:")
            for factor in result['positive_factors']:
                print(f"  - {factor}")

        print("\nRisk model testing completed successfully!")

        # Save all results to a file for review
        output_path = os.path.join(current_dir, 'test_results.json')
        all_results = [calculate_risk_score(buyer, model) for buyer in buyers]

        with open(output_path, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"Results saved to {output_path}")

    except Exception as e:
        print(f"Error during model testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()