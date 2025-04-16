def predict_risk_score_based_on_rule_engine(fetched_data_points, defined_rules, strict=False):
    """
    Predicts risk score and loan approval decision based on fetched data points and defined rules.

    Args:
        fetched_data_points (dict): Actual data points retrieved from the business
        defined_rules (dict): Defined threshold rules for approval
        strict (bool): Whether to use strict mode for evaluation

    Returns:
        dict: Decision output with verdict, credit limit, reason, and detailed criteria evaluation
    """
    # Initialize results
    result = {
        "verdict": "NEEDS_MANUAL_REVIEW",
        "credit_limit": None,
        "reason": "",
        "criteria": {}
    }

    # Track failures
    failures = []
    critical_failures = []
    total_criteria = 0
    passed_criteria = 0

    # Convert string values to appropriate types for comparison
    processed_data = _process_data_types(fetched_data_points)
    processed_rules = _process_data_types(defined_rules)

    # Evaluate each criterion
    for key, expected_value in processed_rules.items():
        total_criteria += 1
        actual_value = processed_data.get(key)

        # Skip if data point not available
        if actual_value is None:
            result["criteria"][key] = {
                "expected": expected_value,
                "actual": "Not available",
                "result": "Fail",
                "remark": "Data point not available"
            }
            failures.append(f"Missing data point: {key}")
            continue

        # Determine comparison logic based on data type and field
        comparison_result, remark = _compare_values(key, actual_value, expected_value)

        # Record the result
        result["criteria"][key] = {
            "expected": expected_value,
            "actual": actual_value,
            "result": "Pass" if comparison_result else "Fail",
            "remark": remark
        }

        if comparison_result:
            passed_criteria += 1
        else:
            failures.append(remark)

            # Mark critical failures (these are deal-breakers even in normal mode)
            if key in ["is_30_plus_dpd", "is_60_plus_dpd", "is_90_plus_dpd", "adverse_remarks_present"]:
                critical_failures.append(remark)

    # Determine verdict
    pass_percentage = (passed_criteria / total_criteria) * 100 if total_criteria > 0 else 0

    if strict and passed_criteria == total_criteria:
        result["verdict"] = "APPROVED"
        result["reason"] = "All criteria passed in strict mode."
    elif not strict:
        if not critical_failures and pass_percentage >= 80:
            result["verdict"] = "APPROVED"
            result[
                "reason"] = f"Passed {passed_criteria}/{total_criteria} criteria ({pass_percentage:.1f}%). No critical failures."
        elif not critical_failures and pass_percentage >= 60:
            result["verdict"] = "NEEDS_MANUAL_REVIEW"
            result[
                "reason"] = f"Passed {passed_criteria}/{total_criteria} criteria ({pass_percentage:.1f}%). Review recommended."
        else:
            result["verdict"] = "REJECTED"
            reason = f"Failed {total_criteria - passed_criteria}/{total_criteria} criteria."
            if critical_failures:
                reason += f" Critical failures: {', '.join(critical_failures)}"
            result["reason"] = reason
    else:
        result["verdict"] = "REJECTED"
        result["reason"] = f"Failed {total_criteria - passed_criteria}/{total_criteria} criteria in strict mode."

    # Calculate credit limit if approved
    if result["verdict"] == "APPROVED":
        result["credit_limit"] = _calculate_credit_limit(processed_data, processed_rules, pass_percentage)

    return result


def _process_data_types(data_dict):
    """Convert string values to appropriate types for comparison"""
    processed = {}
    for key, value in data_dict.items():
        if key in ["last_12_month_sales_in_rs", "business_vintage", "applicant_age", "proprietor_age"]:
            # Convert string numbers to integers
            processed[key] = int(value) if isinstance(value, str) else value
        elif key == "debt_to_turnover_ratio":
            # Convert string ratios to floats
            processed[key] = float(value) if isinstance(value, str) else value
        else:
            processed[key] = value
    return processed


def _compare_values(key, actual, expected):
    """Compare actual and expected values based on the type of data point"""
    # Boolean flags (like DPD indicators, adverse remarks) - actual should match expected
    if key in ["is_30_plus_dpd", "is_60_plus_dpd", "is_90_plus_dpd", "adverse_remarks_present", "debt_gt_one_year"]:
        if actual == expected:
            return True, f"{key.replace('_', ' ').title()} status is acceptable"
        else:
            return False, f"{key.replace('_', ' ').title()} status doesn't meet requirements"

    # Count fields (like credit enquiries, loans disbursed) - actual should be <= expected
    elif key in ["unsecured_credit_enquiries_90_days", "unsecured_loans_disbursed_3_months"]:
        if actual <= expected:
            return True, f"{key.replace('_', ' ').title()} count is within limits"
        else:
            return False, f"{key.replace('_', ' ').title()} count exceeds limits"

    # Turnover dip - actual should be <= expected (lower dip is better)
    elif key == "turnover_dip_percent_change":
        if actual <= expected:
            return True, f"Turnover dip is acceptable at {actual}%"
        else:
            return False, f"Turnover dip is too high at {actual}%"

    # Annual sales - actual should be >= expected (higher sales are better)
    elif key == "last_12_month_sales_in_rs":
        if actual >= expected:
            return True, f"Annual sales of Rs {actual:,} meet minimum requirements"
        else:
            return False, f"Annual sales of Rs {actual:,} below minimum requirement of Rs {expected:,}"

    # Debt-to-turnover ratio - actual should be <= expected (lower ratio is better)
    elif key == "debt_to_turnover_ratio":
        if actual <= expected:
            return True, f"Debt-to-turnover ratio of {actual} is acceptable"
        else:
            return False, f"Debt-to-turnover ratio of {actual} exceeds maximum of {expected}"

    # Business vintage, applicant age, proprietor age - actual should be >= expected
    elif key in ["business_vintage", "applicant_age", "proprietor_age"]:
        if actual >= expected:
            return True, f"{key.replace('_', ' ').title()} of {actual} meets minimum requirements"
        else:
            return False, f"{key.replace('_', ' ').title()} of {actual} below minimum requirement of {expected}"

    # Default case
    else:
        if actual == expected:
            return True, f"{key.replace('_', ' ').title()} meets requirements"
        else:
            return False, f"{key.replace('_', ' ').title()} doesn't meet requirements"


