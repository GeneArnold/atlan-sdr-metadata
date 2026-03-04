# Atlan SDR Integration - External Metadata Viewer

## What We Built
A Flask app that displays external metadata for Atlan assets when embedded as an SDR custom app.

**Live URL:** https://atlan-sdr-metadata.onrender.com
**GitHub:** https://github.com/GeneArnold/atlan-sdr-metadata

## How It Works
1. User views an asset in Atlan
2. Atlan sends asset GUID via postMessage to our embedded app
3. App displays external metadata for that specific asset
4. Currently shows mock data for demo purposes

## Current Mock Data Assets
We have mock external metadata for these GUIDs:
- `df36986b-e3f5-45b9-8b58-bf292b54868c` (customer_transactions)
- `a7c2e9f1-4d5b-6a8c-9f0e-1b3d5e7f9a1c` (product_catalog)
- `b5d8f3c2-6e1a-4b9d-8c2f-3a5b7d9e1f4c` (user_profiles)

## What We Need From Your Instance
**3-5 real asset GUIDs** from your demo instance so we can add mock metadata for them. For example:
- A Table asset GUID
- A Column asset GUID
- A GlossaryTerm asset GUID

Just send us the GUIDs and asset names, we'll add mock external metadata.

## Setup in Atlan
1. **Admin → Custom Apps → Add SDR App**
2. **App URL:** `https://atlan-sdr-metadata.onrender.com`
3. **Name:** External Metadata Viewer
4. **Display Location:** Asset sidebar or custom tab
5. **Asset Types:** Configure which assets should show this tab

## Testing
Once embedded, open any asset with mock data and you'll see:
- Business owner information
- Quality scores and metrics
- Custom tags and classifications
- Usage statistics
- Dependencies

## Technical Details
- **Framework:** Python Flask with JavaScript frontend
- **Communication:** postMessage protocol
- **Hosting:** Render.com (publicly accessible)
- **CORS:** Enabled for Atlan domains

## Quick Test (Browser Console)
```javascript
// Test without embedding - run on our URL
window.postMessage({
  type: 'ATLAN_AUTH_CONTEXT',
  payload: { page: { params: { id: 'YOUR-ASSET-GUID-HERE' }}}
}, '*');
```

## Contact
Gene Arnold - Ready to add mock data for your instance's GUIDs!