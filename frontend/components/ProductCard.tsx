import React from 'react'

interface Specification {
  Type: string
  Data: string
}

interface ProductData {
  Type: string
  Content: string
  Source?: string
  ItemNumber?: string
}

interface Product {
  id: string
  description: string
  category: string
  specifications: Specification[]
  product_data: ProductData[]
  link: string
  ean?: string
}

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)
  
  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden border border-gray-200 card-hover">
      {/* Product header */}
      <div className="bg-gray-50 p-6 border-b border-gray-200">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
              {product.description}
            </h3>
            <div className="flex gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1 bg-red-600 text-white text-xs px-3 py-1.5 rounded-full font-semibold shadow-sm">
                {product.category}
              </span>
              {product.ean && (
                <span className="inline-flex items-center gap-1 bg-gray-200 text-gray-700 text-xs px-3 py-1.5 rounded-full font-medium border border-gray-300">
                  EAN: {product.ean}
                </span>
              )}
              <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-xs px-3 py-1.5 rounded-full font-medium border border-green-300">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                In Stock
              </span>
            </div>
          </div>
          <div className="flex-shrink-0 w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center shadow-sm border border-red-200">
            <span className="text-3xl">🔧</span>
          </div>
        </div>
      </div>

      {/* Product body */}
      <div className="p-6 space-y-5">
        {/* Display specifications from ProductSpecifications table */}
        {product.specifications && product.specifications.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <span className="w-1 h-4 bg-gradient-to-b from-red-500 to-red-600 rounded-full"></span>
              Technical Specifications
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {product.specifications.slice(0, isExpanded ? product.specifications.length : 6).map((spec, i) => (
                <div key={i} className="bg-gray-50 rounded-xl p-3 border border-gray-200 hover:border-red-300 transition-colors">
                  <span className="font-semibold text-gray-600 text-xs block mb-1">{spec.Type}</span>
                  <span className="text-gray-900 text-sm font-medium">{spec.Data}</span>
                </div>
              ))}
            </div>
            {product.specifications.length > 6 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-3 text-sm text-red-600 hover:text-red-700 font-semibold flex items-center gap-1 transition-colors"
              >
                {isExpanded ? '▲ Show Less' : `▼ Show ${product.specifications.length - 6} More Specifications`}
              </button>
            )}
          </div>
        )}

        {/* Display additional data from ProductData table */}
        {product.product_data && product.product_data.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <span className="w-1 h-4 bg-gradient-to-b from-red-500 to-red-600 rounded-full"></span>
              Additional Information
            </h4>
            <div className="space-y-2">
              {product.product_data.slice(0, 3).map((data, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-red-500 mt-0.5">●</span>
                  <div>
                    <span className="font-semibold text-gray-600">{data.Type}:</span>{' '}
                    <span className="text-gray-800">{data.Content}</span>
                  </div>
                </div>
              ))}
            </div>
            {product.product_data.length > 3 && (
              <p className="text-xs text-gray-500 mt-2 ml-4">
                +{product.product_data.length - 3} more details available
              </p>
            )}
          </div>
        )}
      </div>

      {/* Product footer */}
      <div className="p-6 pt-0">
        <div className="flex items-center justify-between gap-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
          <div>
            <p className="text-xs text-gray-500 mb-1">Product ID</p>
            <p className="text-sm font-bold text-gray-800 font-mono">{product.id}</p>
          </div>
          <a
            href={product.link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg"
          >
            <span>View Details</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  )
}

