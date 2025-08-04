import React, { useContext } from 'react';
import { ShoppingCartIcon, UserIcon } from '@heroicons/react/24/outline';
import { CartContext, AppStateContext, AppDispatchContext } from '../contexts';

export default function Header() {
  const cartState = useContext(CartContext);
  const appState = useContext(AppStateContext);
  const appDispatch = useContext(AppDispatchContext);

  const cartCount = cartState.reduce((total, item) => total + item.quantity, 0);

  const handleNavigate = (page) => {
    appDispatch({ type: 'SET_PAGE', payload: page });
    window.history.pushState(null, '', page === 'landing' ? '/' : `/${page}`);
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <button onClick={() => handleNavigate('landing')} className="text-xl font-bold tracking-tight text-gray-900 rounded-md p-2 hover:bg-gray-100 transition-colors">
            Weave Shop
          </button>
          <button onClick={() => handleNavigate('landing')} className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors hidden sm:block">
            Shop
          </button>
        </div>
        <div className="flex items-center space-x-4">
          {appState.isAdmin ? (
            <button
              onClick={() => appDispatch({ type: 'LOGOUT' })}
              className="flex items-center space-x-1 text-gray-500 hover:text-gray-900 transition-colors p-2 rounded-md hover:bg-red-100"
            >
              <UserIcon className="h-5 w-5" />
              <span className="hidden sm:block">Logout</span>
            </button>
          ) : (
            <button
              onClick={() => handleNavigate('admin-login')}
              className="flex items-center space-x-1 text-gray-500 hover:text-gray-900 transition-colors p-2 rounded-md hover:bg-gray-100"
            >
              <UserIcon className="h-5 w-5" />
              <span className="hidden sm:block">Admin</span>
            </button>
          )}
          <button
            onClick={() => handleNavigate('cart')}
            className="relative p-2 rounded-md text-gray-500 hover:text-gray-900 transition-colors hover:bg-gray-100"
          >
            <ShoppingCartIcon className="h-6 w-6" />
            {cartCount > 0 && (
              <span className="absolute top-0 right-0 inline-flex items-center justify-center h-4 w-4 rounded-full bg-red-500 text-white text-xs font-bold">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
