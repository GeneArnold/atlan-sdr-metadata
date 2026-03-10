# Atlan Genie Chat Interface

This app provides a chat interface for Databricks Genie spaces embedded in Atlan.

## Environment Variables Required

Set these in Render dashboard:

- `DATABRICKS_WORKSPACE_URL` - Your Databricks workspace URL
- `DATABRICKS_TOKEN` - Databricks personal access token
- `ATLAN_HOST` - Atlan instance URL (e.g., https://partner-sandbox.atlan.com)
- `ATLAN_API_TOKEN` - Atlan API token for fetching asset metadata

## Features

- Chat with Databricks Genie spaces directly from Atlan
- Automatic space ID extraction from Atlan custom metadata
- SQL query generation and display
- Conversation context maintained

## Deployment

This app is deployed on Render at: https://atlan-sdr-metadata.onrender.com

## Archive

The previous external metadata viewer app has been archived in the `archive_external_metadata/` folder.