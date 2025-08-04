import React, { useContext, useState } from 'react';
import { motion } from 'framer-motion';
import { AppStateContext, AppDispatchContext } from '../contexts';
import AdminProductCard from './AdminProductCard';

export default function AdminDashboard() {
  const appState = useContext(AppStateContext);
  const appDispatch = useContext(AppDispatchContext);
  const [products, setProducts] = useState(appState.products);

  const handleUpdateProduct = (id, newProductData) => {
    const updatedProducts = products.map(p => p.id === id ? { ...p, ...newProductData } : p);
    setProducts(updatedProducts);
    appDispatch({ type: 'SET_PRODUCTS', payload: updatedProducts });
  };

  return (
    <motion.div
      key="admin-dashboard-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <button
          onClick={() => appDispatch({ type: 'LOGOUT' })}
          className="px-4 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors"
        >
          Logout
        </button>
      </div>
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-2xl font-bold mb-4">Product Inventory</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <AdminProductCard key={product.id} product={product} onUpdate={handleUpdateProduct} />
          ))}
        </div>
      </div>
    </motion.div>
  );
}
