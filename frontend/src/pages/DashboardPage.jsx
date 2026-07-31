import { useAuth } from "../context/AuthContext";

function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>
        Welcome, {user?.full_name} ({user?.role})
      </p>

      {(user?.role === "staff" || user?.role === "admin") && (
        <p><a href="/staff/dashboard">Staff Dashboard</a></p>
      )}
      {user?.role === "admin" && (
        <>
          <p><a href="/admin/users">Manage Users</a></p>
          <p><a href="/admin/students/import">Import Students</a></p>
          <p><a href="/admin/staff">Manage Staff</a></p>
        </>
      )}

      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default DashboardPage;