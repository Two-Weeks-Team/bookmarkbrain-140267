"use client";

import { useEffect, useState } from 'react';

interface Tag {
  id: string;
  name: string;
  count: number;
}

export default function TagCloud() {
  const [tags, setTags] = useState<Tag[]>([]);

  useEffect(() => {
    fetch('/api/tags')
      .then((res) => res.json())
      .then((data) => setTags(data.tags));
  }, []);

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-3">Popular Tags</h2>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <button
            key={tag.id}
            className="px-3 py-1 bg-gray-200 rounded-full text-sm hover:bg-gray-300 transition-colors"
          >
            {tag.name} ({tag.count})
          </button>
        ))}
      </div>
    </div>
  );
}