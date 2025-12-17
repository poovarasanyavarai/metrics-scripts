# Z-Agent Metrics

A Python application that fetches chatbot data from ZAgent APIs and PostgreSQL database, then inserts metrics into the database for real-time analytics.

## Overview

- Fetches chatbot configurations from ZAgent APIs
- Retrieves conversation and feedback data from PostgreSQL
- Calculates metrics (conversation counts, CSAT, platform usage)
- Inserts formatted data directly into `chatbot_metrics` table
- Optimized to process 85+ chatbots in ~20 seconds
- Runs every 5 minutes via Kubernetes CronJob

## Features

- ✅ **99.9% Query Optimization**: Reduces from 237 to 3 database queries
- ✅ **Direct Database Insertion**: No intermediate files, better performance
- ✅ **Production Ready**: Docker containerized with Kubernetes deployment
- ✅ **Real-time Processing**: Live metrics with timestamp snapshots
- ✅ **Comprehensive Analytics**: Tracks conversations, feedback, leads, and platform usage

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

### Docker Build

```bash
# Build Docker image
docker build -t z-agent-metrics .

# Run with environment variables
docker run --rm \
  -e DATABASE_URL="postgresql://z_agent_user:z_agent_password@postgresql-shared:5432/z_agent" \
  -e CONFIG_STORE_API_KEY="your-api-key" \
  z-agent-metrics
```

### Deploy to Azure Container Registry (ACR)

#### Step 1: Build and Push to ACR

```bash
# Make build script executable
chmod +x build-and-push.sh

# Build and push to ACR (automated script)
./build-and-push.sh

# Or manually:
az acr login --name zinfradevv1
docker build -t zinfradevv1.azurecr.io/z-agent-metrics:latest .
docker push zinfradevv1.azurecr.io/z-agent-metrics:latest
```

#### Step 2: Deploy to Kubernetes

```bash
# Apply the CronJob configuration
kubectl apply -f z-agent-metrics-cronjob.yaml

# Verify deployment
kubectl get cronjob z-agent-metrics
kubectl get jobs -l app=z-agent-metrics

# View logs of the latest run
POD_NAME=$(kubectl get pods -l app=z-agent-metrics --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
kubectl logs $POD_NAME
```

## Project Structure

```
├── main.py                    # Main application entry point
├── api_calls.py               # ZAgent API integration
├── db_calls.py                # PostgreSQL database operations
├── static_data.py             # Static data constants
├── logger_config.py           # Logging configuration
├── Dockerfile                # Docker container definition
├── build-and-push.sh         # ACR build and push script
├── z-agent-metrics-cronjob.yaml  # Kubernetes CronJob manifest
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Configuration

The application uses these environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `CONFIG_STORE_BASE_URL`: ZAgent API base URL
- `CONFIG_STORE_API_KEY`: API authentication key
- `LOG_LEVEL`: Logging level (default: INFO)

## Performance

- **Chatbots processed**: 83-85 per run
- **Execution time**: 5-10 seconds (Kubernetes), ~20 seconds (local)
- **Database queries**: 3 optimized queries (99.9% reduction)
- **Memory usage**: 256Mi-512Mi
- **CPU usage**: 200m-500m

## Monitoring

### Check CronJob Status
```bash
kubectl get cronjob z-agent-metrics
kubectl get jobs -l app=z-agent-metrics -w
```

### View Application Logs
```bash
# Latest run logs
kubectl logs -l app=z-agent-metrics --tail=50

# Follow logs in real-time
kubectl logs -l app=z-agent-metrics -f
```

### Database Metrics
```sql
-- Check latest metrics
SELECT * FROM chatbot_metrics
ORDER BY created_at DESC
LIMIT 10;

-- Count of records per day
SELECT DATE(created_at) as date, COUNT(*) as records
FROM chatbot_metrics
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## Troubleshooting

### Common Issues

1. **ImagePullBackOff**
   ```bash
   # Verify image exists in ACR
   az acr repository show-tags --name zinfradevv1 --repository z-agent-metrics
   ```

2. **Database Connection**
   ```bash
   # Test database connectivity
   kubectl exec -it <pod-name> -- nc -zv postgresql-shared 5432
   ```

3. **API Errors**
   - Check API key validity
   - Verify network connectivity to ZAgent APIs
   - Check rate limits

### Debug Commands

```bash
# Describe CronJob
kubectl describe cronjob z-agent-metrics

# Describe job
kubectl describe job <job-name>

# View events
kubectl get events --field-selector involvedObject.name=z-agent-metrics
```

## Maintenance

### Update Application
1. Build and push new image with new tag
2. Update image tag in `z-agent-metrics-cronjob.yaml`
3. Apply changes: `kubectl apply -f z-agent-metrics-cronjob.yaml`

### Cleanup
```bash
# Delete old successful jobs (keep last 3)
kubectl delete jobs -l app=z-agent-metrics --field-selector status.successful=1

# Delete entire CronJob
kubectl delete cronjob z-agent-metrics
```

## Production Deployment

The Kubernetes CronJob is configured to:
- Run every 5 minutes (`*/5 * * * *`)
- Timeout after 10 minutes
- Keep last 3 successful and failed jobs
- Use resource limits (CPU: 500m, Memory: 512Mi)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Quick Commands Reference

```bash
# Build and deploy
./build-and-push.sh
kubectl apply -f z-agent-metrics-cronjob.yaml

# Monitor
kubectl get cronjob z-agent-metrics
kubectl get jobs -l app=z-agent-metrics
kubectl logs -l app=z-agent-metrics

# Debug
kubectl describe cronjob z-agent-metrics
kubectl get events | grep z-agent-metrics
```

**Result**: Chatbot metrics are collected and inserted into your database every 5 minutes! 🚀