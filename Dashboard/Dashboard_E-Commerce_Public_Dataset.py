# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Import Dataset
df_olist = pd.read_csv("Dashboard/main_data.csv")

# Convert specified columns in the df_orders to datetime format for accurate time-based analysis
datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']

for column in datetime_columns:
    df_olist[column] = pd.to_datetime(df_olist[column])

# Number of products sold each month
df_olist['date'] = df_olist['order_purchase_timestamp'].dt.to_period('M')
daily_counts = df_olist.groupby('date')['order_id'].count()

# Product sales revenue by month
df_olist['date'] = df_olist['order_purchase_timestamp'].dt.to_period('M')
daily_total_price = df_olist.groupby('date')['price'].sum()

# Product sales by day and hour
df_olist['day_of_week_name'] = df_olist['order_purchase_timestamp'].dt.strftime('%A')
df_olist['hour'] = df_olist['order_purchase_timestamp'].dt.hour

order_counts = df_olist.groupby(['day_of_week_name', 'hour']).size().reset_index(name='count')
peak_orders = order_counts.pivot(index='day_of_week_name', columns='hour', values='count')

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
peak_orders = peak_orders.reindex(days_order)

# Top 10 categories
category_order_counts = df_olist.groupby('product_category_name_english')['order_id'].count()
sorted_category_order_counts = category_order_counts.sort_values(ascending=False)

top_10_categories = sorted_category_order_counts.head(10)
bottom_10_categories = sorted_category_order_counts.tail(10)

# Difference between the actual delivery time and the estimated time in each month
df_olist['delivery_delay'] = (df_olist['order_delivered_customer_date'] - df_olist['order_estimated_delivery_date']).dt.days
df_delayed = df_olist[df_olist['delivery_delay'] > 0]

monthly_average_delivery_difference = df_delayed.groupby(df_delayed['order_purchase_timestamp'].dt.to_period('M'))['delivery_delay'].mean()

# Average review score in each month
monthly_average_review = df_delayed.groupby(df_delayed['order_purchase_timestamp'].dt.to_period('M'))['review_score'].mean()

# Streamlit app
st.set_page_config(
    page_title="Olist E-commerce Dashboard",
    layout="wide",  # Set layout to wide for better space utilization
    initial_sidebar_state="auto",
)

st.title("Olist E-commerce Dashboard")

st.header("Questions")
st.markdown("""
- What are the sales and order delivery trends on Olist's e-commerce platform over time, as well as order patterns by time and day of the week?
- What are the top 10 most and least sold product categories on Olist's e-commerce platform?
- How does late delivery affect customer satisfaction on the Olist e-commerce platform?
""")

# Question 1
st.header("Sales and Order Delivery Trends")

# Order Percentage Trends
st.subheader("Order Percentage Trends")
percentage_counts = (daily_counts / daily_counts.sum()) * 100
plt.figure(figsize=(15, 6))
line_plot = percentage_counts.plot(color='#007BFF', linestyle='-', linewidth=2, marker='o', markersize=5, markerfacecolor='#FF8C00')
plt.title('Percentage of Orders by Date', fontsize=15)
plt.xlabel('Date', fontsize=10)
plt.ylabel('Percentage of Orders (%)', fontsize=10)
plt.grid()
plt.ylim(0, percentage_counts.max() + 4.3)
plt.gca().set_facecolor('#F5F5F5')

for x, y in zip(percentage_counts.index, percentage_counts):
    plt.text(x, y + 0.5, f'{y:.1f}%', ha='center', fontsize=10, color='black')

plt.tight_layout()
st.pyplot(plt)

# Total Price Trends
st.subheader("Total Price of Products Sold")
plt.figure(figsize=(15, 6))
line_plot = daily_total_price.plot(color='#007BFF', linestyle='-', linewidth=2, marker='o', markersize=5, markerfacecolor='#FF8C00')
plt.title('Total Price of Products Sold by Date', fontsize=15)
plt.xlabel('Date', fontsize=10)
plt.ylabel('Total Price (R$)', fontsize=10)
plt.ylim(0, daily_total_price.max() + 200000)
plt.gca().set_facecolor('#F5F5F5')
plt.grid()

