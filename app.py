"""
Atlan Genie Chat Interface
Embedded chat interface for Databricks Genie spaces within Atlan
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import requests
import time
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from datetime import datetime
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.assets import Asset

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for Atlan domains
CORS(app, origins=[
    "https://home.atlan.com",
    "https://partner-sandbox.atlan.com",
    "http://localhost:3001"
])

# Configuration from environment
DATABRICKS_WORKSPACE_URL = os.getenv('DATABRICKS_WORKSPACE_URL', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN', '')
ATLAN_HOST = os.getenv('ATLAN_HOST', 'https://partner-sandbox.atlan.com')
ATLAN_API_TOKEN = os.getenv('ATLAN_API_TOKEN', '')

class GenieClient:
    """Simplified Genie client for chat interface"""

    def __init__(self, workspace_url: str, token: str):
        self.workspace_url = workspace_url.rstrip("/")
        self.token = token
        self.api_base = f"{self.workspace_url}/api/2.0/genie"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def start_conversation(self, space_id: str, question: str) -> Tuple[str, str]:
        """Start a new conversation"""
        url = f"{self.api_base}/spaces/{space_id}/start-conversation"
        payload = {"content": question}

        response = requests.post(url, json=payload, headers=self.headers, timeout=30.0)
        if response.status_code == 401:
            raise Exception("Authentication failed. Check your Databricks token.")
        response.raise_for_status()
        data = response.json()
        return data["conversation_id"], data["message_id"]

    def continue_conversation(self, space_id: str, conversation_id: str, question: str) -> str:
        """Continue existing conversation"""
        url = f"{self.api_base}/spaces/{space_id}/conversations/{conversation_id}/messages"
        payload = {"content": question}

        response = requests.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return data["message_id"]

    def get_message_status(self, space_id: str, conversation_id: str, message_id: str) -> Dict[str, Any]:
        """Get message status and results"""
        url = f"{self.api_base}/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"

        response = requests.get(url, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def wait_for_response(
        self,
        space_id: str,
        conversation_id: str,
        message_id: str,
        max_wait: int = 30
    ) -> Dict[str, Any]:
        """Poll and wait for response"""
        start_time = time.time()
        poll_interval = 1.0

        while time.time() - start_time < max_wait:
            try:
                message = self.get_message_status(space_id, conversation_id, message_id)
                status = message.get("status", "UNKNOWN")

                if status == "COMPLETED":
                    # Extract response
                    result = {
                        "status": "completed",
                        "text_response": None,
                        "sql_query": None
                    }

                    attachments = message.get("attachments", [])
                    for attachment in attachments:
                        if "text" in attachment and "content" in attachment["text"]:
                            result["text_response"] = attachment["text"]["content"]
                        if attachment.get("query"):
                            result["sql_query"] = attachment["query"].get("query")

                    return result

                elif status in ["FAILED", "CANCELLED"]:
                    return {"status": "failed", "error": f"Message {status}"}

                time.sleep(min(poll_interval * 1.5, 5))

            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {"status": "timeout", "error": "Response timeout"}

# Initialize Genie client
genie_client = None
if DATABRICKS_WORKSPACE_URL and DATABRICKS_TOKEN:
    genie_client = GenieClient(DATABRICKS_WORKSPACE_URL, DATABRICKS_TOKEN)

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/space/<space_guid>')
def get_space_info(space_guid):
    """Get space information from Atlan asset"""

    # First, check if we have Atlan API configured
    if ATLAN_API_TOKEN:
        try:
            # Initialize Atlan client with our API token and host
            os.environ['ATLAN_API_KEY'] = ATLAN_API_TOKEN
            os.environ['ATLAN_BASE_URL'] = ATLAN_HOST

            client = AtlanClient()

            # Get the asset by GUID
            asset = client.asset.get_by_guid(
                guid=space_guid,
                asset_type=Asset  # Generic asset type
            )

            # Get the "Genie Spaces Details" custom metadata set
            # Note: get_custom_metadata doesn't take a client parameter
            genie_spaces = asset.get_custom_metadata(name="Genie Spaces Details")

            # Access the spaceId field
            databricks_space_id = genie_spaces.get("spaceId") if genie_spaces else None

            if databricks_space_id:
                return jsonify({
                    'success': True,
                    'space_id': databricks_space_id,
                    'name': asset.name or 'Genie Space',
                    'description': asset.description or 'Databricks Genie space for data analysis',
                    'databricks_url': f"{DATABRICKS_WORKSPACE_URL}/genie/spaces/{databricks_space_id}"
                })
            else:
                # No Databricks space ID found in custom metadata
                return jsonify({
                    'success': False,
                    'error': 'No Databricks space ID found in Genie Spaces Details custom metadata',
                    'debug': {
                        'asset_name': asset.name,
                        'qualified_name': asset.qualified_name,
                        'custom_metadata': genie_spaces
                    }
                })

        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg or 'Unauthorized' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'Atlan API authentication failed. The API token has expired or is invalid.',
                    'suggestion': 'Please update the ATLAN_API_TOKEN in the .env file with a fresh token from Atlan.',
                    'demo_available': True
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Error fetching from Atlan: {error_msg}'
                })

    # Fallback to demo mode if no Atlan API configured
    else:
        # Demo mode - use a hardcoded space for testing
        if space_guid == 'demo-space-guid':
            return jsonify({
                'success': True,
                'space_id': '01f10ea33fc010dcb2dc604b75ac4336',
                'name': 'Wide World Importers Sales (Demo)',
                'description': 'Demo Genie space for testing',
                'databricks_url': f"{DATABRICKS_WORKSPACE_URL}/genie/spaces/01f10ea33fc010dcb2dc604b75ac4336"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Atlan API not configured. Set ATLAN_API_TOKEN to fetch real asset data.'
            })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message with Genie"""
    if not genie_client:
        return jsonify({
            'success': False,
            'error': 'Genie not configured. Set DATABRICKS_WORKSPACE_URL and DATABRICKS_TOKEN.'
        }), 503

    data = request.json
    space_id = data.get('space_id')
    message = data.get('message')
    conversation_id = data.get('conversation_id')

    if not space_id or not message:
        return jsonify({'success': False, 'error': 'Missing space_id or message'}), 400

    try:
        # Start or continue conversation
        if not conversation_id:
            conversation_id, message_id = genie_client.start_conversation(space_id, message)
        else:
            message_id = genie_client.continue_conversation(space_id, conversation_id, message)

        # Wait for response
        result = genie_client.wait_for_response(space_id, conversation_id, message_id)

        if result["status"] == "completed":
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'response': result.get('text_response', 'Query processed successfully'),
                'sql': result.get('sql_query')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to get response')
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config')
def get_config():
    """Check configuration status"""
    return jsonify({
        'configured': bool(DATABRICKS_WORKSPACE_URL and DATABRICKS_TOKEN),
        'workspace_url': DATABRICKS_WORKSPACE_URL[:30] + '...' if DATABRICKS_WORKSPACE_URL else None
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'app': 'atlan-genie-chat',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)