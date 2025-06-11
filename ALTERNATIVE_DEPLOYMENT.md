# 🚀 Alternative Deployment Methods for Hinglish Voice Cloning

> **When Docker is not available, use these alternative deployment methods**

## 📋 Prerequisites

- Python 3.11+
- Windows 10/11
- 4GB+ RAM
- 10GB+ free disk space

## 🔧 Method 1: Virtual Environment (Recommended)

### **Step 1: Setup Virtual Environment**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### **Step 2: Install Dependencies**
```cmd
# Install requirements
pip install -r requirements.txt

# If you encounter errors, install individually:
pip install fastapi uvicorn websockets python-multipart
pip install numpy scipy librosa soundfile torch
pip install supabase openai google-generativeai
```

### **Step 3: Setup Environment**
```cmd
# Copy environment template
copy .env.example .env

# Edit .env file with your API keys (use notepad or any text editor)
notepad .env
```

### **Step 4: Run Application**
```cmd
# Start the server
python server.py

# Or run directly
python -m uvicorn app.websocket_server:app --host 0.0.0.0 --port 8000
```

### **Step 5: Access Application**
- **Web Interface:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎯 Method 2: Direct Python Execution

### **Quick Start**
```cmd
# Install dependencies globally (not recommended for production)
pip install fastapi uvicorn websockets python-multipart numpy scipy librosa soundfile torch supabase openai google-generativeai

# Set environment variables (replace with your actual keys)
set OPENAI_API_KEY=your_openai_api_key_here
set GEMINI_API_KEY=your_gemini_api_key_here
set SUPABASE_URL=your_supabase_url_here
set SUPABASE_KEY=your_supabase_key_here

# Run the application
python server.py
```

---

## 🌐 Method 3: Cloud Deployment

### **Heroku Deployment**
```cmd
# Install Heroku CLI
# Create Procfile
echo web: python server.py > Procfile

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_KEY=your_key

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### **Railway Deployment**
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically from main branch

### **DigitalOcean App Platform**
1. Create new app from GitHub repository
2. Configure environment variables
3. Deploy with auto-scaling

---

## 🔧 Method 4: Windows Service

### **Install as Windows Service**
```cmd
# Install pywin32
pip install pywin32

# Create service script
python scripts\install_service.py

# Start service
net start HinglishVoiceService
```

---

## 🛠️ Development Setup

### **With Auto-Reload**
```cmd
# For development with hot reload
python -m uvicorn app.websocket_server:app --host 0.0.0.0 --port 8000 --reload

# Or using the server script
python server.py
```

### **With Debug Mode**
```cmd
# Set debug environment
set DEBUG=true
set LOG_LEVEL=DEBUG

# Run with debug
python server.py
```

---

## 📊 Performance Optimization

### **Memory Usage**
```cmd
# Monitor memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Optimize for low memory
set TORCH_USE_CUDA_DSA=1
set OMP_NUM_THREADS=2
```

### **CPU Optimization**
```cmd
# Set CPU affinity (if needed)
set NUMBA_NUM_THREADS=4
set MKL_NUM_THREADS=4
```

---

## 🔍 Monitoring and Logs

### **View Logs**
```cmd
# Real-time logs
python server.py > logs\app.log 2>&1

# Or use logging
tail -f logs\app.log  # If you have Git Bash
```

### **Health Monitoring**
```cmd
# Check health endpoint
curl http://localhost:8000/health

# Monitor with PowerShell
powershell -Command "while($true) { Invoke-RestMethod http://localhost:8000/health; Start-Sleep 10 }"
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Use different port
python -m uvicorn app.websocket_server:app --host 0.0.0.0 --port 8080
```

#### **Module Import Errors**
```cmd
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Or install specific modules
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### **API Key Errors**
```cmd
# Verify environment variables
echo %OPENAI_API_KEY%
echo %GEMINI_API_KEY%

# Test API connectivity
python -c "import openai; print('OpenAI OK')"
python -c "import google.generativeai; print('Gemini OK')"
```

#### **Database Connection Issues**
```cmd
# Test Supabase connection
python -c "from supabase import create_client; print('Supabase OK')"

# Check environment variables
echo %SUPABASE_URL%
echo %SUPABASE_KEY%
```

---

## 📋 Deployment Checklist

### **Before Deployment**
- [ ] Python 3.11+ installed
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database tables created
- [ ] API keys verified
- [ ] Firewall configured (if needed)

### **After Deployment**
- [ ] Health check passes
- [ ] Web interface accessible
- [ ] API endpoints working
- [ ] WebSocket connections working
- [ ] Voice upload/generation tested
- [ ] Chatbot functionality verified

---

## 🔄 Updates and Maintenance

### **Update Application**
```cmd
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
# (Stop current process and run python server.py again)
```

### **Backup Data**
```cmd
# Backup generated files
xcopy generated backup\generated\ /E /I

# Backup voice profiles
xcopy voices backup\voices\ /E /I

# Backup database (if using local DB)
# Export from Supabase dashboard
```

---

## 🌟 Production Recommendations

### **For Production Use:**
1. **Use Virtual Environment** - Isolate dependencies
2. **Set Up Monitoring** - Use logs and health checks
3. **Configure Reverse Proxy** - Use nginx or IIS
4. **Enable HTTPS** - Use SSL certificates
5. **Set Up Backups** - Regular data backups
6. **Monitor Resources** - CPU, memory, disk usage

### **Security:**
```cmd
# Restrict file permissions
icacls voices /grant Users:(R)
icacls generated /grant Users:(R)

# Use environment file with restricted access
icacls .env /grant Administrators:(F) /inheritance:r
```

---

**🎯 Ready to Deploy!** Choose the method that best fits your environment and requirements.
