import React from 'react';

export default function LoadingScreen() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-gray-900 mb-4"></div>
      <p className="text-xl font-medium text-gray-700">Loading products...</p>
    </div>
  );
}
