# 🐳 Docker Deployment Guide for Hinglish Voice Cloning System

> **Complete Dockerized deployment for the Hinglish Voice Cloning application**

## 🐳 Docker Installation (Windows)

**Before proceeding with Docker deployment, you need to install Docker Desktop:**

### **Step 1: Install Docker Desktop**
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the installation wizard
3. Restart your computer when prompted
4. Start Docker Desktop from the Start menu
5. Wait for Docker to initialize (green icon in system tray)

### **Step 2: Verify Installation**
```cmd
# Check Docker version
docker --version

# Check Docker Compose version  
docker-compose --version

# Test Docker installation
docker run hello-world
```

### **Step 3: Configure Docker (Optional)**
- **Memory:** Allocate at least 4GB RAM to Docker
- **CPU:** Allocate at least 2 CPU cores
- **Storage:** Ensure at least 10GB free space

### **Troubleshooting Docker Installation**
- **WSL 2 Required:** Windows 10/11 requires WSL 2 backend
- **Virtualization:** Enable virtualization in BIOS if needed
- **Windows Features:** Enable "Hyper-V" and "Containers" features

---

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for container
- 10GB free disk space for models and audio files

## 🚀 Quick Start (Docker Compose)

### 1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd hinglish-voice-cloning
```

### 2. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

**Required environment variables:**
```env
# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Application Settings
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

### 3. **Build and Run**
```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f hinglish-voice-app

# Check health
curl http://localhost:8000/health
```

### 4. **Access Application**
- **Web Interface:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🔧 Manual Docker Build

### **Build Image**
```bash
docker build -t hinglish-voice-cloning .
```

### **Run Container**
```bash
docker run -d \
  --name hinglish-voice-app \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  -v $(pwd)/generated:/app/generated \
  -v $(pwd)/voices:/app/voices \
  -v $(pwd)/temp:/app/temp \
  -v $(pwd)/logs:/app/logs \
  hinglish-voice-cloning
```

## 🔍 Monitoring

### **Container Health**
```bash
# Check container status
docker ps

# Check health endpoint
curl http://localhost:8000/health

# View application logs
docker logs hinglish-voice-app -f

# Execute commands in container
docker exec -it hinglish-voice-app bash
```

### **Performance Monitoring**
```bash
# Resource usage
docker stats hinglish-voice-app

# Container inspect
docker inspect hinglish-voice-app
```

## 🗂️ Volume Management

### **Persistent Data**
The following directories are mounted as volumes:
- `./generated` → Generated audio files
- `./voices` → Uploaded voice samples
- `./temp` → Temporary processing files
- `./logs` → Application logs

### **Backup Data**
```bash
# Create backup
docker run --rm \
  -v $(pwd)/generated:/backup/generated \
  -v $(pwd)/voices:/backup/voices \
  alpine tar czf /backup.tar.gz /backup/

# Restore backup
docker run --rm \
  -v $(pwd):/restore \
  alpine tar xzf /restore/backup.tar.gz
```

## 🔄 Updates and Maintenance

### **Update Application**
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### **Clean Up**
```bash
# Remove old containers
docker-compose down

# Remove images
docker rmi hinglish-voice-cloning

# Clean system
docker system prune -f
```

## 🌐 Production Deployment

### **Docker Swarm**
```yaml
# docker-stack.yml
version: '3.8'
services:
  hinglish-voice-app:
    image: hinglish-voice-cloning:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key
      - GEMINI_API_KEY_FILE=/run/secrets/gemini_key
    secrets:
      - openai_key
      - gemini_key
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

secrets:
  openai_key:
    external: true
  gemini_key:
    external: true
```

### **Kubernetes**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hinglish-voice-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hinglish-voice-app
  template:
    metadata:
      labels:
        app: hinglish-voice-app
    spec:
      containers:
      - name: app
        image: hinglish-voice-cloning:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: gemini-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: hinglish-voice-service
spec:
  selector:
    app: hinglish-voice-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔐 Security Best Practices

### **Environment Variables**
```bash
# Use Docker secrets for sensitive data
echo "your_api_key" | docker secret create openai_key -
echo "your_gemini_key" | docker secret create gemini_key -
```

### **Network Security**
```yaml
# docker-compose.yml with network isolation
version: '3.8'
services:
  hinglish-voice-app:
    # ... other config
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
    internal: true
```

### **Resource Limits**
```yaml
services:
  hinglish-voice-app:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 🐛 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
```bash
# Check logs
docker-compose logs hinglish-voice-app

# Common fixes
- Ensure .env file exists with all required variables
- Check port 8000 is not in use
- Verify Docker daemon is running
```

#### **Audio Generation Fails**
```bash
# Check container resources
docker stats hinglish-voice-app

# Ensure sufficient disk space
df -h

# Check volume mounts
docker inspect hinglish-voice-app | grep Mounts -A 20
```

#### **API Connectivity Issues**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Check network configuration
docker network ls
docker network inspect <network_name>
```

### **Debug Mode**
```bash
# Run with debug logging
docker-compose run --rm \
  -e LOG_LEVEL=DEBUG \
  hinglish-voice-app python server.py
```

## 📊 Performance Optimization

### **Multi-stage Build** (Optional)
```dockerfile
# Dockerfile.prod - optimized for production
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "server.py"]
```

### **Resource Tuning**
```yaml
# Recommended resource limits
deploy:
  resources:
    limits:
      cpus: '4.0'      # 4 CPU cores for ML processing
      memory: 8G       # 8GB RAM for models and audio processing
    reservations:
      cpus: '2.0'      # Minimum 2 cores
      memory: 4G       # Minimum 4GB RAM
```

## 🔄 CI/CD Integration

### **GitHub Actions**
```yaml
# .github/workflows/docker.yml
name: Build and Deploy Docker
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t hinglish-voice-cloning .
    
    - name: Test health check
      run: |
        docker run -d --name test-app -p 8000:8000 hinglish-voice-cloning
        sleep 30
        curl -f http://localhost:8000/health
        docker stop test-app
```

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com/
- **Docker Compose Reference:** https://docs.docker.com/compose/
- **FastAPI in Docker:** https://fastapi.tiangolo.com/deployment/docker/
- **Production Checklist:** See PRODUCTION_READY.md

---

**🎯 Ready to Deploy!** Your Hinglish Voice Cloning system is now fully containerized and production-ready!
