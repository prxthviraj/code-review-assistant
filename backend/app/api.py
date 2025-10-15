from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from llm_analyzer import CodeAnalyzer
from database import (
    init_db, save_review, get_all_reviews, get_review_by_id, 
    delete_review_by_id, delete_all_reviews, get_reviews_by_date_range,
    get_statistics
)
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'py', 'js', 'java', 'cpp', 'c', 'h', 'hpp',
    'html', 'css', 'tsx', 'jsx', 'go', 'rs', 
    'php', 'rb', 'swift', 'kt', 'cs', 'scala'
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialize
init_db()
analyzer = CodeAnalyzer()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_language(filename):
    """Detect programming language from file extension"""
    ext_to_lang = {
        'py': 'Python', 'js': 'JavaScript', 'jsx': 'React',
        'ts': 'TypeScript', 'tsx': 'React TypeScript',
        'java': 'Java', 'cpp': 'C++', 'c': 'C',
        'h': 'C Header', 'hpp': 'C++ Header',
        'go': 'Go', 'rs': 'Rust', 'php': 'PHP',
        'rb': 'Ruby', 'swift': 'Swift', 'kt': 'Kotlin',
        'cs': 'C#', 'scala': 'Scala', 'html': 'HTML',
        'css': 'CSS'
    }
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext_to_lang.get(ext, 'Unknown')

def calculate_code_metrics(code_content):
    """Calculate basic code metrics"""
    lines = code_content.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    blank_lines = len([line for line in lines if not line.strip()])
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    
    return {
        'total_lines': total_lines,
        'code_lines': code_lines,
        'blank_lines': blank_lines,
        'comment_lines': comment_lines,
        'comment_ratio': round((comment_lines / code_lines * 100) if code_lines > 0 else 0, 2)
    }

# ========================================
# CORE ENDPOINTS
# ========================================

@app.route('/')
def home():
    """API health check"""
    return jsonify({
        "message": "Code Review Assistant API",
        "version": "2.0",
        "status": "running",
        "endpoints": {
            "review": "/api/review [POST]",
            "batch_review": "/api/batch-review [POST]",
            "reviews": "/api/reviews [GET, DELETE]",
            "review_detail": "/api/review/<id> [GET, DELETE]",
            "statistics": "/api/statistics [GET]",
            "export": "/api/review/<id>/export [GET]",
            "search": "/api/reviews/search [GET]",
            "compare": "/api/reviews/compare [POST]",
            "trends": "/api/trends [GET]"
        }
    })

