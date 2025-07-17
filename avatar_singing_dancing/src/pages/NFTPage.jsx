import React from "react";
import MintNFT from "../components/MintNFT";
import { useAuth } from "../context/AuthContext";

const NFTPage = () => {
  const { plan } = useAuth();

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {plan !== "pro" ? <p>Upgrade to mint NFTs</p> : <MintNFT imageUrl="https://example.com/avatar.png" name="ClipOpera Avatar 001" />}
    </div>
  );
};

export default NFTPage;
