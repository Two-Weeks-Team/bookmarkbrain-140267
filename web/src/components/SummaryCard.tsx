"use client";

import { useState } from 'react';

interface Bookmark {
  id: string;
  url: string;
  title: string;
  summary: string;
  tags: string[];
}

export default function SummaryCard({ bookmark }: { bookmark: Bookmark }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border rounded p-3 hover:shadow-md transition-shadow">
      <h3 className="font-medium">
        <a href={bookmark.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
          {bookmark.title}
        </a>
      </h3>
      <p className="text-sm text-gray-600 mt-1">
        {expanded ? bookmark.summary : `${bookmark.summary.substring(0, 100)}...`}
        {!expanded && (
          <button onClick={() => setExpanded(true)} className="text-blue-500 ml-1">
            Read more
          </button>
        )}
      </p>
      <div className="flex flex-wrap gap-1 mt-2">
        {bookmark.tags.map((tag) => (
          <span key={tag} className="text-xs bg-gray-200 px-2 py-1 rounded">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}