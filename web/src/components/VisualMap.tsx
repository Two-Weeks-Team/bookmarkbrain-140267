'use client';

import { useEffect, useRef } from 'react';

interface Bookmark {
  id: string;
  title: string;
  tags: string[];
}

export default function VisualMap({ bookmarks }: { bookmarks: Bookmark[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || bookmarks.length === 0) return;

    // Simple visual map implementation - replace with D3/vis.js in production
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'w-full h-64');
    
    const spacing = 80;
    bookmarks.forEach((bookmark, i) => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', (i * spacing).toString());
      circle.setAttribute('cy', '100');
      circle.setAttribute('r', '15');
      circle.setAttribute('fill', '#3b82f6');
      circle.setAttribute('class', 'cursor-pointer hover:fill-blue-400');
      
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', (i * spacing).toString());
      text.setAttribute('y', '115');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('class', 'text-xs fill-white');
      text.textContent = bookmark.title.split(' ').slice(0, 2).join(' ');
      
      svg.appendChild(circle);
      svg.appendChild(text);
    });

    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(svg);
  }, [bookmarks]);

  return <div ref={containerRef} className="mt-8 border rounded p-4 bg-gray-50" />;
}