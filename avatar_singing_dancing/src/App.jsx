import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThirdwebProvider, ChainId } from "@thirdweb-dev/react";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ExportPage from "./pages/ExportPage";
import NFTPage from "./pages/NFTPage";
import ConfirmPage from "./pages/ConfirmPage";

function App() {
  return (
    <ThirdwebProvider desiredChainId={ChainId.Polygon}>
      <AuthProvider>
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/export" element={<ExportPage />} />
            <Route path="/nft" element={<NFTPage />} />
            <Route path="/confirm" element={<ConfirmPage />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThirdwebProvider>
  );
}

export default App;
