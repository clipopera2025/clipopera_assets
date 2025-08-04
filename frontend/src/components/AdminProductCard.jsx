import React, { useState } from 'react';

export default function AdminProductCard({ product, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPrice, setEditedPrice] = useState(product.price);
  const [editedStock, setEditedStock] = useState(product.variants[0].stock);
  const image = product.images?.[0] || 'https://placehold.co/600x400';

  const handleSave = () => {
    onUpdate(product.id, {
      price: Number(editedPrice),
      variants: [{ ...product.variants[0], stock: Number(editedStock) }],
    });
    setIsEditing(false);
  };

  return (
    <div className="bg-gray-100 p-4 rounded-xl shadow-sm">
      <img src={image} alt={product.title} className="w-full h-40 object-cover rounded-md mb-4" />
      <h3 className="text-lg font-semibold">{product.title}</h3>
      {isEditing ? (
        <div className="space-y-2 mt-2">
          <input
            type="number"
            value={editedPrice}
            onChange={(e) => setEditedPrice(e.target.value)}
            className="w-full px-2 py-1 border rounded-md"
          />
          <input
            type="number"
            value={editedStock}
            onChange={(e) => setEditedStock(e.target.value)}
            className="w-full px-2 py-1 border rounded-md"
          />
          <button onClick={handleSave} className="w-full py-2 bg-green-500 text-white rounded-lg">Save</button>
        </div>
      ) : (
        <div className="mt-2 space-y-1">
          <p className="text-gray-700">Price: <span className="font-mono">${product.price}</span></p>
          <p className="text-gray-700">Stock: <span className="font-mono">{product.variants[0].stock}</span></p>
          <button onClick={() => setIsEditing(true)} className="w-full py-2 mt-2 bg-blue-500 text-white rounded-lg">Edit</button>
        </div>
      )}
    </div>
  );
}
