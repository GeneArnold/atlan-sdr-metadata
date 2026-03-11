# Render Deployment Troubleshooting Guide

## Overview

This guide documents the complete deployment process for the Genie chat integration on Render, including all issues encountered and their solutions. The deployment uses a Python Flask application connected to a GitHub repository with automatic deployments.

## Deployment Architecture

```
GitHub Repository (main branch)
    ↓ (webhook)
Render Build System
    ↓ (Docker container)
Python 3.11.10 Environment
    ↓ (Gunicorn WSGI)
Live Application
    ↓ (HTTPS)
https://atlan-sdr-metadata.onrender.com
```

## Critical Files for Deployment

### 1. `.python-version`
**Purpose**: Specifies exact Python version for Render

**Content**:
```
3.11.10
```

**Why It's Critical**:
- Render uses this to select Python version
- Python 3.14 breaks pyatlan/Pydantic v1
- Must be 3.11.x for SDK compatibility

### 2. `Procfile`
**Purpose**: Tells Render how to start the application

**Content**:
```
web: gunicorn app:app
```

**Common Errors Without It**:
- "Add a Procfile" error in Render logs
- Application fails to start
- No web process defined

### 3. `requirements.txt`
**Purpose**: Python dependencies

**Critical Dependencies**:
```
Flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.1.0
requests==2.32.3
gunicorn==21.2.0
pyatlan==4.2.5
```

**Version Constraints**:
- `pyatlan==4.2.5` requires Python 3.11.x
- Don't use httpx (incompatible with Python 3.14)
- Pin all versions for consistency

## Common Deployment Issues and Solutions

### Issue 1: Python Version Incompatibility

**Symptoms**:
```
ERROR: Package 'pyatlan' requires a different Python: 3.14.0 not in '>=3.8,<3.13'
ImportError: cannot import name 'deprecated' from 'typing_extensions'
```

**Root Cause**: Python 3.14 incompatible with Pydantic v1 used by pyatlan

**Solution**:
1. Create `.python-version` file with `3.11.10`
2. Commit and push to repository
3. Trigger new deployment

**Verification**:
```bash
# In Render logs, look for:
Python version: 3.11.10
```

### Issue 2: Missing Procfile

**Symptoms**:
```
==> Build failed
==> Add a Procfile to your root directory
```

**Solution**:
1. Create `Procfile` (capital P, no extension)
2. Add: `web: gunicorn app:app`
3. Commit and push

**Common Mistakes**:
- Using lowercase `procfile`
- Adding file extension (.txt)
- Wrong gunicorn syntax

### Issue 3: Auto-Deploy Not Triggering

**Symptoms**:
- Code pushed to GitHub
- No new deployment in Render
- Previous deployment still active

**Root Causes**:
1. Previous build failed
2. Auto-deploy disabled after failures
3. Webhook disconnected

**Solution**:
```bash
# Manual deployment trigger
1. Go to Render Dashboard
2. Click "Manual Deploy"
3. Select "Deploy latest commit"

# Fix auto-deploy
1. Settings → Build & Deploy
2. Toggle "Auto-Deploy" off and on
3. Verify GitHub webhook exists
```

### Issue 4: Environment Variables Not Loading

**Symptoms**:
```python
KeyError: 'DATABRICKS_TOKEN'
Configuration check: {configured: false}
```

**Solution**:
1. In Render Dashboard → Environment
2. Add all required variables:
   ```
   ATLAN_BASE_URL=https://partner-sandbox.atlan.com
   ATLAN_API_KEY=your-token-here
   DATABRICKS_WORKSPACE_URL=https://your-workspace.databricks.com
   DATABRICKS_TOKEN=your-databricks-token
   ```
3. Click "Save Changes"
4. Restart service

### Issue 5: Build Cache Issues

**Symptoms**:
- Old code running despite new deployment
- Dependencies not updating
- "Module not found" errors

**Solution**:
```bash
# Clear build cache
1. Render Dashboard → Settings
2. Click "Clear Build Cache"
3. Trigger new deployment

# Force dependency reinstall
- Modify requirements.txt (add/remove space)
- Commit and push
```

## Deployment Process Step-by-Step

### Initial Setup

1. **Prepare Repository**:
```bash
# Required files
touch .python-version
echo "3.11.10" > .python-version

touch Procfile
echo "web: gunicorn app:app" > Procfile

# Ensure requirements.txt is complete
pip freeze > requirements.txt
```

2. **Connect to Render**:
- New → Web Service
- Connect GitHub repository
- Select main branch
- Name: atlan-sdr-metadata

