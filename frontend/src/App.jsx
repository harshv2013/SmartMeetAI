import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first!");
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/transcribe/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    const res = await fetch(`http://127.0.0.1:8000/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    setResults(data);
    };

  return (
    <div className="min-h-screen bg-gradient-to-r from-cyan-50 via-blue-100 to-indigo-50 text-gray-900 flex flex-col items-center justify-center p-6">

      <h1 className="text-4xl font-bold text-blue-600 mb-6">SmartMeetAI 🧠</h1>

      <div className="bg-white p-6 rounded-2xl shadow-md w-full max-w-lg text-center border border-gray-200">
        <input
          type="file"
          accept=".mp3,.mp4,.wav"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 mb-4 p-2"
        />
        <button
          onClick={handleUpload}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-all"
        >
          {loading ? "Processing..." : "Upload & Analyze"}
        </button>
      </div>

      {/* {result && (
        <div className="mt-8 w-full max-w-3xl bg-white p-6 rounded-xl shadow-md border border-gray-200 text-left">
          <h2 className="text-xl font-bold text-blue-700 mb-3">
            📝 Meeting Insights
          </h2>
          <p><strong>File:</strong> {result.filename}</p>
          <p className="text-gray-500 text-sm mb-4">
            {result.transcript_path}
          </p>

          {result.insights?.summary ? (
            <>
              <p className="mb-2"><strong>Summary:</strong> {result.insights.summary}</p>
              <p><strong>Topics:</strong> {result.insights.key_topics?.join(", ") || "None"}</p>
              <p><strong>Sentiment:</strong> {result.insights.sentiment}</p>
            </>
          ) : (
            <p className="text-yellow-600">No summary available.</p>
          )}
        </div>
      )} */}
      {result && (
        <div className="mt-10 w-full max-w-3xl bg-white/80 backdrop-blur-md border border-blue-100 p-6 rounded-2xl shadow-lg">
            <h2 className="text-2xl font-bold text-blue-700 mb-4 flex items-center gap-2">
            📋 Meeting Insights
            </h2>

            <div className="text-sm text-gray-700">
            <p><strong>📁 File:</strong> {result.filename}</p>
            <p className="text-gray-400 mb-4">{result.transcript_path}</p>

            {result.insights?.summary ? (
                <>
                <p className="mb-2"><strong>🧠 Summary:</strong> {result.insights.summary}</p>
                <p className="mb-2"><strong>🔑 Topics:</strong> {result.insights.key_topics?.join(", ") || "—"}</p>
                <p className="mb-2"><strong>📋 Decisions:</strong> {result.insights.decisions?.join(", ") || "—"}</p>
                <p className="mb-2"><strong>✅ Action Items:</strong> {result.insights.action_items?.join(", ") || "—"}</p>
                <p><strong>🎭 Sentiment:</strong> {result.insights.sentiment}</p>
                </>
            ) : (
                <p className="text-yellow-600 font-medium">⚠️ No summary available.</p>
            )}
            </div>
        </div>
        )}

        {/* 🔍 Semantic Search Section */}
        <div className="mt-10 w-full max-w-2xl bg-white p-6 rounded-2xl shadow-md border border-gray-200">
        <h2 className="text-xl font-bold text-blue-700 mb-3">🔍 Search Meetings</h2>
        <div className="flex gap-2">
            <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search transcripts, topics, or decisions..."
            className="flex-1 p-2 border border-gray-300 rounded-lg"
            />
            <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
            Search
            </button>
        </div>

        {results.length > 0 && (
            <div className="mt-4 space-y-3">
                {results.map((r) => (
                <div
                    key={r.id}
                    className="bg-blue-50 p-4 rounded-lg border border-blue-100 shadow-sm hover:shadow-md transition-shadow"
                >
                    <p className="text-sm font-semibold text-blue-700">
                    🎧 {r.filename}
                    </p>
                    <p className="text-gray-600 text-sm mt-1">{r.snippet}</p>
                </div>
                ))}
            </div>
            )}

        </div>


    </div>
  );
}

export default App;
