# Phase 10: Deployment & Containerization

## Overview
This phase completes the project with production-ready Docker containerization, environment configuration, and deployment instructions.

## Architecture

### Multi-Stage Dockerfile
The `Dockerfile` uses a two-stage build process:

**Stage 1: Builder**
- Python 3.11 slim base image
- Installs build dependencies (gcc, libpng-dev, libjpeg-dev, libfreetype6-dev)
- Creates optimized wheel files for all dependencies
- Result: Intermediate builder image (discarded after build)

**Stage 2: Runtime**
- Python 3.11 slim base image (minimal size)
- Copies only wheels from builder
- Installs runtime libraries (libpng16, libjpeg62, libfreetype6)
- Runs as non-root user (appuser, UID 1000)
- Includes health check endpoint
- Exposes port 8000
- Runs Uvicorn with 4 workers

### Benefits of Multi-Stage Build
✅ Reduced image size (~2x smaller)
✅ No build tools in production image
✅ Faster deployment cycles
✅ Secure: Non-root user execution
✅ Consistent across dev/prod

## Files

### `Dockerfile`
- Multi-stage build configuration
- Health check with `/api/v1/health` endpoint
- Uvicorn ASGI server with 4 workers
- Security: Non-root user, minimal dependencies

### `.env.example`
- Template for all configurable settings
- Includes comments for each option
- Supports OpenAI, Gemini, and mock providers
- LLM parameters, anomaly detection thresholds, etc.

### `.dockerignore`
- Excludes unnecessary files from build context
- Reduces image size: ~500MB → ~300MB
- Ignores .git, __pycache__, venv, .env, etc.

### `docker-compose.yml`
- Local development environment setup
- Maps port 8000 to host
- Mounts source code for hot-reload
- Includes health check configuration
- Optional production config (commented)

## Deployment Instructions

### Local Development

#### Option 1: Docker Compose (Recommended)
```bash
# Build and run
docker-compose up --build

# Access API
curl http://localhost:8000/api/v1/health
open http://localhost:8000/

# Stop
docker-compose down
```

#### Option 2: Manual Docker Build
```bash
# Build image
docker build -t insightboard-api:latest .

# Run container
docker run -p 8000:8000 \
  -e INSIGHTBOARD_DEFAULT_LLM_PROVIDER=mock \
  insightboard-api:latest

# Access
curl http://localhost:8000/api/v1/health
```

### Environment Configuration

#### 1. Create `.env` file
```bash
# Copy from template
cp .env.example .env

# Edit with your actual API keys
nano .env
```

#### 2. Configure LLM Provider
```bash
# Option A: Mock (no API key needed - for testing)
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=mock

# Option B: OpenAI
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=openai
INSIGHTBOARD_OPENAI_API_KEY=sk-your-key-here
INSIGHTBOARD_OPENAI_MODEL=gpt-4o

# Option C: Gemini
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=gemini
INSIGHTBOARD_GEMINI_API_KEY=AIzaSyDxxxxxxxxxx
INSIGHTBOARD_GEMINI_MODEL=gemini-2.5-flash
```

#### 3. Configure Retry Behavior
```bash
# Max retry attempts for LLM calls (default: 3)
INSIGHTBOARD_LLM_MAX_RETRIES=5

# Timeout for LLM API calls (seconds)
INSIGHTBOARD_LLM_TIMEOUT_SECONDS=60.0
```

### Production Deployment

#### Docker Hub / Container Registry
```bash
# Tag image
docker tag insightboard-api:latest myregistry/insightboard-api:1.0.0

# Push to registry
docker push myregistry/insightboard-api:1.0.0
```

#### Cloud Platforms