for x, y in zip(daily_total_price.index, daily_total_price):
    if y >= 1000:
        y_label = f'{y/1000:.0f}k'  # Format as thousands
    else:
        y_label = f'{y:.0f}'
    plt.text(x, y + 30000, y_label, ha='center', fontsize=10, color='black')

plt.tight_layout()
st.pyplot(plt)

# Peak Ordering Times
st.subheader("Peak Ordering Times by Day of the Week and Hour")
plt.figure(figsize=(20, 7))
ax = sns.heatmap(peak_orders, cmap="Blues", annot=True, fmt='d', cbar=True)
ax.set_xlabel('Hour')
ax.set_ylabel('Day of Week')
ax.set_title('Peak Ordering Times by Day of the Week and Hour')
plt.xticks(ticks=range(24), labels=[str(i) for i in range(24)])
st.pyplot(plt)

st.markdown("""
**Insight:**
1. Total Order and Total Revenue Trends:
    - Overall, total orders and total revenue increased from 2016 to 2018, indicating positive business growth.
    - There were seasonal fluctuations, with a significant increase in orders at the end of the year (possibly related to the holiday period).
    - It is important to further analyze the factors that led to the increase or decrease in order volume and revenue, such as promotions, events, or external factors.
2. Peak Ordering Times:
    - Peak ordering times occur mostly on weekdays (Monday - Friday) and during business hours (around 10-17).
    - On Saturdays and Sundays, order volumes tend to be lower.
    - This indicates that most customers place orders during business hours and on business days.
""")

# Question 2
st.header("Product Category Analysis")

# Top and Bottom 10 Product Categories
st.subheader("Most and Least Sold Product Categories")
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Most and Least Sold Product Categories", fontsize=16)

top_10_categories.index = top_10_categories.index.str.replace('_', ' ')
bottom_10_categories.index = bottom_10_categories.index.str.replace('_', ' ')

bars_left = axes[0].barh(top_10_categories.index[::-1], top_10_categories.values[::-1], color='skyblue')
bars_left[-1].set_color('#007BFF')
axes[0].set_xlabel('Number of Orders')
axes[0].set_title('Top 10 Most Sold Product Categories')
axes[0].set_facecolor('#F5F5F5')

for bar in bars_left:
    width = bar.get_width()
    axes[0].text(width - 20, bar.get_y() + bar.get_height()/2, f'{int(width)}', ha='right', va='center', color='black')

bars_right = axes[1].barh(bottom_10_categories.index, bottom_10_categories.values, color='#FFCC80')
bars_right[-1].set_color('#FF8C00')
axes[1].set_xlabel('Number of Orders')
axes[1].set_title('Bottom 10 Least Sold Product Categories')
axes[1].invert_xaxis()
axes[1].yaxis.tick_right()
axes[1].yaxis.set_label_position("right")
axes[1].set_facecolor('#F5F5F5')

