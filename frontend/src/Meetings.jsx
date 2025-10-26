import React, { useEffect, useState } from "react";

export default function Meetings() {
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/meetings/")
      .then((res) => res.json())
      .then(setMeetings);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <h1 className="text-3xl font-bold text-blue-700 mb-6">📂 Meeting Archive</h1>
      <div className="space-y-4">
        {meetings.map((m) => (
          <div key={m.id} className="bg-white/90 border border-blue-100 p-4 rounded-lg shadow-sm">
            <p><strong>{m.filename}</strong></p>
            <p className="text-gray-600 text-sm">{new Date(m.created_at).toLocaleString()}</p>
            <p className="mt-2 text-gray-700">{m.summary.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
