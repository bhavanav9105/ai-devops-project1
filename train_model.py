import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Extended training dataset with 7 features mapped to 3
data = {
    "Marketing_Spend": [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000],
    "Customer_Visits": [60, 100, 130, 150, 175, 200, 225, 250, 270, 300, 340, 380],
    "Product_Price":   [8, 10, 10, 10, 12, 12, 12, 12, 14, 15, 15, 16],
    "Sales":           [1000, 2000, 3200, 4000, 5000, 6000, 7200, 8000, 9200, 10000, 12000, 14000]
}

df = pd.DataFrame(data)
X  = df[["Marketing_Spend", "Customer_Visits", "Product_Price"]]
y  = df["Sales"]

model = LinearRegression()
model.fit(X, y)

pickle.dump(model, open("sales_model.pkl", "wb"))
print("✅ Model trained and saved!")
print(f"   R² score: {model.score(X, y):.4f}")
