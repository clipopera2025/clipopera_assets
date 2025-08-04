import React, { useEffect, useState } from 'react';

export default function CountdownTimer() {
  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);
    return () => clearTimeout(timer);
  });

  function calculateTimeLeft() {
    const difference = +new Date('2024-12-31T23:59:59') - +new Date();
    let timeLeft = {};

    if (difference > 0) {
      timeLeft = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }
    return timeLeft;
  }

  const timerComponents = Object.keys(timeLeft).map((unit) => {
    if (!timeLeft[unit]) {
      return null;
    }
    return (
      <div key={unit} className="flex flex-col items-center p-4 bg-white text-red-500 rounded-lg shadow-md">
        <span className="text-3xl md:text-5xl font-extrabold">{timeLeft[unit]}</span>
        <span className="text-xs md:text-sm font-medium">{unit.toUpperCase()}</span>
      </div>
    );
  });

  return (
    <div className="flex justify-center space-x-2 md:space-x-4">
      {timerComponents.length ? timerComponents : <span className="text-lg">Sale has ended!</span>}
    </div>
  );
}
