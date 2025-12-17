# Chatbot Metrics Generator

A modular Python application to fetch chatbot data from ZAgent APIs and PostgreSQL database, then generate JSON metrics formatted for INSERT operations.

## Features

- Fetches chatbots, settings, and languages from ZAgent API
- Connects to PostgreSQL database to get conversation and feedback data
- Optimized queries using IN operator (only 3 database queries regardless of chatbot count)
- Maps language IDs to language names from API
- Counts conversations by platform and feedback by channel
- Generates JSON data formatted for INSERT into chatbot_metrics table

## Project Structure

```
├── main.py                    # Main entry point (orchestrates everything)
├── api_calls.py               # All API-related functions
├── db_calls.py                # All database-related functions
├── static_data.py             # All static data constants
├── generate_chatbot_metrics.py # Backward compatible entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                # Docker configuration
└── README.md                 # This file
```

## Requirements

- Python 3.12+
- PostgreSQL database connection
- Access to ZAgent APIs

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Update the following constants in `api_calls.py`:

- `DATABASE_URL`: PostgreSQL connection string (in db_calls.py)
- `ACCOUNT_IDS`: List of account IDs to fetch chatbots for
- `API_KEY`: Your ZAgent API key
- `BASE_URL`: ZAgent API base URL

## Usage

### Running the main application:
```bash
python main.py
```

### For backward compatibility:
```bash
python generate_chatbot_metrics.py
```

The application will:
1. Fetch data from APIs and database
2. Generate metrics for all chatbots
3. Save to JSON file: `chatbot_metrics_insert_format_YYYY-MM-DD_HH-MM-SS.sss.json`

## Docker Usage

Build the Docker image:
```bash
docker build -t chatbot-metrics .
```

Run the container with environment variables:
```bash
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@host:port/db" \
  -e API_KEY="your-api-key" \
  -v $(pwd)/output:/app/output \
  chatbot-metrics
```

Or run with a .env file:
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  chatbot-metrics
```

## Output Format

The generated JSON contains:
- `chatbot_metrics`: Array of chatbot records with all metrics
- `metadata`: Summary information including total counts and query statistics

Each chatbot record includes:
- Basic info (id, name, profile_url)
- Conversation metrics (today's count, yesterday's count, difference)
- Feedback metrics (total, positive, negative, CSAT)
- Platform distribution (e.g., `{"WEB": 5, "WHATSAPP": 3}`)
- Language distribution (e.g., `{"English": 4, "Tamil": 2}`)
- Feedback channel distribution (e.g., `[{"channel": "web", "count": 10}]`)
- Static data (alerts, trends, geo performance)

## Database Optimization

The script uses optimized queries with IN operator:
- **Query 1**: Fetch all today's conversations for all chatbots
- **Query 2**: Get yesterday's conversation counts
- **Query 3**: Get all feedback with channel information

This reduces database queries from 237 (3 per chatbot) to just 3 total queries.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary to ZAgent.