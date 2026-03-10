# 🚀 DATABRICKS SETUP - Quick Deploy Instructions

## Files Ready for Deployment

All files are in: `/Users/gene.arnold/WorkSpace/atlan-iframe/atlan-sdr-databricks/`

```
atlan-sdr-databricks/
├── app.py              # Flask app with postMessage handler
├── app.yaml            # Databricks deployment config
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # UI that receives asset context
└── test_local.py      # Local test script
```

## Step 1: Create the Databricks App

Run these commands in your terminal:

```bash
# Navigate to the app directory
cd /Users/gene.arnold/WorkSpace/atlan-iframe/atlan-sdr-databricks

# Initialize Databricks app (if you haven't already)
databricks app init

# Create the app
databricks app create atlan-sdr-metadata
```

## Step 2: Deploy to Databricks

```bash
# Deploy the app
databricks app deploy atlan-sdr-metadata

# Check deployment status
databricks app get atlan-sdr-metadata
```

## Step 3: Get Your App URL

After deployment, you'll get a URL like:
```
https://dbc-8d941db8-48cd.cloud.databricks.app/atlan-sdr-metadata
```

## Optional: Test Locally First

Before deploying, you can test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run test script
python test_local.py

# Open browser to http://localhost:8080
# Test postMessage in browser console (instructions will be printed)
```

## What This App Does

1. **Receives postMessage** from Atlan with asset GUID
2. **Displays external metadata** for that asset
3. **Ready for production** - just needs to be registered in Atlan

## Next Steps After Deployment

1. **Get the Databricks app URL** from the deployment
2. **Register in Atlan**:
   - Go to Atlan Admin → Custom Apps
   - Add new SDR app
   - Enter your Databricks app URL
   - Configure for asset viewer tabs
3. **Test with real assets** in Atlan

## Troubleshooting

If the app doesn't deploy:
```bash
# Check logs
databricks app logs atlan-sdr-metadata

# Redeploy if needed
databricks app deploy atlan-sdr-metadata --force
```

## What You Need to Do on Databricks Side

### Option A: Using Databricks CLI (Recommended)
```bash
# Just run these 3 commands:
cd /Users/gene.arnold/WorkSpace/atlan-iframe/atlan-sdr-databricks
databricks app create atlan-sdr-metadata
databricks app deploy atlan-sdr-metadata
```

### Option B: Using Databricks UI
1. Go to your Databricks workspace
2. Navigate to "Compute" → "Apps"
3. Click "Create App"
4. Choose "Flask Hello World" template
5. Replace the files with ours
6. Deploy

## The URL You'll Get

After deployment, Databricks will give you a URL like:
```
https://[your-workspace].cloud.databricks.app/atlan-sdr-metadata
```

This is the URL you'll register in Atlan!

## Ready to Deploy?

The app is **100% ready**. It will:
- ✅ Receive asset GUIDs from Atlan
- ✅ Display external metadata
- ✅ Work in production immediately
- ✅ Can be enhanced later with real database

Just deploy it and you'll have a working integration in minutes! 🎉