import { useState } from "react";
import api from "../api";

const DOCUMENT_TYPES = ["textbook", "project_report"];

function DocumentUploadPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [documentType, setDocumentType] = useState(DOCUMENT_TYPES[0]);
  const [category, setCategory] = useState("");
  const [file, setFile] = useState(null);

  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  function resetForm() {
    setTitle("");
    setDescription("");
    setDocumentType(DOCUMENT_TYPES[0]);
    setCategory("");
    setFile(null);
    setUploadProgress(0);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccessMessage("");

    if (!file) {
      setError("Please choose a PDF file to upload");
      return;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("description", description);
    formData.append("document_type", documentType);
    formData.append("category", category);
    formData.append("file", file);

    setIsUploading(true);

    try {
      const response = await api.post("/documents/upload", formData, {
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percent);
        },
      });
      setSuccessMessage(`Uploaded: ${response.data.title}`);
      resetForm();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div>
      <h1>Upload Document</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div>
          <label>Document Type</label>
          <select value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
            {DOCUMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Category</label>
          <input
            type="text"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g. Computer Science"
          />
        </div>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile) setFile(droppedFile);
          }}
          style={{
            border: "2px dashed #999",
            padding: "1.5rem",
            textAlign: "center",
            marginBottom: "0.5rem",
          }}
        >
          <p>{file ? file.name : "Drag a PDF here, or use the picker below"}</p>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            required
          />
        </div>

        {isUploading && (
          <div>
            <progress value={uploadProgress} max="100" />
            <span> {uploadProgress}%</span>
          </div>
        )}

        {error && <p style={{ color: "red" }}>{error}</p>}
        {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

        <button type="submit" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>
    </div>
  );
}

export default DocumentUploadPage;