"""
Create rich embeddings with hybrid strategy
Combines all related data (Products + ProductSpecifications + ProductData) into single embedding
"""
import os
# Fix OpenMP library conflict (safe workaround for multiple OpenMP runtimes)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.embeddings import EmbeddingService

def decode_unicode(text):
    """Decode Unicode escape sequences (e.g., \\u00E6 to æ, \\u00f8 to ø)"""
    if not text:
        return text
    try:
        # Try to decode unicode escapes
        if isinstance(text, str) and '\\u' in text:
            return text.encode('utf-8').decode('unicode-escape')
    except:
        pass
    return text

def get_field_name(spec_code, meta_fields):
    """Map specification code to readable field name using SimpleMetaFields"""
    for field in meta_fields:
        if spec_code.startswith(field.get('MetaClass', '')):
            return field.get('FieldName', spec_code)
    return spec_code

def parse_description(desc_raw):
    """Parse multilingual description JSON and return clean text"""
    if not desc_raw:
        return ''
    
    try:
        # Parse JSON format: {"da":"...","en":"...","sv":"..."}
        if isinstance(desc_raw, str) and desc_raw.strip().startswith('{'):
            desc_dict = json.loads(desc_raw)
            # Priority: English > Danish > Swedish > Norwegian > any available
            for lang in ['en', 'da', 'sv', 'no', 'fi', 'de']:
                if lang in desc_dict and desc_dict[lang]:
                    return decode_unicode(desc_dict[lang])
            # Fallback to first available value
            if desc_dict:
                return decode_unicode(list(desc_dict.values())[0])
        # Not JSON, return as-is
        return decode_unicode(desc_raw)
    except:
        return decode_unicode(desc_raw)

def create_rich_embedding_text(product, meta_fields):
    """
    Create rich text representation combining all related data
    Preserves relationships: Products + ProductSpecifications + ProductData
    
    CRITICAL: This text is what gets embedded and searched, so it must contain
    ALL searchable content in plain, readable format (not JSON)
    """
    # Parse main description (most important for search)
    description = parse_description(product.get('ItemDescriptionSerialized', ''))
    
    # Parse secondary description
    description2 = parse_description(product.get('ItemDescription2Serialized', ''))
    
    # Parse tertiary description
    description3 = product.get('ItemDescription3', '') or ''
    description3 = decode_unicode(description3)
    
    # Parse specifications (including nested JSON)
    specs_text = ""
    specifications = product.get('specifications', [])
    if specifications:
        for spec in specifications:
            spec_type = spec.get('Type', '')
            spec_data = spec.get('Data', '')
            
            # Try to parse nested JSON in Data field
            if spec_data and isinstance(spec_data, str) and spec_data.strip().startswith('{'):
                try:
                    nested_data = json.loads(spec_data)
                    # Extract ALL fields from nested JSON (dimensions, materials, etc.)
                    for key, val in nested_data.items():
                        if isinstance(val, dict):
                            # Handle nested structure like {"value": "125", "type": "number"}
                            value = val.get('value', '')
                            if value and str(value).strip():
                                clean_key = key.replace('_', ' ').replace('(mm)', 'mm').replace('(inch)', 'inch').strip()
                                specs_text += f"{clean_key}: {value}\n"
                        elif val and str(val).strip():
                            # Direct value
                            clean_key = key.replace('_', ' ').strip()
                            specs_text += f"{clean_key}: {val}\n"
                except:
                    # If parsing fails, use raw data
                    field_name = get_field_name(spec_type, meta_fields)
                    if spec_data and str(spec_data).strip():
                        specs_text += f"{field_name}: {spec_data}\n"
            elif spec_data and str(spec_data).strip():
                # Not JSON, use as-is
                field_name = get_field_name(spec_type, meta_fields)
                specs_text += f"{field_name}: {spec_data}\n"
    
    # Include product data
    product_data_text = ""
    product_data = product.get('product_data', [])
    if product_data:
        for data in product_data:
            data_type = data.get('Type', '')
            data_content = decode_unicode(data.get('Content', ''))
            product_data_text += f"{data_type}: {data_content}\n"
    
    # Parse FilterMetaDataSerialized for additional specs (dimensions, materials, etc.)
    filter_metadata_text = ""
    filter_meta = product.get('FilterMetaDataSerialized', '')
    if filter_meta and filter_meta != '{}':
        try:
            filter_dict = json.loads(filter_meta) if isinstance(filter_meta, str) else filter_meta
            for key, value in filter_dict.items():
                if not value or value == {}:  # Skip empty values
                    continue
                
                field_name = get_field_name(key, meta_fields)
                
                if isinstance(value, dict):
                    # Handle multilingual dict like {"da":"...","en":"..."}
                    # Priority: English > Danish > first available
                    clean_value = None
                    for lang in ['en', 'da', 'sv', 'no']:
                        if lang in value and value[lang]:
                            clean_value = decode_unicode(str(value[lang]))
                            break
                    if not clean_value and value:
                        clean_value = decode_unicode(str(list(value.values())[0]))
                    
                    if clean_value and clean_value.strip():
                        filter_metadata_text += f"{field_name}: {clean_value}\n"
                elif str(value).strip():
                    filter_metadata_text += f"{field_name}: {decode_unicode(str(value))}\n"
        except Exception as e:
            pass  # Skip if parsing fails
    
    # CRITICAL: Parse CuttingFilterMetaDataSerialized - contains material/application info (wood, metal, etc.)
    cutting_filter_text = ""
    cutting_filter_meta = product.get('CuttingFilterMetaDataSerialized', '')
    if cutting_filter_meta and cutting_filter_meta != '{}':
        try:
            cutting_dict = json.loads(cutting_filter_meta) if isinstance(cutting_filter_meta, str) else cutting_filter_meta
            for key, value in cutting_dict.items():
                if not value or value == {}:  # Skip empty values
                    continue
                
                field_name = get_field_name(key, meta_fields)
                
                if isinstance(value, dict):
                    # Handle multilingual dict like {"da":"...","en":"..."}
                    # Priority: English > Danish > first available
                    clean_value = None
                    for lang in ['en', 'da', 'sv', 'no']:
                        if lang in value and value[lang]:
                            clean_value = decode_unicode(str(value[lang]))
                            break
                    if not clean_value and value:
                        clean_value = decode_unicode(str(list(value.values())[0]))
                    
                    if clean_value and clean_value.strip():
                        cutting_filter_text += f"{field_name}: {clean_value}\n"
                elif str(value).strip():
                    cutting_filter_text += f"{field_name}: {decode_unicode(str(value))}\n"
        except Exception as e:
            pass  # Skip if parsing fails
    
    # Parse MachineFilterMetaDataSerialized - contains machine/compatibility info
    machine_filter_text = ""
    machine_filter_meta = product.get('MachineFilterMetaDataSerialized', '')
    if machine_filter_meta and machine_filter_meta != '{}':
        try:
            machine_dict = json.loads(machine_filter_meta) if isinstance(machine_filter_meta, str) else machine_filter_meta
            for key, value in machine_dict.items():
                if not value or value == {}:  # Skip empty values
                    continue
                
                field_name = get_field_name(key, meta_fields)
                
                if isinstance(value, dict):
                    # Handle multilingual dict like {"da":"...","en":"..."}
                    # Priority: English > Danish > first available
                    clean_value = None
                    for lang in ['en', 'da', 'sv', 'no']:
                        if lang in value and value[lang]:
                            clean_value = decode_unicode(str(value[lang]))
                            break
                    if not clean_value and value:
                        clean_value = decode_unicode(str(list(value.values())[0]))
                    
                    if clean_value and clean_value.strip():
                        machine_filter_text += f"{field_name}: {clean_value}\n"
                elif str(value).strip():
                    machine_filter_text += f"{field_name}: {decode_unicode(str(value))}\n"
        except Exception as e:
            pass  # Skip if parsing fails
    
    # Get item number and category
    item_number = product.get('SanitizedItemNumber', '')
    category = product.get('MetaClass', '')
    ean = product.get('Ean', '') or ''
    
    # Process ALL remaining product fields that haven't been explicitly handled
    # This ensures no data is missed - we only exclude fields that are:
    # 1. Already processed above
    # 2. Internal/system fields (IsDeleted, Timestamp, etc.)
    # 3. Empty/irrelevant (Parent='purchases' already filtered)
    other_fields_text = ""
    excluded_fields = {
        # Already processed fields
        'ItemDescriptionSerialized', 'ItemDescription2Serialized', 'ItemDescription3',
        'FilterMetaDataSerialized', 'CuttingFilterMetaDataSerialized', 'MachineFilterMetaDataSerialized',
        'specifications', 'product_data',
        # Already included as identifiers
        'SanitizedItemNumber', 'MetaClass', 'Ean',
        # System/internal fields (not searchable)
        'MarketsSerialized', 'Parent', 'IsDeleted', 'Id', 'Timestamp', 'UpdateIndex',
        'IsMaster', 'ServiceType', 'Status', 'Priority', 'TunNumber', 'Company',
        'DrawingExists', 'HasAssociations', 'HasListPrice'
    }
    
    for key, value in product.items():
        # Skip fields we've already processed or that are empty/irrelevant
        if key in excluded_fields or not value:
            continue
        
        # Skip None, empty strings, empty dicts, empty lists
        if value is None:
            continue
        if isinstance(value, str) and (not value.strip() or value == '{}' or value == '[]'):
            continue
        if isinstance(value, (dict, list)) and len(value) == 0:
            continue
        
        # Process different value types
        try:
            if isinstance(value, str):
                # Try to parse JSON strings
                if value.strip().startswith('{'):
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict) and parsed:
                            # Parse multilingual dicts
                            clean_val = None
                            for lang in ['en', 'da', 'sv', 'no']:
                                if lang in parsed and parsed[lang]:
                                    clean_val = decode_unicode(str(parsed[lang]))
                                    break
                            if not clean_val and parsed:
                                clean_val = decode_unicode(str(list(parsed.values())[0]))
                            if clean_val and clean_val.strip():
                                other_fields_text += f"{key}: {clean_val}\n"
                    except:
                        # Not JSON, use as-is
                        decoded = decode_unicode(value)
                        if decoded and decoded.strip():
                            other_fields_text += f"{key}: {decoded}\n"
                else:
                    decoded = decode_unicode(value)
                    if decoded and decoded.strip():
                        other_fields_text += f"{key}: {decoded}\n"
            elif isinstance(value, (int, float)):
                other_fields_text += f"{key}: {value}\n"
            elif isinstance(value, bool):
                if value:  # Only include True values
                    other_fields_text += f"{key}: Yes\n"
        except Exception:
            pass  # Skip fields that can't be processed
    
    # Create rich, searchable text for embedding
    # Format: Most important info first (description), then details
    # CRITICAL: Material/application info must be prominent for proper filtering
    parts = []
    
    # Main description (MOST IMPORTANT - appears first)
    if description:
        parts.append(f"Product: {description}")
    
    # Secondary descriptions
    if description2:
        parts.append(f"Details: {description2}")
    if description3:
        parts.append(f"Additional: {description3}")
    
    # CRITICAL: Cutting Filter Metadata - Material/Application (wood, metal, etc.)
    # This MUST be prominent so LLM can verify material compatibility
    if cutting_filter_text.strip():
        parts.append(f"\nMATERIAL/APPLICATION (CRITICAL FOR COMPATIBILITY):")
        parts.append(cutting_filter_text.strip())
    
    # Item identifiers
    parts.append(f"\nItem Number: {item_number}")
    if category:
        parts.append(f"Category: {category}")
    if ean:
        parts.append(f"EAN: {ean}")
    
    # Specifications (dimensions, materials, etc.)
    if specs_text.strip():
        parts.append(f"\nSpecifications:")
        parts.append(specs_text.strip())
    
    # Filter metadata (additional searchable attributes)
    if filter_metadata_text.strip():
        parts.append(f"\nAttributes:")
        parts.append(filter_metadata_text.strip())
    
    # Machine filter metadata (machine compatibility)
    if machine_filter_text.strip():
        parts.append(f"\nMachine Compatibility:")
        parts.append(machine_filter_text.strip())
    
    # Product data
    if product_data_text.strip():
        parts.append(f"\nAdditional Information:")
        parts.append(product_data_text.strip())
    
    # ALL OTHER FIELDS - ensures no data is missed
    if other_fields_text.strip():
        parts.append(f"\nOther Product Details:")
        parts.append(other_fields_text.strip())
    
    rich_text = '\n'.join(parts)
    return rich_text.strip()

