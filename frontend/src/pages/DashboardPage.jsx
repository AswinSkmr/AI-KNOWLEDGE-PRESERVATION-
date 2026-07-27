import { useAuth } from "../context/AuthContext";

function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>
        Welcome, {user?.full_name} ({user?.role})
      </p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default DashboardPage;