3. **Configure Build Settings**:
- Build Command: `pip install -r requirements.txt`
- Start Command: (auto-detected from Procfile)
- Auto-Deploy: Yes

4. **Set Environment Variables**:
- Add all required API keys
- Save changes

### Deployment Workflow

1. **Local Development**:
```bash
# Test locally first
python app.py
# Verify at http://localhost:5000
```

2. **Commit Changes**:
```bash
git add -A
git commit -m "Description of changes"
git push origin main
```

3. **Monitor Deployment**:
- Watch Render logs in real-time
- Check for build errors
- Verify successful start

4. **Verify Production**:
```bash
# Test the deployed app
curl https://atlan-sdr-metadata.onrender.com/api/config
# Should return: {"configured": true}
```

## Build Optimization

### Caching Strategy

Render caches dependencies between builds:
- First build: ~2-3 minutes
- Subsequent builds: ~30 seconds

**To Maximize Cache Hits**:
1. Don't change Python version unnecessarily
2. Keep requirements.txt stable
3. Use specific versions (not ranges)

### Build Performance

**Typical Build Timeline**:
```
00:00 - Build started
00:05 - Cloning repository
00:10 - Python version detected
00:15 - Installing dependencies
01:30 - Build complete
01:35 - Starting service
01:40 - Service live
```

## Debugging Deployments

### Useful Render Log Searches

```bash
# Find Python version
"Python version:"

# Find build errors
"ERROR:" OR "Failed"

# Find startup issues
"Listening at:" OR "Worker"

# Find configuration issues
"Configuration check:"
```

### Common Log Patterns

**Successful Deployment**:
```
==> Cloning from https://github.com/GeneArnold/atlan-sdr-metadata.git
==> Using Python version: 3.11.10
==> Installing dependencies
    Successfully installed Flask-3.0.0 ...
==> Build successful
==> Starting service with 'gunicorn app:app'
    [INFO] Listening at: http://0.0.0.0:10000
```

**Failed Deployment**:
```
==> Build failed
==> Python version 3.14.0 not supported
==> Add a Procfile to your root directory
==> ModuleNotFoundError: No module named 'pyatlan'
```

## Rollback Procedures

### Quick Rollback

1. Render Dashboard → Events
2. Find last successful deployment
3. Click "Rollback to this version"
4. Confirm rollback

### Manual Rollback via Git

```bash
# Find last working commit
git log --oneline

# Reset to that commit
git reset --hard <commit-hash>

# Force push (careful!)
git push --force origin main
```

## Monitoring and Health Checks

### Health Check Endpoint

Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'configured': bool(DATABRICKS_TOKEN)
    })
```

### Render Health Checks

1. Settings → Health Check
2. Path: `/health`
3. Timeout: 10 seconds
4. Interval: 30 seconds

## Production Best Practices

### 1. Zero-Downtime Deployments

Render automatically provides:
- Blue-green deployments
- Health check validation
- Automatic rollback on failures

### 2. Environment Management

```python
# Use python-dotenv for local dev
from dotenv import load_dotenv
load_dotenv()

# Render provides env vars automatically
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
```

### 3. Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 4. Error Handling

```python
@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({
        'error': 'Internal server error',
        'message': str(error) if app.debug else 'An error occurred'
    }), 500
```

## Deployment Checklist

### Pre-Deployment

- [ ] Test locally with `python app.py`
- [ ] Verify `.python-version` exists with `3.11.10`
- [ ] Verify `Procfile` exists with correct syntax
- [ ] Check `requirements.txt` is up to date
- [ ] Ensure all env vars documented

### During Deployment

- [ ] Push to GitHub main branch
- [ ] Monitor Render logs for build progress
- [ ] Watch for any error messages
- [ ] Verify successful service start

### Post-Deployment

- [ ] Test `/api/config` endpoint
- [ ] Test chat interface loads
- [ ] Verify no console errors
- [ ] Check auto-deploy is still enabled
- [ ] Document any issues encountered

## Emergency Contacts

### When Things Go Wrong

1. **Check Render Status**: https://status.render.com
2. **Review Recent Changes**: GitHub commit history
3. **Check Environment Variables**: Render Dashboard
4. **Review Full Logs**: Last 1000 lines in Render
5. **Rollback if Needed**: Use Render's rollback feature

## Summary

Successful deployment requires:
1. Correct Python version (3.11.10)
2. Proper Procfile configuration
3. Complete requirements.txt
4. All environment variables set
5. Monitoring deployment logs

The most common issues are Python version mismatches and missing configuration files. Always test locally first and monitor deployment logs carefully. When in doubt, check the `.python-version` and `Procfile` files first.