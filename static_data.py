"""
Static data module containing all static values used in chatbot metrics
"""

# Static feedback by geography
STATIC_FB_GEO = [
    {"country": "India", "percentage": "85", "country_code": "IN"},
    {"country": "USA", "percentage": "90", "country_code": "US"}
]

# Static feedback by channel
STATIC_FB_CHANNEL = [
    {"channel": "whatsapp", "count": 100},
    {"channel": "facebook", "count": 80}
]

# Static performance by geo
STATIC_PERFORM_BY_GEO = {
    "dots": [
        {"lat": 13.0843, "lng": 80.2705, "country": "Tamilnadu", "code": "IN", "interactions": 80000},
        {"lat": 45.5122, "lng": -122.6587, "country": "Portland", "code": "US", "interactions": 58000},
        {"lat": 44.9778, "lng": -93.265, "country": "Minneapolis", "code": "US", "interactions": 62000},
        {"lat": 39.9526, "lng": -75.1652, "country": "Philadelphia", "code": "US", "interactions": 85000}
    ],
    "countryPerformance": [
        {"country": "USA", "interactions": 120000, "code": "US"},
        {"country": "Indonesia", "interactions": 80000, "code": "IN"},
        {"country": "United Kingdom", "interactions": 40000, "code": "GB"},
        {"country": "Sri Lanka", "interactions": 30000, "code": "LK"}
    ]
}

# Static alerts
STATIC_ALERTS = [
    {"time": "1 hr ago", "message": "ABC Bot fallback rate hit 22%", "severity": "high"},
    {"time": "1 hr ago", "message": "Handovers spiked 20% showing automation losing ground in peak hours", "severity": "medium"},
    {"time": "1 hr ago", "message": "Queue delay persists: 12 users waiting over 5 minutes in XYZ Bot", "severity": "high"},
    {"time": "1 hr ago", "message": "9 out of 10 chats in ABC Bot had positive sentiment this week", "severity": "low"},
    {"time": "1 hr ago", "message": "Positive sentiment steady at 90% in ABC Bot this week", "severity": "low"},
    {"time": "1 hr ago", "message": "ABC Bot fallback rate remains elevated at 22%", "severity": "medium"},
    {"time": "1 hr ago", "message": "Human handovers surged 20% during peak hours", "severity": "medium"},
    {"time": "1 hr ago", "message": "Queue still blocked and unresolved in XYZ Bot", "severity": "high"},
    {"time": "45 min ago", "message": "Response time increased by 15% in support bot", "severity": "medium"},
    {"time": "30 min ago", "message": "Drop detected in conversation volume across all bots", "severity": "low"},
    {"time": "25 min ago", "message": "Average handle time exceeded SLA limit by 10%", "severity": "high"},
    {"time": "20 min ago", "message": "Bot accuracy dropped to 85% during live sessions", "severity": "medium"},
    {"time": "10 min ago", "message": "Human takeover ratio increased to 25%", "severity": "medium"},
    {"time": "5 min ago", "message": "XYZ Bot outage detected — unable to process requests", "severity": "critical"}
]

# Static trends
STATIC_TRENDS = [
    {"time": "1 hr ago", "message": "Fallback rate in ABC Bot stable at 22%", "severity": "medium"},
    {"time": "1 hr ago", "message": "Human handovers increased 20% during peak time", "severity": "medium"},
    {"time": "1 hr ago", "message": "Queue delay trending upward: average wait >5 min", "severity": "high"},
    {"time": "1 hr ago", "message": "Positive sentiment steady at 90%", "severity": "low"},
    {"time": "1 hr ago", "message": "Automation efficiency dropped 20% during rush hours", "severity": "medium"},
    {"time": "1 hr ago", "message": "User satisfaction holding steady at 90%", "severity": "low"},
    {"time": "45 min ago", "message": "Average response time rose by 15% this hour", "severity": "medium"},
    {"time": "30 min ago", "message": "Engagement rate dipped 10% during non-peak hours", "severity": "low"},
    {"time": "25 min ago", "message": "Resolution rate improved to 88% across all bots", "severity": "low"},
    {"time": "20 min ago", "message": "Fallback rate trending downward — improvement noted", "severity": "low"},
    {"time": "15 min ago", "message": "Customer satisfaction index up by 5% this week", "severity": "low"},
    {"time": "10 min ago", "message": "Queue backlog cleared 80% faster after system optimization", "severity": "low"},
    {"time": "5 min ago", "message": "Sentiment recovery detected — 3% rise in positive chats", "severity": "low"}
]

# Static net impact
STATIC_NET_IMPACT = {
    "cost_savings": 12500,
    "time_saved": 840,
    "efficiency_gain": 67
}

# Static net impact graph
STATIC_NET_IMPACT_GRAPH = {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "values": [100, 120, 115, 135, 140, 155]
}