"""
Test Scripts for Code Review Assistant API v2.0
Run these to test all new features
"""

import requests
import json

API_URL = "http://localhost:5001"

def test_health_check():
    """Test 1: API Health Check"""
    print("\n" + "="*60)
    print("TEST 1: API Health Check")
    print("="*60)
    
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_single_upload():
    """Test 2: Single File Upload"""
    print("\n" + "="*60)
    print("TEST 2: Single File Upload")
    print("="*60)
    
    # Create a test file
    test_code = """
def hello():
    print("Hello World")

hello()
"""
    
    files = {'file': ('test.py', test_code)}
    response = requests.post(f"{API_URL}/api/review", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Review ID: {result.get('review_id')}")
    print(f"Quality Score: {result.get('report', {}).get('overall_score')}")

def test_batch_upload():
    """Test 3: Batch File Upload"""
    print("\n" + "="*60)
    print("TEST 3: Batch File Upload")
    print("="*60)
    
    # Create multiple test files
    files = [
        ('files', ('test1.py', 'def func1():\n    pass')),
        ('files', ('test2.py', 'def func2():\n    pass')),
        ('files', ('test3.py', 'def func3():\n    pass'))
    ]
    
    response = requests.post(f"{API_URL}/api/batch-review", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total Analyzed: {result.get('total')}")
    print(f"Failed: {result.get('failed')}")
    
    for item in result.get('results', []):
        print(f"  • {item['filename']}: Score {item['quality_score']}")

def test_get_reviews():
    """Test 4: Get All Reviews"""
    print("\n" + "="*60)
    print("TEST 4: Get All Reviews")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/reviews")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total Reviews: {result.get('total')}")
    
    for review in result.get('reviews', [])[:3]:  # Show first 3
        print(f"  • {review['filename']}: Score {review['quality_score']}")

def test_get_reviews_filtered():
    """Test 5: Get Reviews with Filters"""
    print("\n" + "="*60)
    print("TEST 5: Get Reviews with Filters (min_score=70)")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/reviews?min_score=70&limit=5")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Filtered Results: {result.get('total')}")
    
    for review in result.get('reviews', []):
        print(f"  • {review['filename']}: Score {review['quality_score']}")

def test_statistics():
    """Test 6: Get Statistics"""
    print("\n" + "="*60)
    print("TEST 6: Get Statistics")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/statistics")
    
    print(f"Status: {response.status_code}")
    stats = response.json().get('statistics', {})
    
    print(f"\n📊 Statistics Dashboard:")
    print(f"  Total Reviews: {stats.get('total_reviews')}")
    print(f"  Average Quality: {stats.get('average_quality')}/100")
    print(f"  Total Errors: {stats.get('total_errors')}")
    print(f"  Total Warnings: {stats.get('total_warnings')}")
    print(f"  Recent Activity (7d): {stats.get('recent_activity_7d')}")
    
    print(f"\n📁 File Types:")
    for ft in stats.get('file_type_distribution', []):
        print(f"  • .{ft['type']}: {ft['count']} files")

def test_search():
    """Test 7: Search Reviews"""
    print("\n" + "="*60)
    print("TEST 7: Search Reviews")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/reviews/search?q=test")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Search Query: '{result.get('query')}'")
    print(f"Results Found: {result.get('count')}")
    
    for item in result.get('results', []):
        print(f"  • {item['filename']} (ID: {item['id']})")

def test_export():
    """Test 8: Export Review"""
    print("\n" + "="*60)
    print("TEST 8: Export Review as JSON")
    print("="*60)
    
    # Get first review ID
    response = requests.get(f"{API_URL}/api/reviews?limit=1")
    reviews = response.json().get('reviews', [])
    
    if not reviews:
        print("⚠️ No reviews to export. Upload a file first.")
        return
    
    review_id = reviews[0]['id']
    
    response = requests.get(f"{API_URL}/api/review/{review_id}/export")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save to file
        with open(f'review_export_{review_id}.json', 'wb') as f:
            f.write(response.content)
        print(f"✅ Exported to: review_export_{review_id}.json")
    else:
        print(f"❌ Export failed")

