"""
Atlan SDR External Metadata Viewer - Minimal Flask App
Ready for immediate Databricks deployment
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)

# Enable CORS for Atlan domains
CORS(app, origins=[
    "https://home.atlan.com",
    "https://partner-sandbox.atlan.com",
    "http://localhost:3001"  # For testing
])

# Mock external metadata database (replace with real DB later)
EXTERNAL_METADATA = {
    'df36986b-e3f5-45b9-8b58-bf292b54868c': {
        'asset_name': 'customer_transactions',
        'business_owner': 'John Smith',
        'data_classification': 'Confidential',
        'quality_score': 95,
        'row_count': 1234567,
        'storage_gb': 45.6,
        'usage_count': 1234,
        'error_rate': 0.02,
        'last_audit': '2024-02-15',
        'custom_tags': ['financial', 'pii', 'critical'],
        'dependencies': ['product_catalog', 'user_profiles'],
        'notes': 'This table contains sensitive customer transaction data. Regular audits required for compliance.',
        'last_updated': datetime.now().isoformat()
    },
    'a7c2e9f1-4d5b-6a8c-9f0e-1b3d5e7f9a1c': {
        'asset_name': 'product_catalog',
        'business_owner': 'Sarah Johnson',
        'data_classification': 'Internal',
        'quality_score': 88,
        'row_count': 98765,
        'storage_gb': 2.3,
        'usage_count': 567,
        'error_rate': 0.01,
        'last_audit': '2024-01-20',
        'custom_tags': ['inventory', 'public-facing'],
        'dependencies': ['inventory_status', 'pricing_rules'],
        'notes': 'Product catalog synchronized with e-commerce platform every 15 minutes.',
        'last_updated': datetime.now().isoformat()
    },
    'b5d8f3c2-6e1a-4b9d-8c2f-3a5b7d9e1f4c': {
        'asset_name': 'user_profiles',
        'business_owner': 'Mike Chen',
        'data_classification': 'Highly Confidential',
        'quality_score': 99,
        'row_count': 5432109,
        'storage_gb': 128.9,
        'usage_count': 2345,
        'error_rate': 0.001,
        'last_audit': '2024-02-28',
        'custom_tags': ['gdpr', 'user-data', 'encrypted'],
        'dependencies': ['authentication_logs', 'session_data'],
        'notes': 'Contains PII data. GDPR compliance checks automated. Encrypted at rest and in transit.',
        'last_updated': datetime.now().isoformat()
    },
    # Real Atlan asset - Wide World Importers - Processed Gold
    'ca146cea-c06c-4652-a1af-99515f3073ac': {
        'asset_name': 'Wide World Importers - Processed Gold',
        'business_owner': 'Gene Arnold',
        'data_classification': 'Business Critical',
        'quality_score': 98,
        'row_count': 8750432,
        'storage_gb': 256.8,
        'usage_count': 5678,
        'error_rate': 0.002,
        'last_audit': '2024-03-08',
        'custom_tags': ['gold-tier', 'processed', 'analytics-ready', 'wide-world'],
        'dependencies': ['raw_imports', 'staging_tables', 'dimension_tables'],
        'notes': 'This is the gold layer processed data from Wide World Importers. Data is fully validated, cleaned, and ready for analytics consumption. Updated daily at 2 AM UTC.',
        'last_updated': datetime.now().isoformat()
    }
}

@app.route('/')
def index():
    """Main page that receives postMessage from Atlan"""
    return render_template('index.html')

@app.route('/api/metadata/<guid>')
def get_metadata(guid):
    """API endpoint to fetch metadata for a specific asset"""
    metadata = EXTERNAL_METADATA.get(guid)

    if metadata:
        return jsonify({
            'success': True,
            'data': metadata
        })
    else:
        # Return default metadata for unknown assets
        return jsonify({
            'success': True,
            'data': {
                'asset_name': 'Unknown Asset',
                'business_owner': 'Not Specified',
                'data_classification': 'Unknown',
                'quality_score': 0,
                'notes': f'No external metadata found for asset {guid}',
                'last_updated': datetime.now().isoformat()
            }
        })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'atlan-sdr-metadata'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)