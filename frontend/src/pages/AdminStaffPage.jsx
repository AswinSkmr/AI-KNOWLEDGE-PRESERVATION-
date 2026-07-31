import { useEffect, useState } from "react";
import api from "../api";

const emptyForm = {
  university_id: "",
  full_name: "",
  email: "",
  department: "",
  designation: "",
  employee_id: "",
};

function AdminStaffPage() {
  const [staffList, setStaffList] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [newTempPassword, setNewTempPassword] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  async function loadStaff() {
    const response = await api.get("/staff");
    setStaffList(response.data);
  }

  useEffect(() => {
    loadStaff();
  }, []);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    setNewTempPassword("");
    try {
      const response = await api.post("/staff", form);
      setNewTempPassword(response.data.temporary_password);
      setForm(emptyForm);
      loadStaff();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create staff member");
    }
  }

  function startEdit(staff) {
    setEditingId(staff.id);
    setForm({
      university_id: staff.university_id,
      full_name: staff.full_name,
      email: staff.email,
      department: staff.department || "",
      designation: staff.designation || "",
      employee_id: staff.employee_id || "",
    });
  }

  async function handleSaveEdit(event) {
    event.preventDefault();
    setError("");
    try {
      await api.patch(`/staff/${editingId}`, {
        full_name: form.full_name,
        department: form.department,
        designation: form.designation,
        employee_id: form.employee_id,
      });
      setEditingId(null);
      setForm(emptyForm);
      loadStaff();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update staff member");
    }
  }

  async function handleDisable(id) {
    try {
      await api.patch(`/staff/${id}/disable`);
      loadStaff();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to disable staff member");
    }
  }

  return (
    <div>
      <h1>Staff Management</h1>

      <h2>{editingId ? "Edit Staff Member" : "Create Staff Member"}</h2>
      <form onSubmit={editingId ? handleSaveEdit : handleCreate}>
        <input
          placeholder="University ID"
          value={form.university_id}
          onChange={(e) => updateField("university_id", e.target.value)}
          disabled={Boolean(editingId)}
          required
        />
        <input
          placeholder="Full Name"
          value={form.full_name}
          onChange={(e) => updateField("full_name", e.target.value)}
          required
        />
        <input
          placeholder="Email"
          value={form.email}
          onChange={(e) => updateField("email", e.target.value)}
          disabled={Boolean(editingId)}
          required
        />
        <input
          placeholder="Department"
          value={form.department}
          onChange={(e) => updateField("department", e.target.value)}
        />
        <input
          placeholder="Designation"
          value={form.designation}
          onChange={(e) => updateField("designation", e.target.value)}
        />
        <input
          placeholder="Employee ID"
          value={form.employee_id}
          onChange={(e) => updateField("employee_id", e.target.value)}
        />
        <button type="submit">{editingId ? "Save Changes" : "Create Staff"}</button>
        {editingId && (
          <button type="button" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
            Cancel
          </button>
        )}
      </form>

      {newTempPassword && (
        <p style={{ color: "green" }}>
          Staff created. Temporary password: <strong>{newTempPassword}</strong>
        </p>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <table border="1" cellPadding="8" style={{ marginTop: "1rem" }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Department</th>
            <th>Designation</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {staffList.map((staff) => (
            <tr key={staff.id}>
              <td>{staff.full_name}</td>
              <td>{staff.email}</td>
              <td>{staff.department}</td>
              <td>{staff.designation}</td>
              <td>{staff.is_active ? "Active" : "Disabled"}</td>
              <td>
                <button onClick={() => startEdit(staff)}>Edit</button>{" "}
                {staff.is_active && (
                  <button onClick={() => handleDisable(staff.id)}>Disable</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminStaffPage;