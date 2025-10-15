import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'reviews.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            code_content TEXT NOT NULL,
            review_report TEXT NOT NULL,
            errors_found INTEGER,
            warnings_found INTEGER,
            suggestions_count INTEGER,
            code_quality_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def save_review(filename, file_type, file_size, code_content, review_report, 
                errors_found, warnings_found, suggestions_count, quality_score):
    """Save a code review to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO code_reviews 
        (filename, file_type, file_size, code_content, review_report, 
         errors_found, warnings_found, suggestions_count, code_quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, file_type, file_size, code_content, json.dumps(review_report),
          errors_found, warnings_found, suggestions_count, quality_score))
    
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return review_id

def get_all_reviews():
    """Retrieve all code reviews from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, file_size, errors_found, 
               warnings_found, suggestions_count, code_quality_score, timestamp
        FROM code_reviews
        ORDER BY timestamp DESC
    ''')
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

def get_review_by_id(review_id):
    """Retrieve a specific review by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM code_reviews WHERE id = ?
    ''', (review_id,))
    
    review = cursor.fetchone()
    conn.close()
    
    return review

def delete_review_by_id(review_id):
    """Delete a specific review by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if review exists
    cursor.execute('SELECT id FROM code_reviews WHERE id = ?', (review_id,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute('DELETE FROM code_reviews WHERE id = ?', (review_id,))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def delete_all_reviews():
    """Delete all reviews from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM code_reviews')
    conn.commit()
    
    # Reset the auto-increment counter
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="code_reviews"')
    conn.commit()
    conn.close()
    
    return True

def get_reviews_by_date_range(start_date, end_date):
    """Get reviews within a specific date range"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, file_size, errors_found,
               warnings_found, suggestions_count, code_quality_score, timestamp
        FROM code_reviews
        WHERE DATE(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp DESC
    ''', (start_date, end_date))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

def get_statistics():
    """Get comprehensive statistics about all reviews"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM code_reviews')
    total_reviews = cursor.fetchone()[0]
    
    if total_reviews == 0:
        conn.close()
        return None
    
    # Get aggregate statistics
    cursor.execute('''
        SELECT 
            AVG(code_quality_score) as avg_quality,
            MIN(code_quality_score) as min_quality,
            MAX(code_quality_score) as max_quality,
            SUM(errors_found) as total_errors,
            SUM(warnings_found) as total_warnings,
            SUM(suggestions_count) as total_suggestions,
            AVG(errors_found) as avg_errors,
            AVG(warnings_found) as avg_warnings,
            AVG(file_size) as avg_file_size
        FROM code_reviews
    ''')
    
    stats_row = cursor.fetchone()
    
    # Get file type distribution
    cursor.execute('''
        SELECT file_type, COUNT(*) as count
        FROM code_reviews
        GROUP BY file_type
        ORDER BY count DESC
    ''')
    
    file_types = cursor.fetchall()
    
    # Get recent activity (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) 
        FROM code_reviews 
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
    ''')
    
    recent_activity = cursor.fetchone()[0]
    
    conn.close()
    
    statistics = {
        "total_reviews": total_reviews,
        "average_quality": round(stats_row[0], 2) if stats_row[0] else 0,
        "min_quality": stats_row[1],
        "max_quality": stats_row[2],
        "total_errors": stats_row[3],
        "total_warnings": stats_row[4],
        "total_suggestions": stats_row[5],
        "average_errors": round(stats_row[6], 2) if stats_row[6] else 0,
        "average_warnings": round(stats_row[7], 2) if stats_row[7] else 0,
        "average_file_size": round(stats_row[8], 2) if stats_row[8] else 0,
        "recent_activity_7d": recent_activity,
        "file_type_distribution": [
            {"type": ft[0], "count": ft[1]} for ft in file_types
        ]
    }
    
    return statistics

def search_reviews(search_term):
    """Search reviews by filename"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, file_size, errors_found,
               warnings_found, suggestions_count, code_quality_score, timestamp
        FROM code_reviews
        WHERE filename LIKE ?
        ORDER BY timestamp DESC
    ''', (f'%{search_term}%',))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

def get_reviews_by_quality_range(min_score, max_score):
    """Get reviews within a quality score range"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, file_size, errors_found,
               warnings_found, suggestions_count, code_quality_score, timestamp
        FROM code_reviews
        WHERE code_quality_score BETWEEN ? AND ?
        ORDER BY code_quality_score DESC
    ''', (min_score, max_score))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

def get_top_quality_reviews(limit=10):
    """Get top quality reviews"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, code_quality_score, timestamp
        FROM code_reviews
        ORDER BY code_quality_score DESC
        LIMIT ?
    ''', (limit,))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

def get_worst_quality_reviews(limit=10):
    """Get worst quality reviews (needs improvement)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, file_type, code_quality_score, timestamp
        FROM code_reviews
        ORDER BY code_quality_score ASC
        LIMIT ?
    ''', (limit,))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return reviews

if __name__ == "__main__":
    init_db()
    print("✅ Database setup complete!")
    
    # Print statistics if any reviews exist
    stats = get_statistics()
    if stats:
        print("\n📊 Current Statistics:")
        print(f"   Total Reviews: {stats['total_reviews']}")
        print(f"   Average Quality: {stats['average_quality']}/100")
        print(f"   Total Errors Found: {stats['total_errors']}")
        print(f"   Recent Activity (7d): {stats['recent_activity_7d']}")
    else:
        print("\n📊 No reviews in database yet")