def _calculate_credit_limit(data, rules, pass_percentage):
    """
    Calculate credit limit based on business performance and risk assessment

    Logic:
    1. Base limit determined by annual sales (10-20% of annual sales)
    2. Adjusted by debt-to-turnover ratio
    3. Further adjusted by business vintage
    4. Capped based on risk profile from pass percentage
    """
    # Base calculation - start with 15% of annual sales
    annual_sales = data.get("last_12_month_sales_in_rs", 0)
    base_limit = annual_sales * 0.15

    # Adjustment factors
    adjustments = 1.0

    # Debt-to-turnover adjustment (lower is better)
    debt_ratio = data.get("debt_to_turnover_ratio", 0)
    max_debt_ratio = rules.get("debt_to_turnover_ratio", 2)
    if debt_ratio < max_debt_ratio * 0.5:  # Much better than threshold
        adjustments *= 1.2
    elif debt_ratio < max_debt_ratio * 0.75:  # Better than threshold
        adjustments *= 1.1
    elif debt_ratio > max_debt_ratio * 0.9:  # Close to threshold
        adjustments *= 0.9

    # Business vintage adjustment (higher is better)
    vintage = data.get("business_vintage", 0)
    min_vintage = rules.get("business_vintage", 2)
    if vintage >= min_vintage * 3:  # 3x minimum requirement
        adjustments *= 1.3
    elif vintage >= min_vintage * 2:  # 2x minimum requirement
        adjustments *= 1.2
    elif vintage >= min_vintage * 1.5:  # 1.5x minimum requirement
        adjustments *= 1.1

    # DPD history adjustment (any DPD reduces limit)
    if data.get("is_30_plus_dpd", False):
        adjustments *= 0.8

    # Turnover dip adjustment
    dip = data.get("turnover_dip_percent_change", 0)
    max_dip = rules.get("turnover_dip_percent_change", 75)
    if dip > max_dip * 0.8:  # Close to threshold
        adjustments *= 0.85

    # Apply adjustments
    adjusted_limit = base_limit * adjustments

    # Risk profile cap based on pass percentage
    if pass_percentage >= 95:
        cap_multiplier = 1.0  # No cap
    elif pass_percentage >= 90:
        cap_multiplier = 0.9
    elif pass_percentage >= 85:
        cap_multiplier = 0.8
    elif pass_percentage >= 80:
        cap_multiplier = 0.7
    else:
        cap_multiplier = 0.6

    final_limit = adjusted_limit * cap_multiplier

    # Round to nearest 10,000
    rounded_limit = round(final_limit / 10000) * 10000

    # Ensure minimum viable limit (if approved)
    if rounded_limit < 100000:
        rounded_limit = 100000

    # Format with commas for readability
    return f"Rs {rounded_limit:,.0f}"


# Example usage
if __name__ == "__main__":
    # Sample data
    fetched_data_points = {
        "is_30_plus_dpd": True,
        "is_60_plus_dpd": False,
        "is_90_plus_dpd": False,
        "adverse_remarks_present": False,
        "unsecured_credit_enquiries_90_days": 0,
        "unsecured_loans_disbursed_3_months": 0,
        "debt_gt_one_year": True,
        "turnover_dip_percent_change": 50,
        "last_12_month_sales_in_rs": "1500000",
        "debt_to_turnover_ratio": "3",
        "business_vintage": "5",
        "applicant_age": "30",
        "proprietor_age": "40"
    }

    defined_rules = {
        "is_30_plus_dpd": False,
        "is_60_plus_dpd": False,
        "is_90_plus_dpd": False,
        "adverse_remarks_present": False,
        "unsecured_credit_enquiries_90_days": 0,
        "unsecured_loans_disbursed_3_months": 0,
        "debt_gt_one_year": False,
        "turnover_dip_percent_change": 75,
        "last_12_month_sales_in_rs": "1000000",
        "debt_to_turnover_ratio": "2",
        "business_vintage": "2",
        "applicant_age": "25",
        "proprietor_age": "35"
    }

    # Test in normal mode
    normal_result = predict_risk_score_based_on_rule_engine(fetched_data_points, defined_rules, strict=False)
    print("Normal Mode Result:")
    import json

    print(json.dumps(normal_result, indent=2))

    # Test in strict mode
    strict_result = predict_risk_score_based_on_rule_engine(fetched_data_points, defined_rules, strict=True)
    print("\nStrict Mode Result:")
    print(json.dumps(strict_result, indent=2))