for bar in bars_right:
    width = bar.get_width()
    axes[1].text(width - 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', ha='center', va='center', color='black')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
st.pyplot(fig)

st.markdown("""
**Insight:**
Most and Least Sold Product Categories
    - The product categories `bed_bath_table`, `health_beauty`, and `sports_leisure` are among the most sold categories.
    - This shows that items for household, health and beauty, and sports and leisure are in high demand among Olist customers.
    - On the other hand, there are some less-sold product categories, such as `security_and_services`, `cds_dvds_musicals`, and `la_cuisine`.
""")

# Question 3
st.header("Delivery Delay and Customer Satisfaction")

# Delivery Delay Distribution
st.subheader("Delivery Delay Distribution")
plt.figure(figsize=(13, 6))
plt.hist(df_olist['delivery_delay'], bins=100, color='skyblue', edgecolor='black')
plt.axvline(x=0)
plt.xlabel('Delivery Difference (Days)')
plt.ylabel('Number of Orders')
plt.title('Delivery Delay Distribution: Actual vs Estimated')
plt.xlim(-50, 50)
plt.gca().set_facecolor('#F5F5F5')
plt.grid()
st.pyplot(plt)

# Correlation between Delivery Delay and Customer Satisfaction
st.subheader("Correlation between Delivery Delay and Customer Satisfaction")
df_correlation = pd.DataFrame({'average_review_score': monthly_average_review,
                               'average_delivery_difference': monthly_average_delivery_difference})

correlation = df_correlation['average_review_score'].corr(df_correlation['average_delivery_difference'])

plt.figure(figsize=(10, 6))
plt.scatter(df_correlation['average_review_score'], df_correlation['average_delivery_difference'])
plt.xlabel('Average Review Score')
plt.ylabel('Average Delivery Delay')
plt.title('Correlation Between Delivery Delay and Customer Satisfaction')
plt.ylim(0, df_correlation['average_delivery_difference'].max() + 4)
plt.gca().set_facecolor('#F5F5F5')
plt.grid()

plt.text(df_correlation['average_review_score'].max(), df_correlation['average_delivery_difference'].max() + 2,
         f'Correlation: {correlation:.2f}', fontsize=12, ha='right', va='top')

st.pyplot(plt)

st.markdown("""
**Insight:**
1. Delivery Delay Distribution: Actual vs Estimated
    - Most orders are delivered on time or even faster than expected (negative delivery difference).
    - There is a small proportion of orders that experience delivery delays (positive delivery difference).
    - The delay distribution tends to be centered around 0 with some cases reaching significant delays.

2. Correlation Between Delivery Delay and Customer Satisfaction
    - The correlation between delivery delay (`order_delivered_customer_date > estimated delivery`) and customer reviews is $-0.7$.
    - This shows a strong negative relationship, indicating that as delivery delays increase, customer satisfaction tends to decrease.
""")

st.header("Conclusion")

st.subheader("Sales and Order Delivery Trends")
st.markdown("""
1. Optimize Marketing Strategy in Peak Season
    - There is a significant increase in the number of orders and total revenue at the end of the year. This indicates the potential for increased sales during the holiday season.
    - Therefore, plan special marketing strategies for the holiday season, such as promotions, discounts, and special offers, to increase sales and customer engagement.

2. Increase Promotion and Sales Outside of Busy Hours
    - Based on analysis, order volume tends to be high during peak hours and weekdays.
    - To increase revenue, Olist can consider a strategy of promotions and special offers on weekends or off-peak hours (for example, in the evenings). This can attract customers who are unable to shop online during business hours.

3. Optimizing Customer Service during Rush Hours
    - During peak hours, customer service may experience a higher load.
    - Olist should consider increasing the number of staff or strengthening the automated service system to ensure that customers still have a good experience while shopping.
""")

st.subheader("Product Category Analysis")
st.markdown("""
1. Focus on Inventory and Delivery for Bestselling Categories
    - Ensure that the stock availability of products in the best-selling categories is sufficient to meet demand.
    - Optimize the delivery process for best-selling categories to ensure customer satisfaction.

2. Evaluate Products with the Least Selling Categories
    - Analyze the factors that cause low sales in these categories. Is it due to lack of consumer interest, ineffective promotion, or limited stock?
""")

st.subheader("Delivery Delay and Customer Satisfaction")
st.markdown("""
1. Further Analyze the Factors Causing Delays
    - Understanding the proportion of orders that experience delivery delays can help companies identify areas of improvement in logistics and supply chain processes.
    - Further analyze the factors that cause delivery delays, such as geographical location, delivery method, and traffic density.

2. Prioritize On-Time Delivery
    - The negative correlation between average review scores and average delivery delays shows that delivery delays negatively impact customer satisfaction.
    - Consider optimizing delivery routes, using shipment tracking technology, and improving the efficiency of the order processing process.
""")
