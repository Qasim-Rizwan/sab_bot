"""
One-time data export from SSMS with JOINs to preserve table relationships
Run this script once to export all product data from the database
"""
import pyodbc
import json
import os
from pathlib import Path

def decode_unicode(text):
    """Decode Unicode escape sequences (e.g., \\u00E6 to æ)"""
    if not text:
        return text
    try:
        # Handle Unicode escapes
        return text.encode('latin1').decode('unicode-escape')
    except:
        return text

def get_db_connection():
    """Create database connection (configured inline, no .env required)"""
    
    # ⚠️ Choose your database: 'dbcopy' or 'dbcopy1'
    database = 'dbcopy1'  # Change to 'dbcopy1' if that's the one you want
    
    # Using Windows Authentication (works since --list-databases succeeded)
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"Server=DESKTOP-U33UF27\\SQLEXPRESS;"
        f"Database={database};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)

def list_available_databases():
    """List all available databases on the server"""
    server = 'localhost\\SQLEXPRESS'
    try:
        # Connect to master database to list all databases
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE=master;'
            f'Trusted_Connection=yes;'
            f'TrustServerCertificate=yes;'
        )
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4 ORDER BY name")
        print("\n📋 Available databases on your server:")
        for row in cursor.fetchall():
            print(f"   - {row.name}")
        cursor.close()
        conn.close()
        print("\n💡 Update the 'database' variable in get_db_connection() to match your database name\n")
    except Exception as e:
        print(f"❌ Could not list databases: {e}")
        print("Make sure SQL Server is running and you have access\n")

def get_table_columns(table_name):
    """Get all columns for a specific table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' 
            ORDER BY ORDINAL_POSITION
        """)
        columns = []
        print(f"\n📋 Columns in {table_name} table:")
        for row in cursor.fetchall():
            columns.append(row.COLUMN_NAME)
            print(f"   - {row.COLUMN_NAME} ({row.DATA_TYPE}, nullable={row.IS_NULLABLE})")
        cursor.close()
        conn.close()
        return columns
    except Exception as e:
        print(f"❌ Could not get columns for {table_name}: {e}")
        return []

