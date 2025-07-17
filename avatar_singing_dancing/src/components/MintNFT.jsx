import React, { useState } from "react";
import { useNFTCollection, useAddress } from "@thirdweb-dev/react";

const MintNFT = ({ imageUrl, name }) => {
  const address = useAddress();
  const { contract } = useNFTCollection("YOUR_CONTRACT_ADDRESS"); // Replace with real
  const [minting, setMinting] = useState(false);
  const [status, setStatus] = useState("");

  const mintNFT = async () => {
    if (!address) return setStatus("Connect your wallet first.");
    setMinting(true);
    try {
      const tx = await contract.mintTo(address, { name, image: imageUrl });
      setStatus("✅ Minted!");
    } catch (err) {
      setStatus("❌ Mint failed.");
    } finally {
      setMinting(false);
    }
  };

  return (
    <div className="mt-4">
      <button onClick={mintNFT} disabled={minting} className="bg-blue-600 px-4 py-2 text-white rounded">
        {minting ? "Minting..." : "Mint NFT"}
      </button>
      <p className="mt-2 text-sm">{status}</p>
    </div>
  );
};

export default MintNFT;
