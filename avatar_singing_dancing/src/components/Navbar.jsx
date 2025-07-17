import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="bg-black text-white p-4 flex justify-between">
    <Link to="/" className="font-bold text-lg">ClipOpera OS</Link>
    <div className="space-x-4">
      <Link to="/export">Export</Link>
      <Link to="/nft">NFT</Link>
    </div>
  </nav>
);

export default Navbar;
