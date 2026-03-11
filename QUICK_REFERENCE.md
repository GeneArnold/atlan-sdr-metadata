# Databricks Genie + Atlan Integration - Quick Reference

## What We Built
A web-based chat interface that allows users to interact with Databricks Genie spaces directly from within Atlan's asset management platform.

**Live URL**: https://atlan-sdr-metadata.onrender.com

## How It Works
1. User finds Genie space in Atlan
2. Clicks "Launch Genie" custom tab
3. Chats with data using natural language
4. Gets answers with SQL queries shown
5. Can jump to full Databricks experience

## Tech Stack
- **Backend**: Python Flask + pyatlan SDK
- **Frontend**: Vanilla JavaScript + PostMessage API
- **Hosting**: Render (auto-deploy from GitHub)
- **APIs**: Databricks Genie Conversational API

## Key Files
```
app.py                    # Flask backend
templates/chat.html       # Chat interface
.python-version          # Python 3.11.10 (CRITICAL!)
Procfile                 # web: gunicorn app:app
requirements.txt         # Dependencies
```

## Environment Variables
```bash
ATLAN_BASE_URL=https://partner-sandbox.atlan.com
ATLAN_API_KEY=<your-token>
DATABRICKS_WORKSPACE_URL=https://<workspace>.databricks.com
DATABRICKS_TOKEN=<your-token>
```

## The Race Condition Fix

### Problem
Chat failed on first load, worked after refresh.

### Root Cause
Messages from Atlan arrived before our listener was ready.

### Solution
```javascript
// OLD (BROKEN)
window.addEventListener('load', () => {
    window.addEventListener('message', handler);
});

// NEW (FIXED)
// Set up listener IMMEDIATELY
window.addEventListener('message', handler);
```

### Key Changes
1. Message listener registered immediately (not waiting for DOM)
2. `isConfigured` starts as `undefined` (not `false`)
3. Configuration checked before DOM ready
4. Added proactive IFRAME_READY after 500ms
5. Enhanced logging with prefixes (`[INIT]`, `[MESSAGE]`, etc.)

## Deployment Issues We Solved

### Python Version
- **Problem**: Python 3.14 broke pyatlan
- **Fix**: `.python-version` file with `3.11.10`

### Missing Procfile
- **Problem**: Render didn't know how to start app
- **Fix**: Added `Procfile` with `web: gunicorn app:app`

### Auto-Deploy Failures
- **Problem**: Deploys stopped after errors
- **Fix**: Manual deploy, then re-enable auto-deploy

## API Flow

### 1. Get Space Info
```python
client = AtlanClient()
asset = client.asset.get_by_guid(guid=space_guid, asset_type=Asset)
custom_metadata = asset.get_custom_metadata(name="Genie Spaces Details")
space_id = custom_metadata.get("spaceId")
```

### 2. Start Conversation
```python
POST /api/2.0/ai/genie/spaces/{space_id}/conversations
```

### 3. Ask Question
```python
POST /api/2.0/ai/genie/spaces/{space_id}/conversations/{conversation_id}/queries
Body: {"query": "user question"}
```

### 4. Poll for Answer
```python
GET /api/2.0/ai/genie/spaces/{space_id}/conversations/{conversation_id}/queries/{query_id}
# Poll until status == 'COMPLETED'
```

## PostMessage Protocol

```javascript
// 1. Atlan sends handshake
{ type: 'ATLAN_HANDSHAKE', payload: { appId } }

// 2. We respond ready
{ type: 'IFRAME_READY', payload: { ready: true } }

// 3. Atlan sends context
{ type: 'ATLAN_AUTH_CONTEXT', payload: { page: { params: { id: 'asset-guid' } } } }

// 4. We load the space
loadSpace(guid)
```

## Security Considerations

```javascript
// Always validate origin
const allowedOrigins = [
    'https://home.atlan.com',
    'https://partner-sandbox.atlan.com'
];

if (!allowedOrigins.includes(event.origin)) return;

// Never use '*' for postMessage
window.parent.postMessage(data, event.origin); // Good
window.parent.postMessage(data, '*'); // Bad!
```

## Testing

### Local Test
```bash
python app.py
# Visit http://localhost:5000/chat?test=true
```

### Production Test
1. Open Atlan
2. Find Genie space
3. Click "Launch Genie" tab
4. Check browser console for errors
5. Try asking a question

### Debug Logs to Watch
```
[INIT] Checking configuration immediately
[MESSAGE] Received at 2026-03-10T18:14:17.062Z
[HANDSHAKE] Received, responding with IFRAME_READY
[AUTH_CONTEXT] Loading space with GUID: xxx
[LOAD_SPACE] Fetching space info
```

## Common Issues

### "Configuration Required" Error
- Check DATABRICKS_TOKEN in Render env vars
- Verify token has correct permissions

### Chat Won't Load
- Check browser console for errors
- Verify custom metadata has spaceId
- Check Atlan API token is valid

### Network Errors
- App has retry logic (3 attempts)
- Check CORS settings if cross-origin

## Monitoring

### Health Check
```bash
curl https://atlan-sdr-metadata.onrender.com/api/config
# Should return: {"configured": true}
```

### Key Metrics
- Time to first message: ~100ms
- Configuration check: ~200ms
- Space load time: ~500ms
- Genie response: 2-5 seconds

## Quick Commands

### Deploy Changes
```bash
git add -A
git commit -m "Your changes"
git push origin main
# Watch Render logs for deployment
```

### Rollback
1. Render Dashboard → Events
2. Find last working deployment
3. Click "Rollback"

### Clear Cache
1. Render Dashboard → Settings
2. "Clear Build Cache"
3. Trigger new deployment

## Lessons Learned

1. **iframe timing is tricky** - Set up listeners before anything else
2. **Python versions matter** - Be explicit with `.python-version`
3. **State management** - Use `undefined` for "not checked yet"
4. **Logging saves debugging time** - Add prefixes and timestamps
5. **Retry logic helps** - Networks are unreliable
6. **Test the unhappy path** - Clear cache, use incognito

## Next Steps

- [ ] OAuth 2.0 implementation
- [ ] Token refresh mechanism
- [ ] Conversation history
- [ ] Export functionality
- [ ] WebSocket for real-time

## Contact Info

- **GitHub**: https://github.com/GeneArnold/atlan-sdr-metadata
- **Live App**: https://atlan-sdr-metadata.onrender.com
- **Issues**: Use GitHub Issues for bug reports

---

**Remember**: The race condition fix was all about TIMING. Set up your listeners early, check your state properly, and always have a fallback plan!