import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import "./style.css";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  const chooseFile = (event) => {
    const selected = event.target.files?.[0];
    setError(""); setResult(null); setProgress(0);
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const upload = async () => {
    if (!file) return setError("Сначала выберите изображение");
    const data = new FormData();
    data.append("file", file);
    setLoading(true); setError(""); setResult(null);
    try {
      const response = await axios.post("http://localhost:8000/upload-image/", data, {
        onUploadProgress: (event) => event.total && setProgress(Math.round(event.loaded * 100 / event.total)),
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Не удалось загрузить файл");
    } finally { setLoading(false); }
  };

  return <main className="card">
    <h1>Загрузка изображения</h1>
    <input type="file" accept="image/png,image/jpeg" onChange={chooseFile} />
    {preview && <img className="preview" src={preview} alt="Предпросмотр" />}
    {file && <p>Файл: {file.name}</p>}
    <button onClick={upload} disabled={loading}>{loading ? "Загрузка..." : "Загрузить"}</button>
    {loading && <progress value={progress} max="100" />}
    {loading && <p>{progress}%</p>}
    {error && <p className="error">{error}</p>}
    {result && <section><h2>Файл загружен</h2><img className="preview" src={result.thumbnail_url} alt="Миниатюра" /><p><a href={result.original_url} target="_blank">Открыть оригинал</a></p></section>}
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
