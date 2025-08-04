import React, { useContext, useState } from 'react';
import { motion } from 'framer-motion';
import { CartDispatchContext, AppDispatchContext } from '../contexts';

export default function ProductPage({ product }) {
  const cartDispatch = useContext(CartDispatchContext);
  const appDispatch = useContext(AppDispatchContext);
  const [selectedVariant, setSelectedVariant] = useState(product.variants[0]);
  const [quantity, setQuantity] = useState(1);

  const handleAddToCart = () => {
    if (quantity > 0 && selectedVariant.stock >= quantity) {
      cartDispatch({
        type: 'ADD_ITEM',
        payload: {
          id: `${product.id}-${selectedVariant.length}-${selectedVariant.texture}`,
          title: `${product.title} (${selectedVariant.length} - ${selectedVariant.texture})`,
          price: product.price,
          quantity,
          image: product.images?.[0] || 'https://placehold.co/600x400',
        },
      });
      appDispatch({ type: 'SET_PAGE', payload: 'cart' });
      window.history.pushState(null, '', '/cart');
    }
  };

  return (
    <motion.div
      key="product-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="grid md:grid-cols-2 gap-8 bg-white p-6 rounded-xl shadow-lg"
    >
      <div className="relative">
        <img src={product.images?.[0] || 'https://placehold.co/600x400'} alt={product.title} className="w-full h-auto rounded-lg shadow-md" />
        <span className="absolute top-4 left-4 bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full">
          Only {selectedVariant.stock} left!
        </span>
      </div>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">{product.title}</h1>
        <p className="text-2xl font-semibold text-gray-700">${product.price}</p>
        <p className="text-gray-600">{product.description}</p>

        <div>
          <h3 className="text-lg font-medium mb-2">Length & Texture</h3>
          <div className="flex flex-wrap gap-2">
            {product.variants.map((variant, index) => (
              <button
                key={index}
                onClick={() => setSelectedVariant(variant)}
                className={`px-4 py-2 rounded-md transition-colors ${
                  selectedVariant.length === variant.length
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
                disabled={variant.stock === 0}
              >
                {variant.length} - {variant.texture}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <label htmlFor="quantity" className="text-lg font-medium">Quantity:</label>
          <input
            id="quantity"
            type="number"
            min="1"
            max={selectedVariant.stock}
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            className="w-20 px-3 py-2 border border-gray-300 rounded-md text-center"
          />
        </div>
        <button
          onClick={handleAddToCart}
          className="w-full py-3 bg-red-500 text-white font-bold rounded-lg shadow-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={selectedVariant.stock === 0 || quantity > selectedVariant.stock}
        >
          Add to Cart
        </button>
      </div>
    </motion.div>
  );
}