**AWS ECS:**
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag insightboard-api:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/insightboard-api:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/insightboard-api:latest
```

**Azure Container Instances:**
```bash
# Push to ACR
az acr login --name myregistry
docker tag insightboard-api:latest myregistry.azurecr.io/insightboard-api:latest
docker push myregistry.azurecr.io/insightboard-api:latest
```

**Google Cloud Run:**
```bash
# Push to Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
docker tag insightboard-api:latest us-central1-docker.pkg.dev/PROJECT_ID/insightboard/api:latest
docker push us-central1-docker.pkg.dev/PROJECT_ID/insightboard/api:latest
```

#### Kubernetes Deployment
```yaml
# Example Kubernetes manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insightboard-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: insightboard-api
  template:
    metadata:
      labels:
        app: insightboard-api
    spec:
      containers:
      - name: api
        image: myregistry/insightboard-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: INSIGHTBOARD_ENVIRONMENT
          value: "production"
        - name: INSIGHTBOARD_DEFAULT_LLM_PROVIDER
          valueFrom:
            configMapKeyRef:
              name: insightboard-config
              key: llm-provider
        - name: INSIGHTBOARD_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: insightboard-secrets
              key: openai-api-key
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Image Specifications

### Build Details
- **Base Image**: `python:3.11-slim`
- **Builder Image**: Includes build tools, ~800MB
- **Runtime Image**: Lean runtime dependencies, ~300MB
- **Final Size**: ~350-400MB (depending on dependencies)

### Performance
- **Startup Time**: ~5-10 seconds (health check start period)
- **Memory Usage**: ~100-200MB (idle), ~300-500MB (active)
- **Workers**: 4 (configurable via CMD)

### Security
- ✅ Non-root user (appuser, UID 1000)
- ✅ Minimal dependencies (no build tools)
- ✅ Slim Python image (no extra packages)
- ✅ Health check for orchestration
- ✅ Environment variables for secrets (no hardcoded keys)

## Monitoring & Health Checks

### Health Endpoint
```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Docker health check
docker inspect insightboard-api | grep -A 5 '"Health"'

# Kubernetes health check (configured in manifest)
kubectl get pods insightboard-api-xxx
```

### Logs
```bash
# Docker logs
docker logs -f insightboard-api

# Docker compose logs
docker-compose logs -f insightboard-api

# Kubernetes logs
kubectl logs -f deployment/insightboard-api
```

## Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `INSIGHTBOARD_ENVIRONMENT` | string | development | Environment (development/production) |
| `INSIGHTBOARD_LOG_LEVEL` | string | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `INSIGHTBOARD_DEFAULT_LLM_PROVIDER` | string | mock | LLM provider (mock/openai/gemini) |
| `INSIGHTBOARD_OPENAI_API_KEY` | string | - | OpenAI API key (if using OpenAI) |
| `INSIGHTBOARD_GEMINI_API_KEY` | string | - | Gemini API key (if using Gemini) |
| `INSIGHTBOARD_LLM_MAX_RETRIES` | int | 3 | Max LLM retry attempts (1-10) |
| `INSIGHTBOARD_LLM_TIMEOUT_SECONDS` | float | 60.0 | LLM API timeout in seconds |

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs insightboard-api

# Inspect image
docker inspect insightboard-api:latest
```

### Health check failing
```bash
# Manual health check
curl -v http://localhost:8000/api/v1/health

# Check Docker health
docker inspect insightboard-api --format='{{.State.Health.Status}}'
```

### High memory usage
```bash
# Reduce workers (edit docker-compose or CMD)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Rebuild and restart
docker-compose down
docker-compose up --build
```

## Next Steps

1. **Set up CI/CD Pipeline**
   - GitHub Actions, GitLab CI, or Azure DevOps
   - Auto-build Docker images on commits
   - Push to container registry

2. **Deploy to Cloud**
   - Choose: AWS ECS, Azure Container Instances, Google Cloud Run, or Kubernetes
   - Configure autoscaling policies
   - Set up monitoring and alerting

3. **Security Hardening**
   - Use private container registry
   - Implement image scanning (Trivy, Anchore)
   - Rotate API keys regularly
   - Use secret management (AWS Secrets Manager, Azure Key Vault)

4. **Performance Optimization**
   - Profile application memory usage
   - Tune worker count based on CPU cores
   - Implement caching for LLM responses
   - Set up CDN for static assets

## References

- Docker Documentation: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Uvicorn: https://www.uvicorn.org/
- Multi-stage Builds: https://docs.docker.com/build/building/multi-stage/
