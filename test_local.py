#!/usr/bin/env python3
"""
Quick local test script
Run this to test the app locally before deploying to Databricks
"""

print("Testing Flask app locally...")
print("=" * 50)
print("")
print("1. Starting Flask server on http://localhost:8080")
print("2. Open browser to http://localhost:8080")
print("3. In browser console, run:")
print("")
print("window.postMessage({")
print("  type: 'ATLAN_AUTH_CONTEXT',")
print("  payload: {")
print("    page: {")
print("      params: {")
print("        id: 'df36986b-e3f5-45b9-8b58-bf292b54868c'")
print("      }")
print("    }")
print("  }")
print("}, '*');")
print("")
print("4. You should see the external metadata appear!")
print("")
print("=" * 50)
print("Starting server...")
print("")

import app
app.app.run(host='0.0.0.0', port=8080, debug=True)