import { createContext, useContext, useState } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  async function login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    const { access_token } = response.data;

    localStorage.setItem("access_token", access_token);

    const meResponse = await api.get("/users/me");
    localStorage.setItem("user", JSON.stringify(meResponse.data));
    setUser(meResponse.data);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
  }

  const value = {
    user,
    isAuthenticated: Boolean(user),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}