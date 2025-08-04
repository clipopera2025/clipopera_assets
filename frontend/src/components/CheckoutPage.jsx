import React, { useContext, useState } from 'react';
import { motion } from 'framer-motion';
import { CartContext, AppDispatchContext } from '../contexts';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  process.env.REACT_APP_API_BASE_URL ||
  'http://localhost:5000/api';

export default function CheckoutPage() {
  const cartState = useContext(CartContext);
  const appDispatch = useContext(AppDispatchContext);
  const [isProcessing, setIsProcessing] = useState(false);
  const total = cartState.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleCheckout = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      const response = await fetch(`${API_BASE_URL}/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: cartState }),
      });

      if (!response.ok) {
        throw new Error('Checkout failed on the server.');
      }

      await response.json();
      setIsProcessing(false);
      appDispatch({ type: 'SET_PAGE', payload: 'thank-you' });
      window.history.pushState(null, '', '/thank-you');
    } catch (e) {
      setIsProcessing(false);
      appDispatch({ type: 'SET_ERROR', payload: `Checkout failed: ${e.message}. Is the backend running?` });
    }
  };

  return (
    <motion.div
      key="checkout-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white p-8 rounded-xl shadow-lg max-w-2xl mx-auto"
    >
      <h1 className="text-3xl font-bold mb-6">Checkout</h1>
      <form onSubmit={handleCheckout} className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-2">Contact Information</h2>
          <input type="email" placeholder="Email Address" required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Shipping Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" placeholder="First Name" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="Last Name" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="Address" required className="md:col-span-2 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="City" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="State/Province" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="ZIP/Postal Code" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
            <input type="text" placeholder="Country" required className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900" />
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Payment (Simulated)</h2>
          <p className="text-gray-600 mb-4">
            The backend will simulate a successful payment.
          </p>
        </div>
        <div className="border-t pt-4 flex justify-between items-center text-xl font-bold">
          <span>Total</span>
          <span>${total.toFixed(2)}</span>
        </div>
        <button
          type="submit"
          className="w-full py-3 bg-red-500 text-white font-bold rounded-lg shadow-lg hover:bg-red-600 transition-colors disabled:opacity-50"
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : `Pay $${total.toFixed(2)}`}
        </button>
      </form>
    </motion.div>
  );
}
