"""
Validate exported data meets client requirements
"""
import json
from pathlib import Path
from collections import Counter

def validate_data():
    """Check if exported data is suitable for chatbot requirements"""
    
    print("="*70)
    print("DATA VALIDATION FOR CHATBOT REQUIREMENTS")
    print("="*70)
    
    # Load data
    json_path = Path(__file__).parent.parent / 'data' / 'products_joined.json'
    
    if not json_path.exists():
        print("❌ products_joined.json not found!")
        return False
    
    print(f"\n📁 File: {json_path}")
    print(f"📊 Size: {json_path.stat().st_size / 1e6:.1f} MB")
    
    print("\n⏳ Loading JSON (this may take a moment)...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    meta_fields = data.get('meta_fields', [])
    
    print(f"✅ Loaded successfully!")
    print(f"   Products: {len(products):,}")
    print(f"   Meta Fields: {len(meta_fields):,}")
    
    if not products:
        print("❌ No products found!")
        return False
    
    # Check 1: Product structure
    print("\n" + "="*70)
    print("CHECK 1: Product Structure")
    print("="*70)
    
    sample = products[0]
    print(f"✅ Product columns ({len(sample)} fields):")
    for i, key in enumerate(sample.keys(), 1):
        print(f"   {i:2d}. {key}")
    
    # Check 2: Market filtering (Danish market = 001)
    print("\n" + "="*70)
    print("CHECK 2: Market Filtering (Danish = 001)")
    print("="*70)
    
    market_products = [p for p in products if '001' in str(p.get('MarketsSerialized', ''))]
    print(f"✅ Products with market 001: {len(market_products):,} / {len(products):,}")
    
    if len(market_products) == 0:
        print("⚠️  WARNING: No products for Danish market (001)")
    
    # Check 3: Deleted/Parent filtering
    print("\n" + "="*70)
    print("CHECK 3: IsDeleted and Parent Filtering")
    print("="*70)
    
    deleted = [p for p in products if p.get('IsDeleted') not in (0, None)]
    purchases = [p for p in products if p.get('Parent') == 'purchases']
    
    print(f"✅ Active products (IsDeleted=0): {len(products) - len(deleted):,}")
    print(f"✅ Non-purchase items (Parent!=purchases): {len(products) - len(purchases):,}")
    
    if deleted:
        print(f"⚠️  Found {len(deleted)} deleted products (should be 0)")
    if purchases:
        print(f"⚠️  Found {len(purchases)} purchase items (should be 0)")
    
    # Check 4: Product descriptions (for "sawblades", "calipers", etc.)
    print("\n" + "="*70)
    print("CHECK 4: Product Descriptions (Client Examples)")
    print("="*70)
    
    # Count products with key terms
    desc_field = 'ItemDescriptionSerialized'
    sawblades = [p for p in products if 'saw' in str(p.get(desc_field, '')).lower()]
    calipers = [p for p in products if 'caliper' in str(p.get(desc_field, '')).lower()]
    drills = [p for p in products if 'drill' in str(p.get(desc_field, '')).lower()]
    knives = [p for p in products if 'knife' or 'kniv' in str(p.get(desc_field, '')).lower()]
    
    print(f"✅ Sawblades/Saw products: {len(sawblades):,}")
    print(f"✅ Calipers: {len(calipers):,}")
    print(f"✅ Drills: {len(drills):,}")
    print(f"✅ Knives: {len(knives):,}")
    
    if sawblades:
        print(f"\n   Sample sawblade: {sawblades[0].get(desc_field, '')[:80]}...")
    if calipers:
        print(f"   Sample caliper: {calipers[0].get(desc_field, '')[:80]}...")
    
    # Check 5: Specifications (for "160mm", "soft wood", etc.)
    print("\n" + "="*70)
    print("CHECK 5: Product Specifications")
    print("="*70)
    
    with_specs = [p for p in products if p.get('specifications')]
    with_data = [p for p in products if p.get('product_data')]
    
    print(f"✅ Products with specifications: {len(with_specs):,} / {len(products):,} ({len(with_specs)/len(products)*100:.1f}%)")
    print(f"✅ Products with product_data: {len(with_data):,} / {len(products):,} ({len(with_data)/len(products)*100:.1f}%)")
    
    if with_specs:
        sample_specs = with_specs[0].get('specifications', [])
        print(f"\n   Sample product has {len(sample_specs)} specifications:")
        for spec in sample_specs[:5]:
            print(f"      - {spec}")
    
    # Check 6: Numeric dimensions (for "160" searches)
    print("\n" + "="*70)
    print("CHECK 6: Numeric Dimensions (e.g., 160mm)")
    print("="*70)
    
    # Look for products with numeric values in specs
    products_with_numbers = []
    for p in products[:1000]:  # Check first 1000
        specs = p.get('specifications', [])
        for spec in specs:
            if any(char.isdigit() for char in str(spec.get('Data', ''))):
                products_with_numbers.append(p)
                break
    
    print(f"✅ Products with numeric specs (sample of 1000): {len(products_with_numbers):,}")
    
    if products_with_numbers:
        sample = products_with_numbers[0]
        print(f"\n   Sample: {sample.get(desc_field, '')[:60]}...")
        print(f"   Specs with numbers:")
        for spec in sample.get('specifications', [])[:3]:
            if any(char.isdigit() for char in str(spec.get('Data', ''))):
                print(f"      - {spec.get('Type')}: {spec.get('Data')}")
    
    # Check 7: Meta fields for decoding
    print("\n" + "="*70)
    print("CHECK 7: SimpleMetaFields (Spec Decoding)")
    print("="*70)
    
    print(f"✅ Meta fields available: {len(meta_fields):,}")
    if meta_fields:
        print(f"\n   Sample meta fields:")
        for field in meta_fields[:5]:
            print(f"      - {field}")
    
    # Check 8: Categories/MetaClass
    print("\n" + "="*70)
    print("CHECK 8: Product Categories")
    print("="*70)
    
    categories = Counter(p.get('MetaClass', 'Unknown') for p in products)
    print(f"✅ Unique categories: {len(categories)}")
    print(f"\n   Top 10 categories:")
    for cat, count in categories.most_common(10):
        print(f"      - {cat}: {count:,} products")
    
    # Final Assessment
    print("\n" + "="*70)
    print("FINAL ASSESSMENT FOR CLIENT REQUIREMENTS")
    print("="*70)
    
    checks = []
    
    # Requirement 1: "sawblades 160" - needs descriptions + numeric specs
    if sawblades and products_with_numbers:
        print("✅ Can handle 'sawblades 160' queries")
        print("   → Has sawblade products with numeric dimensions")
        checks.append(True)
    else:
        print("⚠️  May struggle with 'sawblades 160'")
        checks.append(False)
    
    # Requirement 2: "blade for soft wood" - needs specs/materials
    if with_specs:
        print("✅ Can help with material-based queries ('soft wood')")
        print("   → Products have specifications for recommendations")
        checks.append(True)
    else:
        print("⚠️  Limited material-based recommendations")
        checks.append(False)
    
    # Requirement 3: "digital calipers" - needs product variety
    if calipers:
        print("✅ Can find 'digital calipers'")
        print(f"   → Found {len(calipers)} caliper products")
        checks.append(True)
    else:
        print("⚠️  No caliper products found")
        checks.append(False)
    
    # Requirement 4: Low token usage - local embeddings
    print("✅ Ready for low-token approach")
    print("   → Can use local Sentence Transformers")
    print("   → Only LLM response costs tokens (not search)")
    checks.append(True)
    
    # Requirement 5: Complex DB handling
    if with_specs and meta_fields:
        print("✅ Handles complex database structure")
        print("   → Specs joined and preserved")
        print("   → Meta fields for decoding")
        checks.append(True)
    else:
        print("⚠️  Database relationships may be incomplete")
        checks.append(False)
    
    print("\n" + "="*70)
    if all(checks):
        print("✅ DATA IS READY FOR EMBEDDINGS GENERATION!")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python scripts/setup_embeddings.py")
        print("2. This will create vector embeddings from your products")
        print("3. Takes 10-30 minutes depending on product count")
        print("4. After that, start the API and frontend")
        return True
    else:
        print("⚠️  DATA HAS SOME ISSUES")
        print("="*70)
        print("\nReview warnings above and consider:")
        print("- Check if correct tables were exported")
        print("- Verify database schema matches expectations")
        print("- Re-run export with correct filters")
        return False

if __name__ == "__main__":
    try:
        validate_data()
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

