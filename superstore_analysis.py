import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# visual style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10,20)
# Data Cleaning and 
df = pd.read_csv("/workspaces/Superstore-Sales-Analysis/Sample - Superstore.csv",encoding='latin1')
print(f"Satrting data formate(Rows, Coloumn):{df.shape}")
# Removing duplicate values
df.drop_duplicates(inplace= True)
# Removing spaces and dash form data for easy to write query squlite
a= df.columns = [col.replace(' ','_').replace('-','_') for col in df.columns]
# converting order date and formating and getting year/month
df["Order_Date"]=pd.to_datetime(df["Order_Date"],errors="coerce")
df["Order_Year"]=df["Order_Date"].dt.year
df["Order_Month"]=df["Order_Date"].dt.to_period('M').astype(str)
# New Coloumn :Profit_Margin
df['Profit_Margin'] = round((df['Profit']/df['Sales']) * 100,2)
print("Data Cleaning is complited and print first 3 data:")
print(df[['Order_ID','Category','Sub_Category','Sales','Profit','Profit_Margin']].head(3))
print("-" * 60)
conn = sqlite3.connect(':memory:')
print("check connection:",conn)
# after cleaning data set adding in 'superstore' table sqlite3 database
df.to_sql('superstore', conn, index=False,if_exists = 'replace')
# --------------sql query1: for all sales, all profit, total orders -------------------
query_kpi = """
SELECT
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Overall_Margin_Pct
FROM superstore;
"""
# query_kpi = """
# SELECT 
#     COUNT(DISTINCT Order_ID) AS Total_Orders,
#     ROUND(SUM(Sales), 2) AS Total_Sales,
#     ROUND(SUM(Profit), 2) AS Total_Profit,
#     ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Overall_Margin_Pct
# FROM superstore;
# """
print(" Over all Business KPIs(SQL Output):")
print(pd.read_sql_query(query_kpi, conn))
print("-" * 60)
# -----------------Query 2 for sales profit accordin to category---------------
query_category = """
SELECT
    Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM superstore
GROUP BY Category
ORDER BY Total_Profit DESC;
"""
df_category = pd.read_sql_query(query_category, conn)
print("Sql output category wise :")
print(df_category)
print("-" * 60)
# Query for top 5 loss of subcategory wise
query_loss = """
SELECT
    Sub_Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(AVG(Discount) * 100, 1) AS Avg_Discount_Pct
FROM superstore
GROUP BY Sub_Category
HAVING SUM(Profit) < 0
ORDER BY Total_Profit ASC;
"""
df_loss = pd.read_sql_query(query_loss, conn)
print("product witch is running in loss")
print(df_loss)
# ------------- Top 5 City Where Highest Sales--------------------
query_cities="""
SELECT
    City,
    State,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM superstore
GROUP BY City, State
ORDER BY Total_Sales DESC
LIMIT 5;
"""

df_cities =pd.read_sql_query(query_cities, conn)
print("Total Highest Sales in top 5 City")
print(df_cities)
print("-" * 60)

# Start Code for Chart Making and image Saving
# ------------ According to Category wise Sales VS Profit---------------------
plt.figure(figsize=(8,5))
df_cat_melted=df_category.melt(id_vars='Category', value_vars=['Total_Sales', 'Total_Profit'], var_name='Metric', value_name='Amount')
sns.barplot(data=df_cat_melted, x='Category', y='Amount', hue='Metric', palette=['#2b5c8f', '#38a3a5'])
plt.title('Total Sales VS Profit By Category', fontsize=14, fontweight='bold')
plt.ylabel('Amount ($)')
plt.xlabel('Product Category')
plt.tight_layout()
plt.savefig('1_Category_Sales_Profit.png',dpi=300)
plt.show()
# ---------- All Sub-Catrgories's Profit and Loss Horizontaliy Chart-------------
query_subcat = """
SELECT
    Sub_Category, 
    ROUND(SUM(Profit), 2) AS Total_Profit
    FROM superstore
    GROUP BY Sub_Category
    ORDER BY Total_Profit DESC; 
"""
df_subcat = pd.read_sql_query(query_subcat, conn)
plt.figure(figsize = (10,6))
colors=['#d9534f' if x < 0 else '#2ca02c' for x in df_subcat['Total_Profit']]
sns.barplot(data=df_subcat, x='Total_Profit', hue='Sub_Category', palette=colors)
plt.axvline(0,color='black', linewidth=1)
plt.title('Profit and Loss by Sub-Category (Red=Loss)',fontsize=14, fontweight='bold')
plt.xlabel('Total Profit ($)')
plt.ylabel('Sub-Category')
plt.tight_layout()
plt.savefig('2_Sub_Category_Profit_Loss.png', dpi=300)
plt.show()
# ---------Chart-3 Yearly Sales Trends -------------------
query_yearly="""
SELECT 
    Order_Year,
    ROUND(SUM(Sales), 2) AS Yearly_Sales,
    Round(SUM(Profit), 2) AS Yearly_Profit
FROM superstore
WHERE Order_Year IS NOT NULL
GROUP BY Order_Year
ORDER BY Order_Year;
"""
df_yearly=pd.read_sql_query(query_yearly, conn)
plt.figure(figsize=(8,4))
plt.plot(df_yearly['Order_Year'].astype(str),df_yearly['Yearly_Sales'], marker='o', linewidth=2.5, color='#1f77b4', label='Sales')
plt.plot(df_yearly['Order_Year'].astype(str),df_yearly['Yearly_Profit'], marker='s', linewidth=2.5, color='#ff7f0e', label='Profit')
plt.title('Yearly Sales Profit Grow Trends', fontsize=14, fontweight='bold')
plt.xlabel('Year')
plt.ylabel('Amount ($)')
plt.legend()
plt.tight_layout()
plt.savefig('3_Yearly_Trend.png', dpi=300)
plt.show()
conn.close
print('all chart saved in png file types')
