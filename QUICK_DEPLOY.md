# 🚀 QUICK PUBLIC DEPLOYMENT OPTIONS

Since Databricks Apps require authentication, we need to deploy to a **PUBLIC cloud service**. Here are your fastest options:

## Option 1: Railway.app (FASTEST - 2 minutes)

Railway is the absolute fastest - just connect GitHub and deploy!

```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login and deploy
cd /Users/gene.arnold/WorkSpace/atlan-iframe/atlan-sdr-databricks
railway login
railway init
railway up

# Get your public URL
railway domain
```

**URL you'll get:** `https://your-app.railway.app`

## Option 2: Render.com (NO CREDIT CARD - 3 minutes)

1. Go to https://render.com
2. Sign up with GitHub
3. New → Web Service
4. Connect your repo OR use "Deploy from this computer"
5. Settings:
   - Name: `atlan-sdr-metadata`
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `python app.py`
6. Deploy!

**URL you'll get:** `https://atlan-sdr-metadata.onrender.com`

## Option 3: Heroku (5 minutes)

```bash
# Install Heroku CLI if needed
brew tap heroku/brew && brew install heroku

# Deploy
cd /Users/gene.arnold/WorkSpace/atlan-iframe/atlan-sdr-databricks
heroku create atlan-sdr-metadata
git init
git add .
git commit -m "Deploy Atlan SDR"
git push heroku main

# Open app
heroku open
```

**URL you'll get:** `https://atlan-sdr-metadata.herokuapp.com`

## Option 4: Replit (INSTANT - No install)

1. Go to https://replit.com
2. Create new Repl → Import from GitHub
3. Or just drag and drop our files
4. Click Run
5. Your app is instantly live!

**URL you'll get:** `https://atlan-sdr-metadata.your-username.repl.co`

## Option 5: Google Cloud Run (More setup but FREE)

```bash
# Install gcloud CLI if needed
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
EOF

# Deploy
gcloud run deploy atlan-sdr-metadata \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Get URL from output
```

**URL you'll get:** `https://atlan-sdr-metadata-xxxxx.run.app`

## Option 6: AWS Lambda + API Gateway (Serverless)

Use Zappa for easy Lambda deployment:

```bash
pip install zappa
zappa init
zappa deploy production
```

**URL you'll get:** `https://xxxxx.execute-api.region.amazonaws.com/production`

## 🏆 RECOMMENDED: Railway or Render

Both are:
- ✅ FREE to start
- ✅ No credit card required
- ✅ Deploy in under 3 minutes
- ✅ HTTPS by default
- ✅ No authentication required for public access
- ✅ Perfect for iframe embedding

## After Deployment

1. **Test your public URL** in a browser
2. **Test postMessage** in browser console:
```javascript
window.postMessage({
  type: 'ATLAN_AUTH_CONTEXT',
  payload: { page: { params: { id: 'df36986b-e3f5-45b9-8b58-bf292b54868c' }}}
}, '*');
```
3. **Register in Atlan** using your public URL

## The Architecture That Works

```
┌─────────────────────┐
│    Atlan Platform   │
│  ┌───────────────┐  │
│  │  Asset Viewer │  │
│  │   <iframe>    │  │
│  └───────┼───────┘  │
└──────────┼──────────┘
           │ postMessage
           ↓
┌──────────────────────┐
│  Public Cloud App    │
│  (Railway/Render)    │
│  - No auth required  │
│  - Receives GUID     │
│  - Shows metadata    │
└──────────────────────┘
           │ (optional)
           ↓
┌──────────────────────┐
│     Databricks       │
│  (Data Warehouse)    │
│  - Query via API     │
│  - Service Principal │
└──────────────────────┘
```

## Next: Connect to Real Databricks Data (Optional)

Once deployed, you can enhance the app to query real Databricks data:

```python
# In app.py, add Databricks SQL connector
from databricks import sql

def get_external_metadata(guid):
    connection = sql.connect(
        server_hostname=os.getenv('DATABRICKS_HOST'),
        http_path=os.getenv('DATABRICKS_HTTP_PATH'),
        access_token=os.getenv('DATABRICKS_TOKEN')
    )
    # Query your real metadata table
```

But for now, the mock data is perfect for proving the integration works!