"""
Terminology Glossary
Provides explanations for technical terms used in reports
"""

GLOSSARY = {
    # Market Indicators
    "RSI": {
        "full_name": "Relative Strength Index",
        "description": "A momentum indicator that measures the speed and magnitude of price changes. Values range from 0-100.",
        "interpretation": "Above 70 = Overbought (price may fall), Below 30 = Oversold (price may rise), 40-60 = Neutral"
    },
    "MACD": {
        "full_name": "Moving Average Convergence Divergence",
        "description": "A trend-following indicator that shows the relationship between two moving averages of price.",
        "interpretation": "Bullish = Upward trend likely, Bearish = Downward trend likely"
    },
    "Bollinger Bands": {
        "full_name": "Bollinger Bands",
        "description": "Price channels that expand and contract based on market volatility.",
        "interpretation": "Upper = Resistance level, Middle = Average price, Lower = Support level. Price near upper band suggests overbought, near lower band suggests oversold."
    },
    "SMA": {
        "full_name": "Simple Moving Average",
        "description": "The average price over a specific time period, giving equal weight to all prices.",
        "interpretation": "Smooths out price data to identify the direction of the trend"
    },
    "EMA": {
        "full_name": "Exponential Moving Average",
        "description": "A moving average that gives more weight to recent prices, making it more responsive to new information.",
        "interpretation": "Reacts faster to price changes than SMA"
    },
    
    # Model Metrics
    "R² Score": {
        "full_name": "R-Squared (Coefficient of Determination)",
        "description": "Measures how well the model's predictions match the actual data. Ranges from 0 to 1.",
        "interpretation": "1.0 = Perfect predictions, 0.9+ = Excellent, 0.7-0.9 = Good, Below 0.7 = Needs improvement"
    },
    "RMSE": {
        "full_name": "Root Mean Square Error",
        "description": "Average prediction error in dollar terms. Lower is better.",
        "interpretation": "Shows typical prediction error. $5 RMSE means predictions are typically off by $5"
    },
    "MAE": {
        "full_name": "Mean Absolute Error",
        "description": "Average absolute difference between predicted and actual prices.",
        "interpretation": "Similar to RMSE but less sensitive to large errors. Lower is better."
    },
    "Ensemble": {
        "full_name": "Ensemble Model",
        "description": "Combines multiple prediction models by weighting their outputs based on performance.",
        "interpretation": "Usually more accurate than any single model alone"
    },
    
    # Trading Terms
    "Support": {
        "full_name": "Support Level",
        "description": "A price level where buying pressure is strong enough to prevent the price from falling further.",
        "interpretation": "Price tends to bounce up from support levels"
    },
    "Resistance": {
        "full_name": "Resistance Level",
        "description": "A price level where selling pressure is strong enough to prevent the price from rising further.",
        "interpretation": "Price tends to fall back from resistance levels"
    },
    "Volatility": {
        "full_name": "Price Volatility",
        "description": "The degree of variation in price over time. High volatility = large price swings.",
        "interpretation": "High volatility = Higher risk and potential reward, Low volatility = More stable prices"
    },
    "Trend": {
        "full_name": "Price Trend",
        "description": "The general direction of price movement over time.",
        "interpretation": "Bullish = Upward trend, Bearish = Downward trend, Neutral = Sideways movement"
    }
}

def get_term_explanation(term):
    """Get explanation for a technical term"""
    return GLOSSARY.get(term, None)

def generate_glossary_section():
    """Generate a markdown glossary section for reports"""
    glossary_md = """
## Terminology Guide

Understanding the technical terms used in this report:

"""
    
    categories = {
        "Market Indicators": ["RSI", "MACD", "Bollinger Bands", "SMA", "EMA"],
        "Model Performance": ["R² Score", "RMSE", "MAE", "Ensemble"],
        "Trading Concepts": ["Support", "Resistance", "Volatility", "Trend"]
    }
    
    for category, terms in categories.items():
        glossary_md += f"### {category}\n\n"
        for term in terms:
            if term in GLOSSARY:
                info = GLOSSARY[term]
                glossary_md += f"**{term}** ({info['full_name']})\n"
                glossary_md += f"- {info['description']}\n"
                glossary_md += f"- *How to read it:* {info['interpretation']}\n\n"
    
    return glossary_md

def add_inline_explanation(term, value):
    """Add inline explanation for a term with its value"""
    if term in GLOSSARY:
        info = GLOSSARY[term]
        return f"{term}: {value} - *{info['interpretation']}*"
    return f"{term}: {value}"
