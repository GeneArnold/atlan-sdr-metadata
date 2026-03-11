# Databricks Genie Integration for Atlan - Complete Documentation

## Executive Summary

We successfully built and deployed a web-based chatbot interface that enables users to interact with Databricks Genie spaces directly from within Atlan's asset management platform. Users can discover Genie spaces in Atlan, click on a custom tab to open the chat interface, ask questions about their data, and seamlessly transition to the full Databricks experience when needed.

**Live URL**: https://atlan-sdr-metadata.onrender.com

## Architecture Overview

### System Components

1. **Flask Web Application** (`app.py`)
   - Serves the chat interface
   - Handles API routing for Genie interactions
   - Manages authentication with both Atlan and Databricks
   - Uses pyatlan SDK to fetch custom metadata

2. **Genie Client Class**
   - Implements Databricks Conversational API
   - Manages conversation lifecycle (start, continue, poll)
   - Handles SQL query extraction and result formatting

3. **Frontend Chat Interface** (`templates/chat.html`)
   - Real-time chat UI with message bubbles
   - PostMessage protocol for Atlan iframe communication
   - SQL query display with syntax highlighting
   - Responsive design with typing indicators

4. **Deployment Infrastructure**
   - Hosted on Render at https://atlan-sdr-metadata.onrender.com
   - Python 3.11.10 runtime (critical for pyatlan compatibility)
   - Environment variables for secure credential storage

## Integration Flow

### User Workflow
1. User navigates to a Genie space asset in Atlan
2. Clicks on the "Launch Genie" custom tab
3. Chat interface loads in iframe with space context
4. User asks questions in natural language
5. System returns answers with SQL queries displayed
6. User can click "Open in Databricks" for full experience

### Technical Flow
```
Atlan → PostMessage(ATLAN_HANDSHAKE) → iframe
iframe → PostMessage(IFRAME_READY) → Atlan
Atlan → PostMessage(ATLAN_AUTH_CONTEXT with asset GUID) → iframe
iframe → Fetch space metadata via pyatlan SDK
iframe → Initialize Genie conversation
User → Submit question → Flask API
Flask → Databricks Genie API → Poll for results
Flask → Return response with SQL → Update UI
```

## Critical Implementation Details

### 1. PostMessage Race Condition Fix

**Problem**: Initial implementation had a race condition where the chat would error on first load but work after refresh.

**Root Causes**:
- Message listener setup happened after window.load
- Configuration check occurred too late
- Duplicate IFRAME_READY messages
- AUTH_CONTEXT arrived before configuration completed

**Solution**:
```javascript
// Set up message listener IMMEDIATELY (not waiting for DOM)
console.log('Setting up message listener at:', new Date().toISOString());

window.addEventListener('message', async (event) => {
    // Message handling logic
});

// Check configuration immediately
let isConfigured = undefined; // Start as undefined, not false
checkConfiguration();

// Proactive IFRAME_READY after 500ms if no handshake
setTimeout(() => {
    if (!handshakeReceived) {
        window.parent.postMessage({
            type: 'IFRAME_READY',
            payload: { ready: true }
        }, parentOrigin);
    }
}, 500);
```

**Key Insights**:
- Message listeners must be registered immediately on script load
- Configuration state should start as `undefined` to differentiate "not checked" from "false"
- Never wait for DOM ready for critical initialization
- Always validate message origin for security
- Include defensive checks for payload structure

### 2. Python Version Compatibility

**Problem**: Python 3.14 caused incompatibility with pyatlan/Pydantic v1.

**Solution**:
- Created `.python-version` file with `3.11.10`
- Render respects this file for Python version selection
- Critical for pyatlan SDK compatibility

### 3. Custom Metadata Access via pyatlan

**Implementation**:
```python
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.assets import Asset

client = AtlanClient()
asset = client.asset.get_by_guid(guid=space_guid, asset_type=Asset)
genie_spaces = asset.get_custom_metadata(name="Genie Spaces Details")
databricks_space_id = genie_spaces.get("spaceId") if genie_spaces else None
```

**Important**: `get_custom_metadata()` doesn't take a client parameter.

### 4. Databricks Genie Conversational API

**Key Endpoints**:
- Start conversation: `POST /api/2.0/ai/genie/spaces/{space_id}/conversations`
- Continue conversation: `POST /api/2.0/ai/genie/spaces/{space_id}/conversations/{conversation_id}/queries`
- Poll for results: `GET /api/2.0/ai/genie/spaces/{space_id}/conversations/{conversation_id}/queries/{query_id}`

**Polling Pattern**:
```python
def _poll_for_result(self, space_id, conversation_id, query_id, max_attempts=30):
    for attempt in range(max_attempts):
        response = requests.get(url, headers=self.headers)
        data = response.json()

        if data.get('status') == 'COMPLETED':
            return data
        elif data.get('status') == 'FAILED':
            raise Exception(f"Query failed: {data.get('error_message')}")

        time.sleep(1)
```

## Environment Configuration

### Required Environment Variables
```bash
# Atlan Configuration
ATLAN_BASE_URL=https://partner-sandbox.atlan.com
ATLAN_API_KEY=your-atlan-api-token

# Databricks Configuration
DATABRICKS_WORKSPACE_URL=https://your-workspace.databricks.com
DATABRICKS_TOKEN=your-databricks-token
```

