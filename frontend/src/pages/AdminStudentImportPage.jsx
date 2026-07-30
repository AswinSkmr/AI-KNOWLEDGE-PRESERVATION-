import { useState } from "react";
import api from "../api";

function AdminStudentImportPage() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) return;

    setError("");
    setSummary(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/students/import", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSummary(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div>
      <h1>Import Students</h1>

      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={!file || isUploading}>
          {isUploading ? "Uploading..." : "Upload CSV"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {summary && (
        <div style={{ marginTop: "1rem" }}>
          <p>
            {summary.created_count} created, {summary.skipped_count} skipped,{" "}
            {summary.error_count} errors (of {summary.total_rows} rows)
          </p>

          <table border="1" cellPadding="8">
            <thead>
              <tr>
                <th>Row</th>
                <th>Status</th>
                <th>Email</th>
                <th>Detail</th>
                <th>Temporary Password</th>
              </tr>
            </thead>
            <tbody>
              {summary.results.map((r) => (
                <tr key={r.row_number}>
                  <td>{r.row_number}</td>
                  <td>{r.status}</td>
                  <td>{r.email}</td>
                  <td>{r.detail}</td>
                  <td>{r.temporary_password || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AdminStudentImportPage;