def export_products():
    """Export products with all related data (JOINs) - auto-detects columns"""
    print("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("Step 1: Discovering database schema...")
    print("="*60)
    
    # Get actual columns from Products table
    products_columns = get_table_columns('Products')
    if not products_columns:
        print("❌ Could not get Products table columns")
        return
    
    # Get columns from related tables
    specs_columns = get_table_columns('ProductSpecifications')
    data_columns = get_table_columns('ProductData')
    meta_columns = get_table_columns('SimpleMetaFields')
    
    print("\n" + "="*60)
    print("Step 2: Exporting products with relationships...")
    print("="*60)
    
    # Build dynamic query using actual columns
    # Select all columns from Products
    columns_str = ', '.join([f'p.[{col}]' for col in products_columns])
    
    query = f"""
    SELECT {columns_str}
    FROM Products p
    WHERE p.IsDeleted = 0
    AND p.Parent != 'purchases'
    AND p.MarketsSerialized LIKE '%001%'
    """
    
    print(f"\nExecuting query with {len(products_columns)} columns...")
    print(f"Sample columns: {', '.join(products_columns[:5])}...")
    
    cursor.execute(query)
    products = []
    
    # Determine which column to use as ID (prefer SanitizedItemNumber)
    id_column = 'SanitizedItemNumber' if 'SanitizedItemNumber' in products_columns else products_columns[0]
    print(f"Using '{id_column}' as product ID\n")
    
    for row in cursor.fetchall():
        # Build product dict dynamically from actual columns
        product = {}
        for i, col_name in enumerate(products_columns):
            try:
                product[col_name] = getattr(row, col_name)
            except:
                product[col_name] = row[i] if i < len(row) else None
        
        # Get ProductSpecifications for this product
        if specs_columns:
            spec_cursor = conn.cursor()
            # Use first column of specs table as join key
            join_col = specs_columns[0] if specs_columns else 'ItemNumber'
            spec_cols_str = ', '.join([f'[{col}]' for col in specs_columns])
            spec_query = f"""
            SELECT {spec_cols_str}
            FROM ProductSpecifications
            WHERE [{join_col}] = ?
            """
            try:
                spec_cursor.execute(spec_query, product.get(id_column))
                specifications = []
                for spec_row in spec_cursor.fetchall():
                    spec_dict = {}
                    for i, col_name in enumerate(specs_columns):
                        try:
                            spec_dict[col_name] = getattr(spec_row, col_name)
                        except:
                            spec_dict[col_name] = spec_row[i] if i < len(spec_row) else None
                    specifications.append(spec_dict)
                spec_cursor.close()
                product['specifications'] = specifications
            except Exception as e:
                print(f"⚠️  Could not get specs for product {product.get(id_column)}: {e}")
                product['specifications'] = []
        
        # Get ProductData for this product
        if data_columns:
            data_cursor = conn.cursor()
            data_join_col = data_columns[0] if data_columns else 'ItemNumber'
            data_cols_str = ', '.join([f'[{col}]' for col in data_columns])
            data_query = f"""
            SELECT {data_cols_str}
            FROM ProductData
            WHERE [{data_join_col}] = ?
            """
            try:
                data_cursor.execute(data_query, product.get(id_column))
                product_data = []
                for data_row in data_cursor.fetchall():
                    data_dict = {}
                    for i, col_name in enumerate(data_columns):
                        try:
                            data_dict[col_name] = getattr(data_row, col_name)
                        except:
                            data_dict[col_name] = data_row[i] if i < len(data_row) else None
                    product_data.append(data_dict)
                data_cursor.close()
                product['product_data'] = product_data
            except Exception as e:
                print(f"⚠️  Could not get data for product {product.get(id_column)}: {e}")
                product['product_data'] = []
        
        products.append(product)
    
    cursor.close()
    
    print(f"Exported {len(products)} products with relationships")
    
    # Export SimpleMetaFields for decoding spec codes
    print("\n" + "="*60)
    print("Step 3: Exporting SimpleMetaFields...")
    print("="*60)
    
    meta_fields = []
    if meta_columns:
        cursor = conn.cursor()
        meta_cols_str = ', '.join([f'[{col}]' for col in meta_columns])
        try:
            cursor.execute(f"SELECT {meta_cols_str} FROM SimpleMetaFields")
            for row in cursor.fetchall():
                meta_dict = {}
                for i, col_name in enumerate(meta_columns):
                    try:
                        meta_dict[col_name] = getattr(row, col_name)
                    except:
                        meta_dict[col_name] = row[i] if i < len(row) else None
                meta_fields.append(meta_dict)
            cursor.close()
        except Exception as e:
            print(f"⚠️  Could not export SimpleMetaFields: {e}")
    
    
    print(f"Exported {len(meta_fields)} metadata fields")
    
    conn.close()
    
    # Save to JSON
    output_dir = Path(__file__).parent.parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'products_joined.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'products': products,
            'meta_fields': meta_fields
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Data exported successfully to {output_file}")
    print(f"   Products: {len(products)}")
    print(f"   Meta Fields: {len(meta_fields)}")
    print("\nYou can now disconnect from SSMS!")
    
    return output_file

if __name__ == "__main__":
    import sys
    
    # If --list-databases flag is passed, show available databases
    if len(sys.argv) > 1 and sys.argv[1] == '--list-databases':
        list_available_databases()
        sys.exit(0)
    
    try:
        export_products()
    except Exception as e:
        print(f"\n❌ Error exporting data: {e}")
        print("\nMake sure:")
        print("1. SQL Server is running")
        print("2. Database is imported in SSMS")
        print("3. ODBC Driver 17 for SQL Server is installed")
        print("4. Database name in script matches your SSMS database")
        print("\n💡 Run 'python export_data.py --list-databases' to see available databases")

