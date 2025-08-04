import React, { useContext } from 'react';
import { AppDispatchContext } from '../contexts';

export default function ProductCard({ product }) {
  const appDispatch = useContext(AppDispatchContext);

  const handleNavigate = (page, params = {}) => {
    appDispatch({ type: 'SET_PAGE', payload: page });
    const query = new URLSearchParams(params).toString();
    window.history.pushState(null, '', `/${page}?${query}`);
  };

  const image = product.images?.[0] || 'https://placehold.co/600x400';

  return (
    <div
      className="bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer transform hover:scale-105 transition-all duration-300"
      onClick={() => handleNavigate('product', { id: product.id })}
    >
      <img src={image} alt={product.title} className="w-full h-64 object-cover" />
      <div className="p-4 text-center">
        <h3 className="text-xl font-semibold mb-1">{product.title}</h3>
        <p className="text-gray-600">${product.price}</p>
      </div>
    </div>
  );
}