@app.route('/api/review', methods=['POST'])
def review_code():
    """Upload and review a single code file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()
        
        # Get file metadata
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        language = detect_language(filename)
        
        # Calculate metrics
        metrics = calculate_code_metrics(code_content)
        
        # Analyze with LLM
        print(f"🔍 Analyzing {filename} ({language})...")
        analysis = analyzer.analyze_code(code_content, filename)
        report = analyzer.generate_report(analysis, filename)
        
        # Add metrics to report
        report['code_metrics'] = metrics
        report['language'] = language
        
        # Save to database
        review_id = save_review(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            code_content=code_content,
            review_report=report,
            errors_found=report['metrics']['total_errors'],
            warnings_found=report['metrics']['total_warnings'],
            suggestions_count=report['metrics']['total_suggestions'],
            quality_score=report['overall_score']
        )
        
        # Clean up
        os.remove(file_path)
        
        print(f"✅ Review completed for {filename} (ID: {review_id})")
        
        return jsonify({
            "success": True,
            "review_id": review_id,
            "report": report,
            "metrics": metrics,
            "language": language
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch-review', methods=['POST'])
def batch_review():
    """Upload and review multiple files at once"""
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({"error": "No files selected"}), 400
    
    results = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code_content = f.read()
                
                file_size = os.path.getsize(file_path)
                file_type = filename.rsplit('.', 1)[1].lower()
                language = detect_language(filename)
                
                print(f"🔍 Batch analyzing {filename}...")
                analysis = analyzer.analyze_code(code_content, filename)
                report = analyzer.generate_report(analysis, filename)
                
                report['language'] = language
                
                review_id = save_review(
                    filename=filename,
                    file_type=file_type,
                    file_size=file_size,
                    code_content=code_content,
                    review_report=report,
                    errors_found=report['metrics']['total_errors'],
                    warnings_found=report['metrics']['total_warnings'],
                    suggestions_count=report['metrics']['total_suggestions'],
                    quality_score=report['overall_score']
                )
                
                os.remove(file_path)
                
                results.append({
                    "filename": filename,
                    "review_id": review_id,
                    "quality_score": report['overall_score'],
                    "status": "success"
                })
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        else:
            errors.append({
                "filename": file.filename,
                "error": "File type not allowed"
            })
    
    print(f"✅ Batch review completed: {len(results)} successful, {len(errors)} failed")
    
    return jsonify({
        "success": True,
        "results": results,
        "errors": errors,
        "total": len(results),
        "failed": len(errors)
    }), 200

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews with optional filtering"""
    try:
        # Get query parameters for filtering
        limit = request.args.get('limit', type=int, default=None)
        min_score = request.args.get('min_score', type=int, default=None)
        max_score = request.args.get('max_score', type=int, default=None)
        language = request.args.get('language', default=None)
        
        reviews = get_all_reviews()
        
        reviews_list = []
        for review in reviews:
            review_dict = {
                "id": review[0],
                "filename": review[1],
                "file_type": review[2],
                "file_size": review[3],
                "errors_found": review[4],
                "warnings_found": review[5],
                "suggestions_count": review[6],
                "quality_score": review[7],
                "timestamp": review[8]
            }
            
            # Apply filters
            if min_score and review_dict['quality_score'] < min_score:
                continue
            if max_score and review_dict['quality_score'] > max_score:
                continue
            if language:
                # Would need to store language in DB for this
                pass
            
            reviews_list.append(review_dict)
        
        # Apply limit
        if limit:
            reviews_list = reviews_list[:limit]
        
        return jsonify({
            "success": True,
            "total": len(reviews_list),
            "reviews": reviews_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews', methods=['DELETE'])
def clear_all_reviews():
    """Delete all reviews"""
    try:
        delete_all_reviews()
        print("🗑️ All reviews cleared")
        
        return jsonify({
            "success": True,
            "message": "All reviews deleted successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Error clearing reviews: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/review/<int:review_id>', methods=['GET'])
def get_review_detail(review_id):
    """Get detailed review by ID"""
    try:
        review = get_review_by_id(review_id)
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        review_data = {
            "id": review[0],
            "filename": review[1],
            "file_type": review[2],
            "file_size": review[3],
            "code_content": review[4],
            "review_report": json.loads(review[5]),
            "errors_found": review[6],
            "warnings_found": review[7],
            "suggestions_count": review[8],
            "quality_score": review[9],
            "timestamp": review[10]
        }
        
        return jsonify({
            "success": True,
            "review": review_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/review/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Delete a specific review"""
    try:
        result = delete_review_by_id(review_id)
        
        if result:
            print(f"🗑️ Review {review_id} deleted")
            return jsonify({
                "success": True,
                "message": f"Review {review_id} deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Review not found"}), 404
        
    except Exception as e:
        print(f"❌ Error deleting review: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ========================================
# ADVANCED FEATURES
# ========================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics_endpoint():
    """Get comprehensive statistics about all reviews"""
    try:
        stats = get_statistics()
        
        if not stats:
            return jsonify({
                "success": True,
                "statistics": {
                    "total_reviews": 0,
                    "average_quality": 0,
                    "total_errors": 0,
                    "total_warnings": 0,
                    "total_suggestions": 0
                }
            }), 200
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/search', methods=['GET'])
def search_reviews():
    """Search reviews by filename or content"""
    try:
        query = request.args.get('q', default='', type=str)
        
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        all_reviews = get_all_reviews()
        results = []
        
        for review in all_reviews:
            if query.lower() in review[1].lower():  # Search in filename
                results.append({
                    "id": review[0],
                    "filename": review[1],
                    "quality_score": review[7],
                    "timestamp": review[8]
                })
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/review/<int:review_id>/export', methods=['GET'])
def export_review(review_id):
    """Export review as JSON file"""
    try:
        review = get_review_by_id(review_id)
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        review_data = {
            "id": review[0],
            "filename": review[1],
            "file_type": review[2],
            "file_size": review[3],
            "review_report": json.loads(review[5]),
            "errors_found": review[6],
            "warnings_found": review[7],
            "suggestions_count": review[8],
            "quality_score": review[9],
            "timestamp": review[10],
            "exported_at": datetime.now().isoformat()
        }
        
        # Create JSON file in memory
        json_data = json.dumps(review_data, indent=2)
        buffer = io.BytesIO()
        buffer.write(json_data.encode('utf-8'))
        buffer.seek(0)
        
        filename = f"review_{review_id}_{review[1]}.json"
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/compare', methods=['POST'])
def compare_reviews():
    """Compare two code reviews"""
    try:
        data = request.get_json()
        
        if not data or 'review_id_1' not in data or 'review_id_2' not in data:
            return jsonify({"error": "Two review IDs required"}), 400
        
        review1 = get_review_by_id(data['review_id_1'])
        review2 = get_review_by_id(data['review_id_2'])
        
        if not review1 or not review2:
            return jsonify({"error": "One or both reviews not found"}), 404
        
        report1 = json.loads(review1[5])
        report2 = json.loads(review2[5])
        
        comparison = {
            "review_1": {
                "id": review1[0],
                "filename": review1[1],
                "quality_score": review1[9],
                "errors": review1[6],
                "warnings": review1[7],
                "suggestions": review1[8]
            },
            "review_2": {
                "id": review2[0],
                "filename": review2[1],
                "quality_score": review2[9],
                "errors": review2[6],
                "warnings": review2[7],
                "suggestions": review2[8]
            },
            "differences": {
                "quality_score_diff": review2[9] - review1[9],
                "errors_diff": review2[6] - review1[6],
                "warnings_diff": review2[7] - review1[7],
                "suggestions_diff": review2[8] - review1[8]
            },
            "improvement": review2[9] > review1[9]
        }
        
        return jsonify({
            "success": True,
            "comparison": comparison
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get quality trends over time"""
    try:
        days = request.args.get('days', default=7, type=int)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        reviews = get_reviews_by_date_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        # Group by date
        trends = {}
        for review in reviews:
            date = review[8].split(' ')[0]  # Get date part
            if date not in trends:
                trends[date] = {
                    "count": 0,
                    "total_score": 0,
                    "total_errors": 0
                }
            trends[date]["count"] += 1
            trends[date]["total_score"] += review[7]
            trends[date]["total_errors"] += review[4]
        
        # Calculate averages
        trend_data = []
        for date, data in sorted(trends.items()):
            trend_data.append({
                "date": date,
                "reviews_count": data["count"],
                "average_quality": round(data["total_score"] / data["count"], 2),
                "total_errors": data["total_errors"]
            })
        
        return jsonify({
            "success": True,
            "period": f"Last {days} days",
            "trends": trend_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Code Review Assistant API v2.0")
    print("=" * 60)
    print("📍 API running at: http://localhost:5001")
    print("📝 Documentation: http://localhost:5001/")
    print("=" * 60)
    print("\n✨ Available Features:")
    print("  • Single & Batch File Analysis")
    print("  • Advanced Statistics")
    print("  • Search & Filter")
    print("  • Export Reviews (JSON)")
    print("  • Compare Reviews")
    print("  • Quality Trends")
    print("=" * 60)
    
    app.run(debug=True, port=5001, host='0.0.0.0')