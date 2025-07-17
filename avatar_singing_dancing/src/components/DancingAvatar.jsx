import React, { useEffect, useRef } from "react";

function DancingAvatar() {
  const avatarRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      if (avatarRef.current) {
        avatarRef.current.classList.toggle("animate-bounce");
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mt-8">
      <img
        ref={avatarRef}
        src="https://example.com/avatar.png"
        alt="Dancing Avatar"
        className="w-40 mx-auto rounded-full"
      />
    </div>
  );
}

export default DancingAvatar;
