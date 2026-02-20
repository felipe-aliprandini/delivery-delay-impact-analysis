import sqlite3
import pandas as pd
from scipy.stats import pearsonr
import statsmodels.api as sm

conn = sqlite3.connect("olist.db")

query = """
SELECT
    ROUND(julianday(order_delivered_customer_date)
    -julianday(order_estimated_delivery_date)) AS days_diff,
    r.review_score
FROM 
    orders AS o
JOIN 
    order_reviews as r
        ON o.order_id = r.order_id
WHERE 
    o.order_status = 'delivered'
    AND order_estimated_delivery_date IS NOT NULL
    AND order_delivered_customer_date IS NOT NULL;
"""
df = pd.read_sql(query, conn)

# =====================
# # Pearson Correlation Analysis
# =====================

corr, p_value = pearsonr(df["days_diff"], df["review_score"])

print("Correlação:", corr)
print("p-value:", p_value)

# =====================
# Piecewise Linear Regression Model
# =====================

df["late_days"] = df["days_diff"].apply(lambda x: x if x > 0 else 0)
df["early_days"] = df["days_diff"].apply(lambda x: x if x < 0 else 0)

X = sm.add_constant(df[["late_days", "early_days"]])
model = sm.OLS(df["review_score"], X).fit()
print(model.summary())


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# Create piecewise variables
df["late_days"] = df["days_diff"].clip(lower=0)
df["early_days"] = df["days_diff"].clip(upper=0)

# Adjust Model
X = sm.add_constant(df[["late_days", "early_days"]])
model = sm.OLS(df["review_score"], X).fit()

# Generate smooth prediction grid
x_vals = np.linspace(-30, 30, 300)

plot_df = pd.DataFrame({
    "late_days": np.where(x_vals > 0, x_vals, 0),
    "early_days": np.where(x_vals < 0, x_vals, 0)
})

X_plot = sm.add_constant(plot_df)
X_plot = X_plot[model.model.exog_names]

plot_df["days_diff"] = x_vals
plot_df["predicted"] = model.predict(X_plot)

# Plot
plt.figure(figsize=(8,5))

# Scatter with sample 
sample_df = df.sample(5000)
sns.scatterplot(
    data=sample_df,
    x="days_diff",
    y="review_score",
    alpha=0.2
)

# Model prediction line
sns.lineplot(
    data=plot_df,
    x="days_diff",
    y="predicted"
)

plt.ylim(1,5)
plt.title("Asymmetric Impact of Delivery Timing on Customer Ratings")
plt.xlabel("Delivery Difference (Days)")
plt.ylabel("Predicted Review Score")
plt.tight_layout()
plt.show()
