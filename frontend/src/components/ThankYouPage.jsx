import React, { useContext, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CartDispatchContext, AppDispatchContext } from '../contexts';

export default function ThankYouPage() {
  const cartDispatch = useContext(CartDispatchContext);
  const appDispatch = useContext(AppDispatchContext);

  useEffect(() => {
    cartDispatch({ type: 'CLEAR_CART' });
  }, [cartDispatch]);

  return (
    <motion.div
      key="thank-you-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="text-center p-12 bg-white rounded-xl shadow-lg max-w-xl mx-auto"
    >
      <h1 className="text-4xl font-bold text-gray-900 mb-4">Thank You!</h1>
      <p className="text-lg text-gray-600 mb-8">
        Your order has been placed successfully. You will receive a confirmation email shortly.
      </p>
      <div className="bg-gray-100 p-6 rounded-lg mb-8">
        <h2 className="text-2xl font-bold mb-2">Share the love!</h2>
        <p className="text-gray-600 mb-4">
          Share your purchase on social media for a chance to win a discount on your next order.
        </p>
        <div className="flex justify-center space-x-4">
          <button className="p-3 bg-gray-900 text-white rounded-full hover:bg-gray-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.834 7 2.477v6.758z"/>
            </svg>
          </button>
          <button className="p-3 bg-gray-900 text-white rounded-full hover:bg-gray-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.799-1.574 2.164-2.722-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.585 0-6.495 2.91-6.495 6.495 0 .509.055 1.001.162 1.477-5.39-2.7-10.169-5.698-13.382-10.686-.554.953-.878 2.062-.878 3.242 0 2.254 1.147 4.244 2.894 5.419-.902-.027-1.751-.277-2.492-.689v.08c0 3.155 2.245 5.786 5.215 6.398-.546.149-1.121.231-1.708.231-.419 0-.82-.041-1.21-.115.823 2.587 3.203 4.475 6.03 4.529-2.227 1.748-5.044 2.793-8.093 2.793-.525 0-1.042-.03-1.553-.09-.009 0-.019 0-.028 0 2.871 1.848 6.29 2.934 9.967 2.934 11.954 0 18.441-9.917 18.441-18.528 0-.281-.008-.562-.021-.842.946-.684 1.75-1.537 2.39-2.518z"/>
            </svg>
          </button>
        </div>
      </div>
      <button
        onClick={() => {
          appDispatch({ type: 'SET_PAGE', payload: 'landing' });
          window.history.pushState(null, '', '/');
        }}
        className="mt-6 px-6 py-3 bg-gray-900 text-white font-bold rounded-lg hover:bg-gray-800 transition-colors"
      >
        Back to Home
      </button>
    </motion.div>
  );
}
