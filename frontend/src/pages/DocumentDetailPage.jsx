import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";
import { useAuth } from "../context/AuthContext";

function DocumentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [document, setDocument] = useState(null);
  const [error, setError] = useState("");

  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ title: "", description: "", category: "" });

  const [previewBlobUrl, setPreviewBlobUrl] = useState(null);

  const [extraction, setExtraction] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);

  const [summaries, setSummaries] = useState([]);
  const [isGeneratingSummaries, setIsGeneratingSummaries] = useState(false);

  // Milestone 3
  const [chunkCount, setChunkCount] = useState(null);
  const [isChunking, setIsChunking] = useState(false);

  async function loadDocument() {
    setError("");
    try {
      const response = await api.get(`/documents/${id}`);
      setDocument(response.data);
      setEditForm({
        title: response.data.title,
        description: response.data.description || "",
        category: response.data.category || "",
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Document not found");
    }
  }

  async function loadSummaries() {
    try {
      const response = await api.get(`/documents/${id}/summaries`);
      setSummaries(response.data.summaries);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadDocument();
    loadSummaries();
  }, [id]);

  useEffect(() => {
    if (!document || document.mime_type !== "application/pdf") return;

    let objectUrl;

    api
      .get(`/documents/${id}/preview`, { responseType: "blob" })
      .then((response) => {
        objectUrl = window.URL.createObjectURL(response.data);
        setPreviewBlobUrl(objectUrl);
      })
      .catch(() => setPreviewBlobUrl(null));

    return () => {
      if (objectUrl) window.URL.revokeObjectURL(objectUrl);
    };
  }, [document, id]);

  async function handleSaveEdit(event) {
    event.preventDefault();
    try {
      await api.patch(`/documents/${id}`, editForm);
      setIsEditing(false);
      loadDocument();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update document");
    }
  }

  async function handleDelete() {
    if (
      !window.confirm(
        `Delete "${document.title}"? This can be undone by an administrator later, but it will disappear from all listings immediately.`
      )
    ) {
      return;
    }
    try {
      await api.delete(`/documents/${id}`);
      navigate("/documents");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete document");
    }
  }

  async function handleDownload() {
    const response = await api.get(`/documents/${id}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = window.document.createElement("a");
    link.href = url;
    link.download = document.original_file_name;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function handleExtractText() {
    setIsExtracting(true);
    setExtraction(null);
    try {
      const response = await api.post(`/documents/${id}/extract-text`);
      setExtraction(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Text extraction failed");
    } finally {
      setIsExtracting(false);
    }
  }

  async function handleGenerateSummaries() {
    setIsGeneratingSummaries(true);
    try {
      const response = await api.post(`/documents/${id}/generate-summaries`);
      setSummaries(response.data.summaries);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate summaries");
    } finally {
      setIsGeneratingSummaries(false);
    }
  }

  // Milestone 3
  async function handleGenerateChunks() {
    setIsChunking(true);
    try {
      const response = await api.post(`/documents/${id}/generate-chunks`);
      setChunkCount(response.data.chunk_count);
    } catch (err) {
      setError(err.response?.data?.detail || "Chunking failed");
    } finally {
      setIsChunking(false);
    }
  }

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!document) return <p>Loading...</p>;

  const canEdit = user?.role === "admin";

  return (
    <div>
      <button onClick={() => navigate("/documents")}>← Back to list</button>

      {isEditing ? (
        <form onSubmit={handleSaveEdit}>
          <div>
            <label>Title</label>
            <input
              type="text"
              value={editForm.title}
              onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
              required
            />
          </div>
          <div>
            <label>Description</label>
            <textarea
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
            />
          </div>
          <div>
            <label>Category</label>
            <input
              type="text"
              value={editForm.category}
              onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
            />
          </div>
          <button type="submit">Save</button>
          <button type="button" onClick={() => setIsEditing(false)}>
            Cancel
          </button>
        </form>
      ) : (
        <>
          <h1>{document.title}</h1>
          <p>{document.description || "No description provided."}</p>
          <p>
            <strong>Type:</strong> {document.document_type} &nbsp;
            <strong>Category:</strong> {document.category || "—"} &nbsp;
            <strong>Size:</strong> {(document.file_size / (1024 * 1024)).toFixed(2)} MB
          </p>
          <p>
            <strong>Uploaded:</strong> {new Date(document.uploaded_at).toLocaleString()}
          </p>

          <button onClick={handleDownload}>Download</button>
          {canEdit && <button onClick={() => setIsEditing(true)}>Edit</button>}
          {canEdit && (
            <button onClick={handleDelete} style={{ color: "red" }}>
              Delete
            </button>
          )}
          {canEdit && (
            <button onClick={handleExtractText} disabled={isExtracting}>
              {isExtracting ? "Extracting..." : "Extract Text"}
            </button>
          )}
          {canEdit && (
            <button onClick={handleGenerateSummaries} disabled={isGeneratingSummaries}>
              {isGeneratingSummaries ? "Generating..." : "Generate Summaries"}
            </button>
          )}
          {canEdit && (
            <button onClick={handleGenerateChunks} disabled={isChunking}>
              {isChunking ? "Chunking..." : "Chunk Document"}
            </button>
          )}

          {extraction && (
            <div style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #ccc" }}>
              <p>
                <strong>Status:</strong> {extraction.text_extraction_status}
              </p>
              {extraction.page_count != null && (
                <p>
                  <strong>Pages:</strong> {extraction.page_count}
                </p>
              )}
              {extraction.extraction_error && (
                <p style={{ color: "orange" }}>{extraction.extraction_error}</p>
              )}
              {extraction.extracted_text_preview && (
                <p>
                  <strong>Preview:</strong> {extraction.extracted_text_preview}...
                </p>
              )}
            </div>
          )}

          {summaries.length > 0 && (
            <div style={{ marginTop: "1rem" }}>
              <h3>Summaries</h3>
              {summaries.map((s) => (
                <div key={s.summary_id} style={{ marginBottom: "0.75rem" }}>
                  <strong>{s.summary_type}</strong>
                  <p>{s.summary}</p>
                </div>
              ))}
            </div>
          )}

          {chunkCount !== null && (
            <p style={{ marginTop: "1rem" }}>Document split into {chunkCount} chunks.</p>
          )}
        </>
      )}

      {document.mime_type === "application/pdf" && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3>Preview</h3>
          {previewBlobUrl ? (
            <iframe
              src={previewBlobUrl}
              title={document.title}
              width="100%"
              height="600"
              style={{ border: "1px solid #ccc" }}
            />
          ) : (
            <p>Loading preview...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default DocumentDetailPage;