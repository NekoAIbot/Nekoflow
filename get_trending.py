from pytrends.request import TrendReq

# Step 1: Connect to Google
pytrends = TrendReq(hl='en-US', tz=360)

# Step 2: Get top daily search trends
trending_searches = pytrends.trending_searches(pn='united_states')  # You can change to 'nigeria', 'japan', etc.

# Step 3: Print the top 10 trends
print("Today's Top 10 Google Trends:")
print(trending_searches.head(10))
