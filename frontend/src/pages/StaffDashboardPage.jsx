import { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";

function StaffDashboardPage() {
  const { user } = useAuth();
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .get("/staff/dashboard-check")
      .then((response) => setMessage(response.data.message))
      .catch(() => setMessage("Could not verify staff access"));
  }, []);

  return (
    <div>
      <h1>Staff Dashboard</h1>
      <p>Logged in as {user?.full_name} ({user?.role})</p>
      <p>{message}</p>
    </div>
  );
}

export default StaffDashboardPage;