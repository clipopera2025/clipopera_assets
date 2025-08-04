import { createContext } from 'react';

// Cart context and reducer
export const CartContext = createContext(null);
export const CartDispatchContext = createContext(null);

export const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const { id, title, price, quantity, image } = action.payload;
      const existingItem = state.find(item => item.id === id);
      if (existingItem) {
        return state.map(item =>
          item.id === id ? { ...item, quantity: item.quantity + quantity } : item
        );
      }
      return [...state, { id, title, price, quantity, image }];
    }
    case 'REMOVE_ITEM': {
      return state.filter(item => item.id !== action.payload.id);
    }
    case 'UPDATE_QUANTITY': {
      const { id, quantity } = action.payload;
      if (quantity <= 0) {
        return state.filter(item => item.id !== id);
      }
      return state.map(item =>
        item.id === id ? { ...item, quantity: quantity } : item
      );
    }
    case 'CLEAR_CART':
      return [];
    default:
      return state;
  }
};

// Application context and reducer
export const AppStateContext = createContext(null);
export const AppDispatchContext = createContext(null);

export const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_PAGE':
      return { ...state, currentPage: action.payload };
    case 'SET_PRODUCTS':
      return { ...state, products: action.payload, loading: false, error: null };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'LOGIN':
      return { ...state, isAdmin: true, currentPage: 'admin' };
    case 'LOGOUT':
      return { ...state, isAdmin: false, currentPage: 'landing' };
    default:
      return state;
  }
};
