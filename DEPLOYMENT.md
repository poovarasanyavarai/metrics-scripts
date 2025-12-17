# Z-Agent Metrics Deployment Guide

## Overview
This guide explains how to deploy the Z-Agent Metrics application to Kubernetes using Azure Container Registry.

## Prerequisites
- Azure CLI installed and configured
- Docker installed
- kubectl configured to access your Kubernetes cluster
- Access to Azure Container Registry (zinfradevv1)

## Step 1: Build and Push Docker Image

You'll build and push the image manually using these commands:

```bash
# Login to Azure Container Registry
az acr login --name zinfradevv1

# Build the Docker image
docker build -t zinfradevv1.azurecr.io/z-agent-metrics:latest .

# Push the image to ACR
docker push zinfradevv1.azurecr.io/z-agent-metrics:latest
```

## Step 2: Deploy to Kubernetes

### Option A: Apply the CronJob directly
```bash
kubectl apply -f z-agent-metrics-cronjob.yaml
```

### Option B: Replace with custom tag (if needed)
If you're using a different tag, edit the `z-agent-metrics-cronjob.yaml` file:
```yaml
# Change this line to use your custom tag
image: zinfradevv1.azurecr.io/z-agent-metrics:your-custom-tag
```

Then apply:
```bash
kubectl apply -f z-agent-metrics-cronjob.yaml
```

## Step 3: Verify Deployment

### Check CronJob status
```bash
kubectl get cronjob z-agent-metrics
```

### Check job history
```bash
kubectl get jobs -l app=z-agent-metrics
```

### View logs of the latest run
```bash
# Get the latest pod name
POD_NAME=$(kubectl get pods -l app=z-agent-metrics --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# View logs
kubectl logs $POD_NAME
```

### Monitor real-time execution
```bash
# Watch for new jobs
kubectl get jobs -l app=z-agent-metrics -w

# Watch pods
kubectl get pods -l app=z-agent-metrics -w
```

## Configuration

### Environment Variables
The CronJob is configured with these environment variables:

- `CONFIG_STORE_BASE_URL`: ZAgent config store URL
- `CONFIG_STORE_API_KEY`: API key for config store access
- `DATABASE_URL`: PostgreSQL database connection string
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)
- `PYTHONPATH`: Python path

### Database Connection
The application connects to:
- **Database**: `z_agent`
- **Host**: `postgresql-shared:5432`
- **User**: `z_agent_user`
- **Password**: `z_agent_password`

### Schedule
- **Current**: Every 5 minutes (`*/5 * * * *`)
- To modify, edit the `schedule` field in the YAML file

### Resource Limits
- **CPU**: 200m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit
- **Timeout**: 600 seconds (10 minutes)

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Verify image exists in ACR
   az acr repository show-tags --name zinfradevv1 --repository z-agent-metrics
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   kubectl exec -it <pod-name> -- nc -zv postgresql-shared 5432
   ```

3. **Permission Issues**
   ```bash
   # Check service account permissions
   kubectl describe serviceaccount default
   ```

### Debugging

1. **Describe the CronJob**
   ```bash
   kubectl describe cronjob z-agent-metrics
   ```

2. **Describe a specific job**
   ```bash
   kubectl describe job <job-name>
   ```

3. **Get pod events**
   ```bash
   kubectl get events --field-selector involvedObject.name=<pod-name>
   ```

4. **Shell into a running pod**
   ```bash
   kubectl exec -it <pod-name> -- /bin/bash
   ```

## Maintenance

### Updating the Application
1. Build and push new image with new tag
2. Update the image tag in `z-agent-metrics-cronjob.yaml`
3. Apply the updated manifest:
   ```bash
   kubectl apply -f z-agent-metrics-cronjob.yaml
   ```

### Cleanup
```bash
# Delete the CronJob and all associated jobs
kubectl delete cronjob z-agent-metrics

# Delete only old jobs (keep last 3)
kubectl delete jobs -l app=z-agent-metrics --field-selector status.successful=1
```

## Monitoring

### Metrics to Monitor
- Job success/failure rate
- Execution time (should be < 2 minutes)
- Database connection health
- Memory usage
- CPU usage

### Recommended Alerts
- Failed jobs > 3 in a row
- Execution time > 5 minutes
- Memory usage > 400Mi
- CPU usage > 400m

## Security Considerations

- API key is stored as plain text in the manifest (consider using Kubernetes secrets)
- Database credentials are exposed (consider using secrets)
- Container runs as root (runAsNonRoot: false) - consider updating for better security

## Production Recommendations

1. **Use Kubernetes Secrets** for sensitive data
2. **Implement proper logging** with log aggregation
3. **Set up monitoring** with Prometheus/Grafana
4. **Configure resource quotas** and limits
5. **Implement backup strategy** for database
6. **Use network policies** for security