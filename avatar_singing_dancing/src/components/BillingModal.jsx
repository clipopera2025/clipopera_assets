import React from "react";

const BillingModal = ({ open }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center">
      <div className="bg-white text-black p-6 rounded">
        <h2 className="text-xl font-bold">Upgrade to Pro</h2>
        <p className="mt-2">Access premium export and NFT tools.</p>
        <button className="mt-4 bg-green-600 text-white px-4 py-2 rounded">Subscribe</button>
      </div>
    </div>
  );
};

export default BillingModal;
