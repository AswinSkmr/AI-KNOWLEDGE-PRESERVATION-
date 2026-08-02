import { useEffect, useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
const DOCUMENT_TYPES = ["", "textbook", "project_report"];

function DocumentListPage() {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [documentType, setDocumentType] = useState("");
  const [sortBy, setSortBy] = useState("uploaded_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [error, setError] = useState("");

  async function loadDocuments() {
    setError("");
    try {
      const response = await api.get("/documents", {
        params: {
          page,
          page_size: 10,
          document_type: documentType || undefined,
          search: search || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        },
      });
      setDocuments(response.data.documents);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      setError("Failed to load documents");
      console.error(err);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, [page, documentType, sortBy, sortOrder]);

  function handleSearchSubmit(event) {
    event.preventDefault();
    setPage(1);
    loadDocuments();
  }

  function toggleSort(column) {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
    setPage(1);
  }

  function formatFileSize(bytes) {
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  return (
    <div>
      <h1>Documents</h1>

      <form onSubmit={handleSearchSubmit} style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Search by title..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit">Search</button>

        <select
          value={documentType}
          onChange={(e) => {
            setDocumentType(e.target.value);
            setPage(1);
          }}
        >
          {DOCUMENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type === "" ? "All Types" : type}
            </option>
          ))}
        </select>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th onClick={() => toggleSort("title")} style={{ cursor: "pointer" }}>
              Title {sortBy === "title" && (sortOrder === "asc" ? "▲" : "▼")}
            </th>
            <th>Type</th>
            <th>Category</th>
            <th onClick={() => toggleSort("file_size")} style={{ cursor: "pointer" }}>
              Size {sortBy === "file_size" && (sortOrder === "asc" ? "▲" : "▼")}
            </th>
            <th onClick={() => toggleSort("uploaded_at")} style={{ cursor: "pointer" }}>
              Uploaded {sortBy === "uploaded_at" && (sortOrder === "asc" ? "▲" : "▼")}
            </th>
          </tr>
        </thead>
         <tbody>
  {documents.map((doc) => (
    <tr
      key={doc.document_id}
      onClick={() => navigate(`/documents/${doc.document_id}`)}
      style={{ cursor: "pointer" }}
    >
      <td>{doc.title}</td>
      <td>{doc.document_type}</td>
      <td>{doc.category || "—"}</td>
      <td>{formatFileSize(doc.file_size)}</td>
      <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
    </tr>
  ))}
</tbody>
      </table>

      <div style={{ marginTop: "1rem" }}>
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
          Previous
        </button>
        <span> Page {page} of {totalPages} </span>
        <button
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default DocumentListPage;