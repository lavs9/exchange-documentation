import React, { useEffect, useState } from 'react';
import { Link2 } from 'lucide-react';

interface Backlink {
  source_file: string;
  source_title: string;
  snippet: string;
  line_number: number;
}

interface BacklinksPanelProps {
  documentId: string;
  version: string;
  filename: string;
  className?: string;
}

/**
 * Right sidebar panel showing "What links here?"
 *
 * Displays all documents that link to the current document
 * with context snippets.
 */
const BacklinksPanel: React.FC<BacklinksPanelProps> = ({
  documentId,
  version,
  filename,
  className = ''
}) => {
  const [backlinks, setBacklinks] = useState<Backlink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBacklinks = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `http://localhost:8000/api/documents/${documentId}/versions/${version}/backlinks/${filename}`
        );

        if (!response.ok) {
          throw new Error('Failed to fetch backlinks');
        }

        const data = await response.json();
        setBacklinks(data);
      } catch (err) {
        console.error('Error fetching backlinks:', err);
        setError('Failed to load backlinks');
      } finally {
        setLoading(false);
      }
    };

    if (documentId && version && filename) {
      fetchBacklinks();
    }
  }, [documentId, version, filename]);

  // Navigate to source document
  const handleNavigateToSource = (backlink: Backlink) => {
    // Extract filename from source_file path
    const parts = backlink.source_file.split('/');
    const sourceFilename = parts[parts.length - 1].replace('.md', '');

    // Determine if it's a chapter or note
    if (backlink.source_file.startsWith('chapters/')) {
      // Navigate to chapter
      // This would need integration with your routing
      console.log('Navigate to chapter:', sourceFilename);
    } else if (backlink.source_file.startsWith('notes/')) {
      // Navigate to note
      console.log('Navigate to note:', sourceFilename);
    } else if (backlink.source_file.startsWith('references/')) {
      // Navigate to reference
      console.log('Navigate to reference:', sourceFilename);
    }
  };

  // Highlight wikilink in snippet
  const highlightWikilink = (snippet: string) => {
    // Find [[wikilink]] pattern and highlight it
    const parts = snippet.split(/(\[\[[^\]]+\]\])/g);
    return parts.map((part, index) => {
      if (part.match(/\[\[[^\]]+\]\]/)) {
        return (
          <span key={index} className="bg-blue-100 text-blue-800 font-medium px-1 rounded">
            {part}
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  if (loading) {
    return (
      <div className={`bg-white border-l border-gray-200 p-4 ${className}`}>
        <div className="flex items-center gap-2 mb-4">
          <Link2 className="w-5 h-5 text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900">Linked References</h2>
        </div>
        <div className="text-sm text-gray-500">Loading backlinks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white border-l border-gray-200 p-4 ${className}`}>
        <div className="flex items-center gap-2 mb-4">
          <Link2 className="w-5 h-5 text-gray-400" />
          <h2 className="text-lg font-semibold text-gray-900">Linked References</h2>
        </div>
        <div className="text-sm text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className={`bg-white border-l border-gray-200 ${className}`}>
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <Link2 className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Linked References
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({backlinks.length})
            </span>
          </h2>
        </div>
      </div>

      {/* Backlinks list */}
      <div className="p-4 space-y-4 overflow-y-auto">
        {backlinks.length === 0 ? (
          <div className="text-center py-8">
            <Link2 className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No backlinks yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Link to this document using [[wikilinks]]
            </p>
          </div>
        ) : (
          backlinks.map((backlink, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
              onClick={() => handleNavigateToSource(backlink)}
            >
              {/* Source document title */}
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-gray-900 text-sm">
                  {backlink.source_title}
                </h3>
                <span className="text-xs text-gray-500 ml-2">
                  Line {backlink.line_number}
                </span>
              </div>

              {/* Source file path */}
              <div className="text-xs text-gray-500 mb-2 font-mono">
                {backlink.source_file}
              </div>

              {/* Context snippet */}
              <div className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-2 rounded border-l-2 border-blue-500">
                {highlightWikilink(backlink.snippet)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default BacklinksPanel;
