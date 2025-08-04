import React, { useContext } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { AppDispatchContext } from '../contexts';

export default function ErrorScreen({ message }) {
  const appDispatch = useContext(AppDispatchContext);
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-8 bg-red-50 rounded-lg shadow-sm">
      <XMarkIcon className="h-16 w-16 text-red-500 mb-4" />
      <h2 className="text-2xl font-bold text-red-700 mb-2">An error occurred</h2>
      <p className="text-lg text-red-600 mb-4">{message}</p>
      <button
        onClick={() => {
          appDispatch({ type: 'SET_ERROR', payload: null });
          window.location.reload();
        }}
        className="px-6 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors"
      >
        Try Again
      </button>
    </div>
  );
}
