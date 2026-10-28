const base = import.meta.env.VITE_API_BASE || '';
export async function query(path, city, extra = '', signal) {
  const params = `city=${encodeURIComponent(city)}${extra ? '&' + extra : ''}`;
  const response = await fetch(`${base}/api/${path}?${params}`, {signal});
  if (!response.ok) {
    let reason = '';
    try { reason = (await response.json()).detail || ''; } catch { /* ignore */ }
    throw new Error(reason || `API unavailable (HTTP ${response.status})`);
  }
  return response.json();
}
