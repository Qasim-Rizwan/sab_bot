"""
Chat API endpoint with LangChain and relationship preservation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Optional, Dict
import json
import sys
from pathlib import Path
import re
import httpx

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.langchain_setup import get_langchain_service

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: List[Tuple[str, str]] = []


class Product(BaseModel):
    """Product model"""
    id: str
    description: str
    category: str
    specifications: List[dict]
    product_data: List[dict]
    link: str
    ean: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    products: List[Product]
    source_count: int


def decode_unicode(text):
    """Decode Unicode escape sequences"""
    if not text:
        return text
    try:
        if isinstance(text, str) and "\\u" in text:
            return text.encode("utf-8").decode("unicode-escape")
    except Exception:
        # Best-effort decode; fall back to original text on any error
        pass
    return text


async def check_item_urls(
    site_host: str, default_locale: str, item_numbers: List[str]
) -> Dict[str, bool]:
    """
    For each item_number, build the product URL and check if it exists on the live site.

    Returns a dict: { item_number: True/False } where False means the URL is broken (4xx/5xx or network error).
    """
    results: Dict[str, bool] = {}
    if not item_numbers:
        return results

    base = f"https://{site_host}/{default_locale}/product-detail"

    timeout = httpx.Timeout(5.0, connect=5.0)  # Increased timeout
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for item in item_numbers:
            url = f"{base}/{item}"
            try:
                # Try HEAD first (cheaper); fall back to GET if needed
                resp = await client.head(url)
                if resp.status_code >= 400:
                    resp = await client.get(url)
                is_valid = resp.status_code < 400
                results[item] = is_valid
                print(f"  URL check: {item} -> {is_valid} (status: {resp.status_code})")
            except Exception as e:
                # Any error -> treat as not available
                results[item] = False
                print(f"  URL check: {item} -> False (error: {str(e)[:50]})")

    return results


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with conversation history and relationship preservation.

    - Uses LangChain to generate an answer and retrieve product documents.
    - Converts item numbers in markdown links to full product URLs.
    - **Validates** each product URL against the live site and only keeps links that exist.

    Returns:
        ChatResponse with answer and related products
    """
    try:
        # Get LangChain service
        service = get_langchain_service()

        # Get site configuration
        site_host = service.site_host
        default_locale = service.default_locale

        # Query with conversation history
        result = service.query(
            question=request.message,
            chat_history=request.conversation_history,
        )

        # Convert item numbers in markdown links to full URLs
        # Pattern: [text](item_number) -> [text](https://site/product-detail/item_number)
        response_text = result["answer"]

        pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        matches = list(pattern.finditer(response_text))

        # Collect all unique item_numbers that are not already URLs
        raw_item_numbers = {
            m.group(2) for m in matches if not m.group(2).startswith("http")
        }

        # Also collect item numbers from source documents for validation
        source_item_numbers = set()
        for doc in result["source_documents"]:
            item_num = doc.metadata.get("item_number", "")
            if item_num:
                source_item_numbers.add(item_num)
        
        # Combine item numbers from markdown links and source documents
        all_item_numbers = raw_item_numbers | source_item_numbers
        
        # Check which of these item_numbers actually exist on the live site
        print(f"\nFound {len(all_item_numbers)} item numbers to validate: {list(all_item_numbers)[:5]}")
        item_availability: Dict[str, bool] = await check_item_urls(
            site_host, default_locale, list(all_item_numbers)
        )
        print(f"Validation results: {sum(item_availability.values())}/{len(item_availability)} URLs are valid")

        def replace_item_link(match: re.Match) -> str:
            link_text = match.group(1)
            target = match.group(2)

            # If it's already a full URL, leave it as-is
            if target.startswith("http"):
                return match.group(0)

            # Only keep links for item_numbers that are confirmed to exist
            is_available = item_availability.get(target, False)
            if not is_available:
                # Return plain text without any link if the product URL is broken
                return link_text

            full_url = f"https://{site_host}/{default_locale}/product-detail/{target}"
            return f"[{link_text}]({full_url})"

        # Replace [text](item_number) with [text](full_url) only for valid products
        print(f"\nBefore URL replacement:\n{response_text[:500]}")
        response_text = pattern.sub(replace_item_link, response_text)
        print(f"\nAfter URL replacement:\n{response_text[:500]}")

        # Extract products from source documents - ONLY include products with valid, clickable URLs
        products: List[Product] = []
        seen_items = set()

        for doc in result["source_documents"]:
            metadata = doc.metadata

            # Get SanitizedItemNumber from metadata (stored as 'item_number' during embedding creation)
            # Rules.txt: "Products: Column SanitizedItemNumber = unique code for each item.
            # And on the website you can type: https://www.kyocera-unimerco.com/en-dk/product-detail/SanitizedItemNumber"
            item_number = metadata.get("item_number", "")
            if not item_number or item_number in seen_items:
                continue

            # CRITICAL: Only include products with valid, clickable URLs
            is_available = item_availability.get(item_number, False)
            if not is_available:
                # Skip products with broken URLs - don't send them to frontend
                continue

            seen_items.add(item_number)

            # Parse stored specifications (from ProductSpecifications table)
            try:
                specs = json.loads(metadata.get("specifications", "[]"))
            except Exception:
                specs = []

            # Parse stored product data (from ProductData table)
            try:
                product_data = json.loads(metadata.get("product_data", "[]"))
            except Exception:
                product_data = []

            # Decode description
            description = decode_unicode(metadata.get("description", ""))

            # Create product object - only for products with valid URLs
            # Link format per Rules.txt: https://www.kyocera-unimerco.com/en-dk/product-detail/SanitizedItemNumber
            product = Product(
                id=item_number,  # This is SanitizedItemNumber
                description=description,
                category=metadata.get("category", ""),
                specifications=specs,
                product_data=product_data,
                link=f"https://{site_host}/{default_locale}/product-detail/{item_number}",  # Using SanitizedItemNumber
                ean=metadata.get("ean", ""),
            )

            products.append(product)

        return ChatResponse(
            response=response_text,  # Use converted response with filtered, valid URLs only
            products=products,
            source_count=len(result["source_documents"]),
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/count")
async def get_product_count():
    """Get number of products in vector database"""
    try:
        service = get_langchain_service()
        count = service.get_collection_count()
        return {"count": count, "status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting product count: {str(e)}"
        )

