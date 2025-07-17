import React, { useRef, useEffect } from "react";

function AudioAnalyzer() {
  const audioRef = useRef(null);

  useEffect(() => {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const source = ctx.createMediaElementSource(audioRef.current);
    const analyser = ctx.createAnalyser();
    source.connect(analyser);
    analyser.connect(ctx.destination);
  }, []);

  return (
    <div className="mb-4">
      <audio ref={audioRef} controls src="https://example.com/sample.mp3" />
    </div>
  );
}

export default AudioAnalyzer;
