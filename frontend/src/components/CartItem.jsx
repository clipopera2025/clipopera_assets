import React, { useContext } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { CartDispatchContext } from '../contexts';

export default function CartItem({ item }) {
  const cartDispatch = useContext(CartDispatchContext);
  const image = item.image || 'https://placehold.co/600x400';
  return (
    <div className="flex items-center space-x-4 bg-white p-4 rounded-xl shadow-sm">
      <img src={image} alt={item.title} className="w-20 h-20 rounded-md object-cover" />
      <div className="flex-1">
        <h3 className="text-lg font-semibold">{item.title}</h3>
        <p className="text-gray-600">${item.price.toFixed(2)}</p>
      </div>
      <div className="flex items-center space-x-2">
        <input
          type="number"
          min="1"
          value={item.quantity}
          onChange={(e) => cartDispatch({ type: 'UPDATE_QUANTITY', payload: { id: item.id, quantity: Number(e.target.value) } })}
          className="w-16 px-2 py-1 border border-gray-300 rounded-md text-center"
        />
        <button
          onClick={() => cartDispatch({ type: 'REMOVE_ITEM', payload: { id: item.id } })}
          className="p-1 rounded-full text-gray-500 hover:text-red-500 hover:bg-red-100 transition-colors"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
