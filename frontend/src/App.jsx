import React, { useReducer, useEffect } from 'react';
import {
  AppStateContext,
  AppDispatchContext,
  CartContext,
  CartDispatchContext,
  appReducer,
  cartReducer,
} from './contexts';
import Header from './components/Header';
import Footer from './components/Footer';
import LoadingScreen from './components/LoadingScreen';
import ErrorScreen from './components/ErrorScreen';
import LandingPage from './components/LandingPage';
import ProductPage from './components/ProductPage';
import CartPage from './components/CartPage';
import CheckoutPage from './components/CheckoutPage';
import ThankYouPage from './components/ThankYouPage';
import AdminLoginPage from './components/AdminLoginPage';
import AdminDashboard from './components/AdminDashboard';
import { AnimatePresence } from 'framer-motion';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  process.env.REACT_APP_API_BASE_URL ||
  'http://localhost:5000/api';

export default function App() {
  const [appState, appDispatch] = useReducer(appReducer, {
    currentPage: 'landing',
    products: [],
    loading: true,
    error: null,
    isAdmin: false,
  });

  const [cartState, cartDispatch] = useReducer(
    cartReducer,
    [],
    () => {
      const stored = typeof window !== 'undefined' ? localStorage.getItem('cart') : null;
      return stored ? JSON.parse(stored) : [];
    }
  );

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cartState));
  }, [cartState]);

  useEffect(() => {
    const fetchProducts = async () => {
      appDispatch({ type: 'SET_LOADING', payload: true });
      try {
        const response = await fetch(`${API_BASE_URL}/products`);
        if (!response.ok) {
          throw new Error('Failed to fetch products from the server.');
        }
        const data = await response.json();
        appDispatch({ type: 'SET_PRODUCTS', payload: data });
      } catch (e) {
        appDispatch({ type: 'SET_ERROR', payload: 'Failed to load products. Is the backend server running?' });
      }
    };
    fetchProducts();
  }, []);

  const { currentPage, products, loading, error, isAdmin } = appState;

  const renderPage = () => {
    if (loading) return <LoadingScreen />;
    if (error) return <ErrorScreen message={error} />;

    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      case 'product':
        const productId = new URLSearchParams(window.location.search).get('id');
        const product = products.find(p => p.id === productId);
        return product ? <ProductPage product={product} /> : <ErrorScreen message="Product not found." />;
      case 'cart':
        return <CartPage />;
      case 'checkout':
        return <CheckoutPage />;
      case 'thank-you':
        return <ThankYouPage />;
      case 'admin-login':
        return <AdminLoginPage />;
      case 'admin':
        return isAdmin ? <AdminDashboard /> : <AdminLoginPage />;
      default:
        return <LandingPage />;
    }
  };

  return (
    <AppStateContext.Provider value={appState}>
      <AppDispatchContext.Provider value={appDispatch}>
        <CartContext.Provider value={cartState}>
          <CartDispatchContext.Provider value={cartDispatch}>
            <div className="bg-gray-50 text-gray-800 min-h-screen font-sans">
              <Header />
              <main className="container mx-auto px-4 py-8">
                <AnimatePresence mode="wait">{renderPage()}</AnimatePresence>
              </main>
              <Footer />
            </div>
          </CartDispatchContext.Provider>
        </CartContext.Provider>
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}