def test_compare():
    """Test 9: Compare Two Reviews"""
    print("\n" + "="*60)
    print("TEST 9: Compare Two Reviews")
    print("="*60)
    
    # Get first two reviews
    response = requests.get(f"{API_URL}/api/reviews?limit=2")
    reviews = response.json().get('reviews', [])
    
    if len(reviews) < 2:
        print("⚠️ Need at least 2 reviews for comparison. Upload more files.")
        return
    
    data = {
        "review_id_1": reviews[0]['id'],
        "review_id_2": reviews[1]['id']
    }
    
    response = requests.post(
        f"{API_URL}/api/reviews/compare",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json().get('comparison', {})
    
    print(f"\n📊 Comparison Results:")
    print(f"\nReview 1: {result['review_1']['filename']}")
    print(f"  Quality: {result['review_1']['quality_score']}")
    print(f"  Errors: {result['review_1']['errors']}")
    
    print(f"\nReview 2: {result['review_2']['filename']}")
    print(f"  Quality: {result['review_2']['quality_score']}")
    print(f"  Errors: {result['review_2']['errors']}")
    
    print(f"\n📈 Differences:")
    print(f"  Quality Change: {result['differences']['quality_score_diff']:+d}")
    print(f"  Error Change: {result['differences']['errors_diff']:+d}")
    print(f"  Improvement: {'✅ Yes' if result['improvement'] else '❌ No'}")

def test_trends():
    """Test 10: Get Quality Trends"""
    print("\n" + "="*60)
    print("TEST 10: Get Quality Trends")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/trends?days=7")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Period: {result.get('period')}")
    
    print(f"\n📈 Trend Data:")
    for trend in result.get('trends', []):
        print(f"  {trend['date']}: {trend['reviews_count']} reviews, "
              f"avg quality {trend['average_quality']}")

def test_delete_review():
    """Test 11: Delete Single Review"""
    print("\n" + "="*60)
    print("TEST 11: Delete Single Review")
    print("="*60)
    
    # Get last review
    response = requests.get(f"{API_URL}/api/reviews?limit=1")
    reviews = response.json().get('reviews', [])
    
    if not reviews:
        print("⚠️ No reviews to delete.")
        return
    
    review_id = reviews[0]['id']
    
    response = requests.delete(f"{API_URL}/api/review/{review_id}")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Message: {result.get('message')}")

def test_clear_all():
    """Test 12: Clear All Reviews (USE WITH CAUTION!)"""
    print("\n" + "="*60)
    print("TEST 12: Clear All Reviews")
    print("="*60)
    print("⚠️  WARNING: This will delete ALL reviews!")
    
    confirm = input("Type 'YES' to continue: ")
    
    if confirm == 'YES':
        response = requests.delete(f"{API_URL}/api/reviews")
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Message: {result.get('message')}")
    else:
        print("Cancelled.")

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🚀"*30)
    print("RUNNING ALL API TESTS")
    print("🚀"*30)
    
    tests = [
        test_health_check,
        test_single_upload,
        test_batch_upload,
        test_get_reviews,
        test_get_reviews_filtered,
        test_statistics,
        test_search,
        test_export,
        test_compare,
        test_trends,
        # test_delete_review,  # Uncomment to test delete
        # test_clear_all,      # Uncomment to test clear all
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        input("\nPress Enter to continue to next test...")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║   Code Review Assistant API v2.0 - Test Suite           ║
╚══════════════════════════════════════════════════════════╝

Choose an option:
  1. Run all tests
  2. Test specific feature
  0. Exit

Note: Make sure the API is running at http://localhost:5001
    """)
    
    choice = input("Enter choice: ")
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        print("\nAvailable Tests:")
        print("  1. Health Check")
        print("  2. Single Upload")
        print("  3. Batch Upload")
        print("  4. Get Reviews")
        print("  5. Get Reviews (Filtered)")
        print("  6. Statistics")
        print("  7. Search")
        print("  8. Export")
        print("  9. Compare")
        print(" 10. Trends")
        print(" 11. Delete Review")
        print(" 12. Clear All")
        
        test_num = input("\nEnter test number: ")
        
        tests_map = {
            "1": test_health_check,
            "2": test_single_upload,
            "3": test_batch_upload,
            "4": test_get_reviews,
            "5": test_get_reviews_filtered,
            "6": test_statistics,
            "7": test_search,
            "8": test_export,
            "9": test_compare,
            "10": test_trends,
            "11": test_delete_review,
            "12": test_clear_all,
        }
        
        if test_num in tests_map:
            tests_map[test_num]()
        else:
            print("Invalid test number")
    else:
        print("Goodbye!")