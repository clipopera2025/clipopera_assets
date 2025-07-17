import React, { createContext, useState, useEffect, useContext } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [plan, setPlan] = useState("free");

  useEffect(() => {
    // Replace with your actual auth logic
    const fetchUser = async () => {
      setUser({ id: "123", email: "user@clipopera.com" });
      setPlan("pro"); // Simulated plan
    };
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, plan }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
