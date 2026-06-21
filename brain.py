def decision_engine(batch):
    """
    V3.9 AI决策层（简化版）
    """
    score = 75  # mock AI score

    if score > 70:
        action = "INCREASE_BID"
    elif score > 40:
        action = "HOLD"
    else:
        action = "REDUCE"

    return {
        "action": action,
        "score": score,
        "reason": "V3.9 AI simulated decision"
    }
