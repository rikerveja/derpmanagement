from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/urls', methods=['GET'])
def get_api_urls():
    api_urls = []
    for rule in api_bp.url_map.iter_rules():
        if rule.endpoint != 'static' and '/api/' in str(rule):
            methods = ', '.join(rule.methods)
            api_urls.append({
                'endpoint': rule.endpoint,
                'url': str(rule),
                'methods': methods
            })
    return jsonify(api_urls)
