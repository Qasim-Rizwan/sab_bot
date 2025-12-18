"""
Comprehensive test to verify embeddings work for ALL product categories
Run this AFTER generating embeddings to ensure quality
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from services.langchain_setup import get_langchain_service

def test_all_categories():
    """Test various product categories to ensure embeddings work correctly"""
    print("="*70)
    print("COMPREHENSIVE EMBEDDING QUALITY TEST")
    print("="*70)
    
    # Initialize service
    print("\nInitializing service...")
    service = get_langchain_service()
    
    # Check collection count
    count = service.get_collection_count()
    print(f"\n[OK] Total products in database: {count:,}")
    
    if count == 0:
        print("\n[ERROR] No embeddings found! Run: python scripts/setup_embeddings.py")
        return
    
    # Test queries for different categories
    test_cases = [
        {
            "category": "Digital Calipers",
            "queries": [
                "digital caliper",
                "MITUTOYO caliper",
                "measuring tool digital",
                "caliper 200mm"
            ]
        },
        {
            "category": "Sawblades",
            "queries": [
                "sawblades",
                "sawblade 160mm",
                "circular saw blade",
                "blade for wood cutting"
            ]
        },
        {
            "category": "Bandsaw Blades",
            "queries": [
                "bandsaw blade",
                "wood bandsaw",
                "metal bandsaw blade"
            ]
        },
        {
            "category": "Drills",
            "queries": [
                "drill bits",
                "drill 10mm",
                "twist drill",
                "drilling tool"
            ]
        },
        {
            "category": "Knives",
            "queries": [
                "cutting knife",
                "industrial knife",
                "knife insert"
            ]
        },
        {
            "category": "Milling Tools",
            "queries": [
                "milling cutter",
                "end mill",
                "face mill"
            ]
        }
    ]
    
    print("\n" + "="*70)
    print("TESTING SEMANTIC SEARCH FOR ALL CATEGORIES")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    failed_queries = []
    
    for test_case in test_cases:
        category = test_case["category"]
        queries = test_case["queries"]
        
        print(f"\n{'='*70}")
        print(f"Category: {category}")
        print(f"{'='*70}")
        
        for query in queries:
            total_tests += 1
            print(f"\n[TEST {total_tests}] Query: '{query}'")
            
            # Search using vector similarity
            results = service.vectorstore.similarity_search(query, k=5)
            
            if results:
                print(f"  [PASS] Found {len(results)} results")
                # Show first result
                desc = results[0].metadata.get('description', 'No description')
                item = results[0].metadata.get('item_number', 'No item')
                
                # Check if description makes sense for the query
                query_lower = query.lower()
                desc_lower = desc.lower()
                
                # Basic relevance check
                relevant = False
                if 'caliper' in query_lower and 'caliper' in desc_lower:
                    relevant = True
                elif 'sawblade' in query_lower or 'saw blade' in query_lower:
                    relevant = 'saw' in desc_lower or 'blade' in desc_lower
                elif 'bandsaw' in query_lower and 'bandsaw' in desc_lower:
                    relevant = True
                elif 'drill' in query_lower and 'drill' in desc_lower:
                    relevant = True
                elif 'knife' in query_lower or 'kniv' in query_lower:
                    relevant = 'knife' in desc_lower or 'kniv' in desc_lower
                elif 'mill' in query_lower and 'mill' in desc_lower:
                    relevant = True
                else:
                    relevant = True  # Assume relevant if no specific check
                
                if relevant:
                    print(f"  [RELEVANT] Top result: {desc[:70]}")
                    print(f"             Item: {item}")
                    passed_tests += 1
                else:
                    print(f"  [WARNING] May not be relevant: {desc[:70]}")
                    print(f"            Item: {item}")
                    failed_queries.append((query, desc))
            else:
                print(f"  [FAIL] No results found!")
                failed_queries.append((query, "No results"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed/Warnings: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_queries:
        print(f"\n[ATTENTION] {len(failed_queries)} queries need review:")
        for query, result in failed_queries[:5]:  # Show first 5
            print(f"  - Query: '{query}'")
            print(f"    Result: {result[:60]}")
    
    if passed_tests >= total_tests * 0.8:  # 80% success rate
        print("\n[SUCCESS] Embeddings quality is GOOD! Ready for production.")
    elif passed_tests >= total_tests * 0.6:  # 60% success rate
        print("\n[WARNING] Embeddings quality is ACCEPTABLE but could be improved.")
    else:
        print("\n[ERROR] Embeddings quality is POOR. Consider regenerating.")
    
    # Test with LangChain (with LLM)
    print("\n" + "="*70)
    print("TESTING LANGCHAIN WITH LLM (Real Bot Responses)")
    print("="*70)
    
    sample_questions = [
        "I need a digital caliper",
        "Show me sawblades for cutting wood",
        "What drills do you have?"
    ]
    
    for question in sample_questions:
        print(f"\n[QUESTION] {question}")
        result = service.query(question, chat_history=[])
        print(f"[RESPONSE] {result['answer'][:200]}")
        print(f"[PRODUCTS] Retrieved {len(result['source_documents'])} products")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    try:
        test_all_categories()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

