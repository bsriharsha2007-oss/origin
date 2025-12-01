# 🚀 Deploy SwarmForge Web App to Chrome

## Quick Launch (Easiest)

### Windows - Command Prompt
```bash
start_webapp.cmd
```
Then open: **http://localhost:8000**

### Windows - PowerShell
```powershell
.\start_webapp.ps1
```
Then open: **http://localhost:8000**

### macOS/Linux
```bash
chmod +x start_webapp.sh
./start_webapp.sh
```
Then open: **http://localhost:8000**

---

## Manual Deployment

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# (OpenAI, Groq, Tavily - at least one LLM key required)
```

### Step 3: Start the Server
```bash
python webserver.py
```

### Step 4: Open in Chrome
Click the link or type in address bar:
```
http://localhost:8000
```

---

## What You'll See

### 🎮 Left Panel - Control
- **Initialize Swarm**: Start with your LLM
- **Add Agents**: Create team members
- **Configure**: Set roles (Researcher, Analyzer, etc.)

### ⚡ Right Panel - Execute
- **Task Input**: Describe what you want done
- **Agent Count**: How many agents to use
- **Execution Mode**: Parallel, Sequential, or Hierarchical
- **Execute Button**: Run the task

### 👥 Agents Panel
- See all active agents
- Monitor their status and statistics
- Track execution count

### 📊 Results Panel
- **Current Result**: Latest execution output
- **History**: Recent tasks (last 10)
- **Memory**: Search past information
- **Evaluation**: AI-generated quality report

---

## API Documentation

Once running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

All endpoints are documented with examples you can test directly!

---

## Example Tasks to Try

1. **Simple Task**
   ```
   "What are the top 3 Python libraries for data science?"
   ```
   - Use: 2-3 agents, Parallel mode

2. **Analysis Task**
   ```
   "Compare React, Vue, and Angular frameworks"
   ```
   - Use: 3-4 agents, Hierarchical mode

3. **Complex Task**
   ```
   "Create a plan to learn machine learning starting from basics"
   ```
   - Use: 4-5 agents, Sequential mode

4. **Code Task**
   ```
   "Write Python code to calculate Fibonacci sequence efficiently"
   ```
   - Use: 2-3 agents, Parallel mode

---

## Troubleshooting

### ❌ Port 8000 In Use
**Error**: `Address already in use`

**Fix**: 
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (Windows)
taskkill /PID <PID> /F

# Or change port in webserver.py line 435
```

### ❌ No LLM Key Configured
**Error**: `No LLM API key configured`

**Fix**: 
- Edit `.env` file
- Add either `OPENAI_API_KEY` or `GROQ_API_KEY`
- Groq is free (register at console.groq.com)
- Save and restart

### ❌ Dependencies Not Installing
**Error**: `ModuleNotFoundError`

**Fix**:
```bash
pip install -r requirements.txt --force-reinstall
```

### ❌ Import Errors
**Error**: `langchain imports failing`

**Fix**:
```bash
pip install langchain langchain-core langchain-openai langchain-groq --upgrade
```

### ❌ Page Not Loading
**Error**: Blank page or connection refused

**Fix**:
1. Check server is running (should see "Uvicorn running" message)
2. Try `http://127.0.0.1:8000` instead
3. Check firewall isn't blocking port 8000
4. Try different browser (Chrome, Firefox, Edge)

---

## Advanced Usage

### Change Port
Edit `webserver.py`, find:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,  # ← Change this number
)
```

### Access from Other Devices on Network
Edit `webserver.py`:
```python
uvicorn.run(
    app,
    host="0.0.0.0",  # ← Already allows all networks
    port=8000,
)
```

Then access from another computer using:
```
http://<your-computer-ip>:8000
```

Find your IP:
- Windows: `ipconfig` → IPv4 Address
- macOS/Linux: `ifconfig` → inet

### Enable HTTPS (Self-signed)
```bash
# Generate certificate (one time)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Modify webserver.py to use cert
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem"
)
```

---

## Browser Tips

### 🔖 Bookmark the App
1. Open http://localhost:8000
2. Press `Ctrl+D` (or `⌘+D` on Mac)
3. Click "Add" to bookmark

### 📌 Pin to Taskbar (Windows)
1. Open http://localhost:8000
2. Click the menu (⋮)
3. Select "Create shortcut"
4. Check "Open as window"
5. Right-click the app icon and "Pin to taskbar"

### 🔄 Refresh Tips
- **Soft refresh**: `Ctrl+R`
- **Hard refresh**: `Ctrl+Shift+R` (clears cache)
- **Dev tools**: `F12` (see API responses)

---

## Performance Tips

1. **Faster Execution**
   - Use Parallel mode (agents work simultaneously)
   - Use Groq API instead of OpenAI (faster, free)
   - Reduce agent count (2-3 for simple tasks)

2. **Better Results**
   - Use Sequential mode (ordered execution)
   - Use 4-5 agents with different roles
   - Enable Memory Management

3. **Reliability**
   - Use Hierarchical mode with Coordinator
   - Start with smaller tasks to test setup
   - Monitor execution history for patterns

---

## Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "webserver.py"]
```

### Cloud Deployment
- **Azure**: Container Apps or App Service
- **AWS**: ECS, Lambda, or EC2
- **GCP**: Cloud Run or Compute Engine
- **Railway**: Simple push-to-deploy

### Environment Configuration
Set these variables on your hosting platform:
```
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
```

---

## Security for Production

1. **Restrict CORS**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Add Authentication**
   ```python
   # Add JWT or API key verification
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter
   # Limit requests to prevent abuse
   ```

4. **HTTPS Only**
   ```
   # Enable SSL certificates
   ```

5. **Environment Variables**
   ```bash
   # Never commit .env file
   # Use secrets management service
   ```

---

## Next Steps

1. ✅ Start the web app with `start_webapp.cmd`
2. ✅ Initialize swarm in the UI
3. ✅ Add 3 agents with different roles
4. ✅ Run a simple task
5. ✅ Explore the Memory and Evaluation tabs
6. ✅ Try different execution modes

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Interactive Testing**: Try out API endpoints in browser
- **Code Documentation**: See WEBAPP_GUIDE.md
- **Framework Info**: See README.md and PROJECT_SUMMARY.txt

---

**Enjoy deploying SwarmForge! 🚀**
