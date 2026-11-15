import { useEffect, useState } from 'react';
import axios from 'axios';

export function HomePage() {
  const [health, setHealth] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get('/api/health')
      .then((res) => setHealth(res.data.message))
      .catch(() => setHealth('Backend unreachable'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-4">Frontline Document & Knowledge Workspace</h1>
      <p className="text-gray-600 mb-6">
        AI-assisted frontline document and knowledge retrieval — Phase 1 foundation.
      </p>
      <div className="p-4 rounded-lg bg-gray-100">
        <p className="text-gray-700">Backend health: <span className="font-semibold">{health}</span></p>
      </div>
    </div>
  );
}
