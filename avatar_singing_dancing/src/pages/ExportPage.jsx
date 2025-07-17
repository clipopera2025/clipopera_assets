import React, { useEffect } from "react";
import BillingModal from "../components/BillingModal";
import { useAuth } from "../context/AuthContext";

const ExportPage = () => {
  const { plan } = useAuth();

  useEffect(() => {
    // Auto-load billing modal
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {plan !== "pro" ? <BillingModal open /> : <p>You’re ready to export.</p>}
    </div>
  );
};

export default ExportPage;
