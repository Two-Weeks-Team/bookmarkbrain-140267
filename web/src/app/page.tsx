"use client";

import { useState, useEffect } from 'react';
import { searchBookmarks } from '@/lib/api';
import SummaryCard from '@/components/SummaryCard';
import TagCloud from '@/components/TagCloud';

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (searchTerm) {
      searchBookmarks(searchTerm).then(setResults);
    }
  }, [searchTerm]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">BookmarkBrain</h1>
      <input
        type="text"
        placeholder="Search bookmarks..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-2 mb-4 border rounded"
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {results.map((result) => (
          <SummaryCard key={result.id} bookmark={result} />
        ))}
      </div>
      <TagCloud />
    </div>
  );
}