import { useEffect, useState } from "react";
import api from "../api";

function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [roleFilter, setRoleFilter] = useState("");
  const [error, setError] = useState("");

  async function loadUsers() {
    setError("");
    try {
      const params = roleFilter ? { role: roleFilter } : {};
      const response = await api.get("/users", { params });
      setUsers(response.data);
    } catch (err) {
      setError("Failed to load users");
      console.error(err);
    }
  }

  useEffect(() => {
    loadUsers();
  }, [roleFilter]);

  async function toggleStatus(user) {
    const action = user.is_active ? "deactivate" : "activate";
    try {
      await api.patch(`/users/${user.id}/${action}`);
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Action failed");
      console.error(err);
    }
  }

  return (
    <div>
      <h1>User Management</h1>

      <label>
        Filter by role:{" "}
        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
          <option value="">All</option>
          <option value="admin">Admin</option>
          <option value="staff">Staff</option>
          <option value="student">Student</option>
        </select>
      </label>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <table border="1" cellPadding="8" style={{ marginTop: "1rem" }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.full_name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button onClick={() => toggleStatus(user)}>
                  {user.is_active ? "Deactivate" : "Activate"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminUsersPage;