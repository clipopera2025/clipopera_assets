import React, { useContext } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeftIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { CartContext, AppDispatchContext } from '../contexts';
import CartItem from './CartItem';

export default function CartPage() {
  const cartState = useContext(CartContext);
  const appDispatch = useContext(AppDispatchContext);

  const total = cartState.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleNavigate = (page) => {
    appDispatch({ type: 'SET_PAGE', payload: page });
    window.history.pushState(null, '', `/${page}`);
  };

  return (
    <motion.div
      key="cart-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Your Cart</h1>
        <button
          onClick={() => handleNavigate('landing')}
          className="flex items-center space-x-1 text-gray-500 hover:text-gray-900 transition-colors"
        >
          <ChevronLeftIcon className="h-4 w-4" />
          <span>Continue Shopping</span>
        </button>
      </div>

      {cartState.length === 0 ? (
        <div className="text-center p-12 bg-white rounded-xl shadow-lg">
          <ShoppingCartIcon className="h-20 w-20 text-gray-300 mx-auto mb-4" />
          <p className="text-xl font-medium text-gray-600">Your cart is empty.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-4">
            {cartState.map(item => (
              <CartItem key={item.id} item={item} />
            ))}
          </div>
          <div className="md:col-span-1 bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold mb-4">Order Summary</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>${total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold text-xl border-t pt-4 mt-4">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
            </div>
            <button
              onClick={() => handleNavigate('checkout')}
              className="mt-6 w-full py-3 bg-gray-900 text-white font-bold rounded-lg hover:bg-gray-800 transition-colors"
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
