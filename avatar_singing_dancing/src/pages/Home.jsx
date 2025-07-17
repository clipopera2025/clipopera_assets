import React from "react";
import DancingAvatar from "../components/DancingAvatar";
import AudioAnalyzer from "../components/AudioAnalyzer";

function Home() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-4">🎤 ClipOpera Avatar</h1>
      <AudioAnalyzer />
      <DancingAvatar />
    </div>
  );
}

export default Home;
