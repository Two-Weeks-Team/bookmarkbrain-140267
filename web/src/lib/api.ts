export async function createBookmark(data: { url: string; title: string }) {
  const res = await fetch('/api/bookmarks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function searchBookmarks(query: string) {
  const res = await fetch(`/api/bookmarks/search?query=${encodeURIComponent(query)}`);
  return res.json();
}