def setup_embeddings():
    """Main function to create embeddings from exported data"""
    print("="*60)
    print("Creating Embeddings with Hybrid Strategy")
    print("="*60)
    
    # Load exported data
    data_file = Path(__file__).parent.parent / 'data' / 'products_joined.json'
    
    if not data_file.exists():
        print(f"\n❌ Error: Data file not found at {data_file}")
        print("\nPlease run 'python scripts/export_data.py' first to export data from SSMS")
        return
    
    print(f"\nLoading data from {data_file}...")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    meta_fields = data.get('meta_fields', [])
    
    print(f"Loaded {len(products)} products")
    print(f"Loaded {len(meta_fields)} metadata fields")
    
    # Initialize embedding service
    print("\nInitializing Sentence Transformer...")
    embedding_service = EmbeddingService()
    collection = embedding_service.get_or_create_collection("products")
    
    print(f"Current collection count: {embedding_service.get_collection_count()}")
    
    # Process products in batches
    batch_size = 1000  
    total_processed = 0
    
    print(f"\nProcessing products in batches of {batch_size}...")
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        
        # Prepare data for batch
        ids = []
        texts = []
        metadatas = []
        
        for product in batch:
            item_number = product.get('SanitizedItemNumber', '')
            if not item_number:
                continue
            
            # Create rich text embedding
            rich_text = create_rich_embedding_text(product, meta_fields)
            
            # Parse description for metadata (use same parser for consistency)
            description_clean = parse_description(product.get('ItemDescriptionSerialized', ''))
            
            # Prepare metadata
            metadata = {
                'item_number': item_number,
                'description': description_clean,  # Store clean English/Danish description
                'category': product.get('MetaClass', ''),
                'specifications': json.dumps(product.get('specifications', [])),
                'product_data': json.dumps(product.get('product_data', [])),
                'filter_metadata': product.get('FilterMetaDataSerialized', ''),
                'market': product.get('MarketsSerialized', ''),
                'parent': product.get('Parent', ''),
                'ean': product.get('Ean', '') or ''
            }
            
            ids.append(item_number)
            texts.append(rich_text)
            metadatas.append(metadata)
        
        if not ids:
            continue
        
        # Generate embeddings for batch
        print(f"  Generating embeddings for batch {i//batch_size + 1}...")
        embeddings = embedding_service.encode_batch(texts)
        
        # Add to ChromaDB
        print(f"  Adding to ChromaDB...")
        embedding_service.add_to_collection(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )
        
        total_processed += len(ids)
        print(f"  Progress: {total_processed}/{len(products)} products")
    
    final_count = embedding_service.get_collection_count()
    
    print("\n" + "="*60)
    print("✅ Embeddings Created Successfully!")
    print("="*60)
    print(f"Total products processed: {total_processed}")
    print(f"ChromaDB collection count: {final_count}")
    print(f"\nVector database ready at: {embedding_service.chroma_persist_dir}")
    print("\n✅ You can now start the API server!")
    print("   Run: uvicorn main:app --reload")

if __name__ == "__main__":
    try:
        setup_embeddings()
    except Exception as e:
        print(f"\n❌ Error creating embeddings: {e}")
        import traceback
        traceback.print_exc()

