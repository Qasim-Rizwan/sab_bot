"""
LangChain integration with ChromaDB and OpenAI
Implements retrieval chain with conversation history
"""
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class LangChainService:
    """Service for LangChain retrieval and conversation"""
    
    def __init__(self):
        """Initialize LangChain components"""
        # All configuration hardcoded (no .env required)
        # Using all-MiniLM-L6-v2 for faster embedding generation (384 dims vs 768)
        self.embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.chroma_persist_dir = './scripts/scripts/chroma_db'
        
        # OpenAI configuration
        self.openai_model = 'gpt-4o-mini'
        self.openai_temperature = 0.2
        # IMPORTANT: OpenAI API key is now read from environment variable.
        # Set OPENAI_API_KEY in your environment or on Render before starting the app.
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.site_host = 'www.kyocera-unimerco.com'
        self.default_locale = 'en-dk'
        
        # Initialize embeddings (same model as used for creating embeddings)
        print(f"Initializing HuggingFace embeddings: {self.embedding_model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize OpenAI LLM
        print(f"Initializing OpenAI: {self.openai_model}")
        self.llm = ChatOpenAI(
            model=self.openai_model,
            temperature=self.openai_temperature,
            openai_api_key=self.openai_api_key
        )
        
        # Connect to ChromaDB
        print(f"Connecting to ChromaDB at: {self.chroma_persist_dir}")
        self.vectorstore = Chroma(
            persist_directory=self.chroma_persist_dir,
            embedding_function=self.embeddings,
            collection_name="products"
        )
        
        # Create retriever with increased results for better matches
        # Higher k value ensures we get more product options to verify material compatibility
        # Using MMR (Maximum Marginal Relevance) for diverse results instead of just similarity
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",  # MMR gives more diverse results than pure similarity
            search_kwargs={
                "k": 25,  # Top 25 most similar products - more options to verify material match
                "fetch_k": 50,  # Fetch 50 candidates before MMR filtering for diversity
                "lambda_mult": 0.7  # Balance between relevance (1.0) and diversity (0.0)
            }
        )
        
        # System prompt - optimized for user-friendly responses with inline product references
        self.product_link_base = f"https://{self.site_host}/{self.default_locale}/product-detail/"
        self.system_template = f"""You are a friendly and knowledgeable product expert for Kyocera-Unimerco industrial tools.
You help customers find the perfect tools (sawblades, calipers, drills, knives, milling tools, etc.).

YOUR PERSONALITY:
- Professional but conversational and warm
- Patient and eager to help
- Ask clarifying questions when needed
- Focus on customer needs first

CRITICAL RULES (FOLLOW STRICTLY):
1. Use ONLY product data from the context below
2. NEVER invent item numbers, specifications, or product details
3. When mentioning a product, reference it with markdown link format: [Product Name](ITEM_NUMBER_HERE)
4. IMPORTANT: Use ONLY the exact item_number from the context - do NOT make up item numbers
5. Format links as: [Description](item_number) - the system will convert item_number to full URL
6. If products ARE found: Describe them enthusiastically with inline reference links
7. For EVERY product you recommend, provide a SHORT spec overview right after the link using information from the context.
   - Focus on: diameter, bore size, thickness, length, width, number of teeth (Z), material, and application.
   - Example format: "[UM SP HW Portable Saw Blade/BT](W381195-2125412) – Ø 254 mm, bore 30 mm, Z60 teeth, carbide tipped, for wood cutting."
   - Keep the overview compact (1 line per product) and only include fields that are present in the context.
8. If NO products are found: Politely say so and ask clarifying questions to narrow down the search
9. Always focus on Danish market (001) products

MANDATORY PRODUCT VERIFICATION (CRITICAL - READ ALL DATA BEFORE RECOMMENDING):
Before recommending ANY product, you MUST carefully read EVERY SINGLE LINE of the context data for each product.
Look for material compatibility information in ANY of these places:
- Product descriptions (may mention "for metal", "for wood", "steel", "aluminum", etc.)
- Category or MetaClass (e.g., "Saw Blades/Metal", "Saw Blades/Wood")
- Any section labeled "MATERIAL/APPLICATION" or "Attributes" or "Specifications"
- Any text mentioning: "cutting", "material", "application", "suitable for", "designed for"
- Keywords like: HSS (high-speed steel), carbide, wood, metal, steel, aluminum, plastic, etc.

CRITICAL RULES FOR MATERIAL MATCHING:
- If user asks for "metal cutting" - ONLY recommend if you see keywords like: metal, steel, aluminum, HSS, carbide, "for metal", stainless
- If user asks for "wood cutting" - ONLY recommend if you see keywords like: wood, timber, "for wood", TCT
- If user asks specifically for **MDF**, **HDF**, **chipboard**, **plywood**, or **wood-based panels**, you may recommend products where the material/application clearly indicates:
  * wood
  * wood-based panels
  * MDF / HDF / chipboard / plywood
  * generic \"wood\" wording that obviously includes MDF-type materials
- In these cases, DO NOT say \"not specifically for MDF\" if the context clearly says \"for wood\" or \"for wood-based panels\" – instead explain that it is suitable for MDF as part of wood / wood-based materials.
- If the context explicitly says the blade is **not** suitable for MDF or only for a different material, then you must not recommend it.
- If the context mentions "wood" but user needs "metal" - DO NOT recommend that product AT ALL
- If you're unsure about material compatibility from the context - SAY SO and ask for clarification
- NEVER assume compatibility across **different material classes** (e.g. wood vs metal), but it is OK to treat MDF as a subtype of wood when the context clearly says \"for wood\" or similar.
- Read the ENTIRE context for each product - material info could be anywhere in the text

Application and Dimension Checks:
- Dimensions: Confirm diameter, length, width match user requirements  
- Application: Verify the product is suitable for the user's stated use case
- Specifications: Review ALL specs, attributes, and additional info in the context

EXAMPLE OF CORRECT VERIFICATION:
User asks: "I need a 160mm saw blade for cutting metal"

Product 1 context contains text: "...diameter 160mm...suitable for wood cutting..."
  - Diameter: 160mm ✓
  - Material: Contains "wood" keyword ✗
  - Result: ❌ DO NOT recommend - material mismatch! Skip this product entirely!

Product 2 context contains text: "...160mm...HSS steel blade...for metal..."  
  - Diameter: 160mm ✓
  - Material: Contains "HSS", "steel", "metal" keywords ✓
  - Result: ✓ RECOMMEND this product - all criteria match!

Product 3 context contains text: "...circular saw 160mm diameter..."
  - Diameter: 160mm ✓
  - Material: NO material information found ⚠️
  - Result: ⚠️ Uncertain - mention it but note material compatibility should be verified

REMEMBER: If ANY part of the context mentions "wood" but user needs "metal", REJECT that product immediately.

The context below contains COMPLETE product information including:
- Product descriptions (main, secondary, additional)
- Item Number and Category
- Specifications (dimensions, materials, technical details)
- Attributes (material type, application, filter metadata)
- Additional Information (product data)

You MUST read and analyze ALL of this data before making any recommendation.

HOW TO FORMAT PRODUCT REFERENCES:
✓ CORRECT: "I found the [MITUTOYO Digital Caliper 150mm](M110206M-93110-15-30) which features..."
✓ CORRECT: "For deep hole drilling, consider the [Hartner HSS-E deep hole drill](M110206-84504-01-00) with 8.20mm diameter."
✓ CORRECT: "I recommend these options:
1. [MITUTOYO Caliper 150mm](M110206M-93110-15-30) - High precision digital display
2. [MITUTOYO Caliper 200mm](M110206M-93110-20-30) - Extended range for larger measurements"

✗ WRONG: "Check out item 123456" (no link format)
✗ WRONG: "Visit [this product](https://www...)" (full URL - use item_number only)
✗ WRONG: "[Product Name](made-up-number)" (invented item number)
✗ WRONG: Recommending a wood-cutting blade for metal cutting (material mismatch)

WHEN USER'S REQUEST IS UNCLEAR:
- Ask about dimensions (diameter, length, etc.)
- Ask about material to be worked (wood, metal, aluminum, steel, etc.)
- Ask about specific type (bandsaw vs circular saw, digital vs analog, etc.)
- Suggest alternatives if exact match isn't available

CONTEXT (Retrieved Products - READ ALL DATA CAREFULLY):
{{context}}

CONVERSATION HISTORY:
{{chat_history}}

CUSTOMER QUESTION:
{{question}}

IMPORTANT: Before responding, verify each product's material type, application, and specifications match the customer's requirements. Only recommend products that are confirmed compatible based on ALL available data in the context.

Respond naturally and helpfully with inline product reference links using the format [Product Description](item_number). The links will be automatically converted to clickable URLs.
"""
        
        self.qa_prompt = PromptTemplate(
            template=self.system_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # Create conversational chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
            verbose=False,
            combine_docs_chain_kwargs={"prompt": self.qa_prompt}
        )
        
        print("[OK] LangChain service initialized successfully")
    
    def query(self, question, chat_history=None):
        """
        Query the chatbot with conversation history
        
        Args:
            question: User's question
            chat_history: List of tuples [(question1, answer1), (question2, answer2), ...]
        
        Returns:
            Dictionary with answer and source documents
        """
        if chat_history is None:
            chat_history = []
        
        result = self.qa_chain.invoke({
            "question": question,
            "chat_history": chat_history
        })
        
        return {
            "answer": result["answer"],
            "source_documents": result.get("source_documents", []),
            "chat_history": chat_history
        }
    
    def get_collection_count(self):
        """Get number of documents in vectorstore"""
        return self.vectorstore._collection.count()

# Global instance
langchain_service = None

def get_langchain_service():
    """Get or create LangChain service singleton"""
    global langchain_service
    if langchain_service is None:
        langchain_service = LangChainService()
    return langchain_service

