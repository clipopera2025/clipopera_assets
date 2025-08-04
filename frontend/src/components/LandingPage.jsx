import React, { useContext, useState } from 'react';
import { motion } from 'framer-motion';
import { AppDispatchContext, AppStateContext } from '../contexts';
import ProductCard from './ProductCard';
import CountdownTimer from './CountdownTimer';

export default function LandingPage() {
  const appDispatch = useContext(AppDispatchContext);
  const appState = useContext(AppStateContext);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNavigate = (page, params = {}) => {
    appDispatch({ type: 'SET_PAGE', payload: page });
    const query = new URLSearchParams(params).toString();
    window.history.pushState(null, '', `/${page}${query ? '?' + query : ''}`);
  };

  const filteredProducts = appState.products.filter(product =>
    product.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <motion.div
      key="landing-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-12"
    >
      <section className="relative bg-black text-white rounded-xl overflow-hidden shadow-xl">
        <div className="absolute inset-0 bg-[url('https://placehold.co/1200x600/111/444?text=Hero+Image')] bg-cover bg-center opacity-40"></div>
        <div className="relative p-8 md:p-16 text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 tracking-tight">
            Elevate Your Look.
          </h1>
          <p className="text-lg md:text-xl font-light max-w-2xl mx-auto mb-8">
            Discover the highest quality human hair bundles, wigs, and closures.
          </p>
          <button
            onClick={() => handleNavigate('product', { id: appState.products[0]?.id })}
            className="px-8 py-4 bg-red-500 text-white font-bold rounded-lg shadow-lg hover:bg-red-600 transition-colors transform hover:scale-105"
          >
            Shop Now
          </button>
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold mb-6 text-center">Products</h2>
        <div className="max-w-md mx-auto mb-6">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search products"
            className="w-full px-4 py-2 border rounded-md"
          />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold mb-6 text-center">Why Choose Us?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-bold mb-2">Virgin Human Hair</h3>
            <p className="text-gray-600">
              Ethically sourced, unprocessed hair for maximum quality and longevity.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-bold mb-2">Seamless Blending</h3>
            <p className="text-gray-600">
              Our products are designed to blend perfectly with your natural hair.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-bold mb-2">Fast Shipping</h3>
            <p className="text-gray-600">
              Get your order quickly with our expedited shipping options.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-red-500 text-white rounded-xl shadow-xl p-8 text-center">
        <h3 className="text-2xl md:text-4xl font-extrabold mb-2">
          Flash Sale Ends In...
        </h3>
        <CountdownTimer />
        <button
          onClick={() => handleNavigate('product', { id: appState.products[3]?.id })}
          className="mt-6 px-8 py-3 bg-white text-red-500 font-bold rounded-lg shadow-lg hover:bg-gray-100 transition-colors transform hover:scale-105"
        >
          Shop Sale Items
        </button>
      </section>
    </motion.div>
  );
}
