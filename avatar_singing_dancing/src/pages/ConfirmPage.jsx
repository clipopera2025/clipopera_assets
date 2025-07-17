import React from "react";
import { Link, useLocation } from "react-router-dom";

function ConfirmPage() {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const transactionId = query.get("transaction_id");

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-4 text-center">
      <h1 className="text-4xl font-bold text-green-400 mb-4">🎉 You're Pro Now!</h1>
      <p className="text-lg text-gray-300">Thanks for upgrading your plan.</p>
      {transactionId && (
        <p className="text-sm text-gray-500 mt-2">
          Recurly Transaction ID: <span className="text-white font-mono">{transactionId}</span>
        </p>
      )}
      <Link
        to="/dashboard"
        className="mt-6 px-6 py-2 rounded bg-green-600 hover:bg-green-700 transition"
      >
        Go to Dashboard
      </Link>
    </div>
  );
}

export default ConfirmPage;