### Render Deployment Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app` (via Procfile)
- **Python Version**: 3.11.10 (via .python-version)
- **Auto-Deploy**: Enabled from GitHub main branch

## Security Considerations

1. **Origin Validation**:
```javascript
const allowedOrigins = [
    'https://home.atlan.com',
    'https://partner-sandbox.atlan.com',
    'http://localhost:3001'
];
```

2. **Explicit Target Origins**: Never use `'*'` for postMessage
3. **Token Storage**: Environment variables only, never in code
4. **CORS Configuration**: Restrictive CORS headers in production

## Troubleshooting Guide

### Issue: Chat Errors on Initial Load
**Symptoms**: "errors out hardcore" on first click, works after refresh

**Fix Applied**:
1. Set message listener immediately on script load
2. Initialize `isConfigured` as `undefined`
3. Check configuration before DOM ready
4. Add retry logic for network errors

### Issue: Python Version Incompatibility
**Symptoms**: Deployment fails with Pydantic/pyatlan errors

**Fix**: Add `.python-version` file with `3.11.10`

### Issue: Missing Procfile
**Symptoms**: Render doesn't know how to start the app

**Fix**: Add `Procfile` with: `web: gunicorn app:app`

### Issue: Authentication Errors
**Symptoms**: 401 errors from Databricks API

**Fix**: Verify DATABRICKS_TOKEN is valid and has appropriate permissions

## Deployment Checklist

1. **GitHub Repository Setup**
   - [x] Code pushed to main branch
   - [x] `.python-version` file with `3.11.10`
   - [x] `Procfile` with gunicorn command
   - [x] `requirements.txt` with all dependencies

2. **Render Configuration**
   - [x] Connected to GitHub repo
   - [x] Auto-deploy enabled
   - [x] Environment variables set
   - [x] Python version detected from `.python-version`

3. **Atlan Configuration**
   - [x] Custom tab configured for Genie spaces
   - [x] Tab points to Render URL
   - [x] Custom metadata "Genie Spaces Details" with spaceId field

## Testing Procedures

### Local Testing
```bash
# Start local server
python app.py

# Test with query parameter
http://localhost:5000/chat?test=true
```

### Production Testing
1. Navigate to Genie space in Atlan
2. Click "Launch Genie" tab
3. Verify chat loads without refresh
4. Test sample questions
5. Check browser console for error-free operation

### Debug Logging
Look for prefixed logs in browser console:
- `[INIT]` - Initialization sequence
- `[MESSAGE]` - PostMessage events
- `[HANDSHAKE]` - Handshake protocol
- `[AUTH_CONTEXT]` - Asset context received
- `[LOAD_SPACE]` - Space loading process

## Performance Optimizations

1. **Build Caching**: Render caches Python dependencies between builds
2. **Retry Logic**: Network errors retry up to 3 times with 1-second delays
3. **Polling Timeout**: 30-second maximum for Genie API responses
4. **Message Debouncing**: Prevents duplicate handshake messages

## Future Enhancements

1. **Authentication**
   - Implement OAuth 2.0 with PKCE for production
   - Add token refresh mechanism
   - Support multiple authentication methods

2. **Features**
   - Conversation history persistence
   - Export chat transcripts
   - Multiple concurrent conversations
   - Rich media responses (charts, tables)

3. **Infrastructure**
   - Add Redis for session management
   - Implement WebSocket for real-time updates
   - Add comprehensive error tracking (Sentry)
   - Implement rate limiting

## Lessons Learned

1. **Race Conditions in iframes**
   - Always set up message listeners immediately
   - Don't wait for DOM ready for critical initialization
   - Use state variables to track initialization phases
   - Add defensive timeout-based fallbacks

2. **Python Version Management**
   - Be explicit about Python versions in deployment
   - Test compatibility early in development
   - Use `.python-version` for Render deployments
   - Stay on stable versions for production SDKs

3. **PostMessage Security**
   - Always validate message origins
   - Use explicit target origins
   - Validate payload structure defensively
   - Log all message events for debugging

4. **Deployment Automation**
   - Auto-deploy can fail silently after errors
   - Manual deploys may be needed after fixes
   - Monitor build logs closely
   - Test deployment pipeline early and often

## Support and Maintenance

### Common Maintenance Tasks
- Rotate API tokens quarterly
- Monitor Databricks API rate limits
- Update pyatlan SDK versions carefully
- Review security origins periodically

### Monitoring Points
- Render deployment status
- API response times
- Error rates in browser console
- User feedback on load times

### Contact Points
- **GitHub Repository**: https://github.com/GeneArnold/atlan-sdr-metadata
- **Deployment URL**: https://atlan-sdr-metadata.onrender.com
- **Issue Tracking**: GitHub Issues on the repository

## Conclusion

This integration successfully bridges Atlan's asset management capabilities with Databricks Genie's conversational AI, providing users with a seamless data exploration experience. The implementation overcame several technical challenges including iframe race conditions, Python compatibility issues, and complex authentication flows. The solution is now production-ready and actively serving users.

The key to success was careful attention to timing issues in iframe communication, proper state management, and thorough debugging with enhanced logging. The fixes implemented ensure reliable operation without requiring page refreshes or workarounds.