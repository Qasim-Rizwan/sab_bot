# Clickable Links Implementation

## Overview
This document explains how product links are made clickable in the chatbot responses.

## How It Works

### 1. Backend (Python - FastAPI)

#### URL Validation (`backend/api/chat.py`)
- The LLM generates responses with markdown links: `[Product Name](item_number)`
- Backend validates each item_number against the live Kyocera Unimerco website
- Only valid URLs are converted to full URLs: `[Product Name](https://www.kyocera-unimerco.com/en-dk/product-detail/item_number)`
- Invalid/broken URLs are converted to plain text (no link)

```python
async def check_item_urls(site_host: str, default_locale: str, item_numbers: List[str]) -> Dict[str, bool]:
    """
    Validates each item_number by making HTTP HEAD/GET requests to the live site.
    Returns: { item_number: True/False }
    """
```

#### Link Conversion
```python
def replace_item_link(match: re.Match) -> str:
    """
    Converts [text](item_number) to [text](full_url) only if URL is valid.
    Invalid URLs become plain text.
    """
```

### 2. Frontend (React/TypeScript/Next.js)

#### Markdown Parsing (`frontend/components/MessageList.tsx`)
The `renderMessageContent` function:
1. Uses regex to find markdown links: `/\[([^\]]+)\]\(([^)]+)\)/g`
2. Extracts link text and URL
3. Validates URL format (ensures it starts with http:// or https://)
4. Renders as React `<a>` element with:
   - `target="_blank"` - opens in new tab
   - `rel="noopener noreferrer"` - security
   - Blue color and underline styling
   - High z-index (999) to ensure clickability

```tsx
<a
  href={url}
  target="_blank"
  rel="noopener noreferrer"
  className="text-blue-600 hover:text-blue-800 hover:underline ..."
  style={{ 
    pointerEvents: 'auto', 
    zIndex: 999, 
    position: 'relative',
    touchAction: 'auto',
    userSelect: 'auto'
  }}
>
  {linkText}
</a>
```

#### CSS Styling (`frontend/styles/globals.css`)
Multiple CSS rules ensure links are always clickable:

```css
/* Target all product links */
a[href^="https://www.kyocera-unimerco.com"],
[class*="message"] a,
.message-content a,
div[class*="rounded-2xl"] a {
  pointer-events: auto !important;
  cursor: pointer !important;
  position: relative !important;
  z-index: 999 !important;
  text-decoration: underline !important;
  color: #2563eb !important;  /* Blue */
}

a[href^="https://www.kyocera-unimerco.com"]:hover {
  color: #1e40af !important;  /* Darker blue */
  font-weight: 600 !important;
}
```

## Testing

### 1. Test in Browser
1. Start backend: `cd backend && python -m uvicorn main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Open `http://localhost:3000`
4. Ask: "can you give me a saw blade that can cut aluminum?"
5. Click on blue underlined product links in the response

### 2. Test with HTML File
Open `TEST_CLICKABLE_LINKS.html` in your browser to test the link rendering independently.

## Debugging

If links are not clickable, check:

1. **Browser Console** - Look for:
   - `Found markdown link: ...` - confirms regex is finding links
   - `Link clicked: ...` - confirms click event fires

2. **Backend Logs** - Look for:
   - `Found X item numbers to validate: [...]`
   - `URL check: item_number -> True/False (status: XXX)`
   - `Validation results: X/Y URLs are valid`

3. **Network Tab** - Verify:
   - API response contains markdown links with full URLs
   - URLs start with `https://www.kyocera-unimerco.com/`

4. **Inspect Element** - Check:
   - Links are `<a>` tags with proper `href` attribute
   - Links have `z-index: 999` and `pointer-events: auto`
   - No parent element blocks pointer events

## Common Issues

### Issue: Links appear as plain text
**Cause**: Backend URL validation failed (product doesn't exist on live site)
**Solution**: Check backend logs for validation results

### Issue: Links are visible but not clickable
**Cause**: CSS `pointer-events: none` on parent element
**Solution**: Verify CSS rules in browser inspector, ensure `pointer-events: auto !important` on links

### Issue: Links don't render at all
**Cause**: Markdown regex not matching
**Solution**: Check that backend is sending proper markdown format `[text](url)`

## URL Format

Per `Rules.txt`, the correct URL format is:
```
https://www.kyocera-unimerco.com/{locale}/product-detail/{SanitizedItemNumber}
```

Example:
```
https://www.kyocera-unimerco.com/en-dk/product-detail/W381196-2835014
```

## Configuration

Site configuration is in `backend/services/langchain_setup.py`:
```python
self.site_host = 'www.kyocera-unimerco.com'
self.default_locale = 'en-dk'
```

## Files Modified

1. **Backend**
   - `backend/api/chat.py` - URL validation and link conversion
   - `backend/services/langchain_setup.py` - Site configuration

2. **Frontend**
   - `frontend/components/MessageList.tsx` - Markdown parsing and link rendering
   - `frontend/styles/globals.css` - Link styling and clickability
   - `frontend/components/ChatBox.tsx` - No modifications needed

## Summary

The clickable link system works in three stages:
1. **Backend validates** - Checks if product URLs exist on live site
2. **Backend converts** - Transforms valid item numbers to full URLs in markdown
3. **Frontend renders** - Parses markdown and creates clickable `<a>` elements with proper styling

This ensures that only valid, clickable product links are shown to users, preventing broken links and improving user experience.

