import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, AlertCircle, Book } from 'lucide-react';
import { apiClient } from '../services/api';
import TableOfContents from './TableOfContents';
import DocumentViewer from './DocumentViewer';
import SearchBar from './SearchBar';
import type { Document, TableOfContents as TOC } from '../types';

const DocumentViewerPage: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<Document | null>(null);
  const [toc, setToc] = useState<TOC | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tocExpanded, setTocExpanded] = useState(true);
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);

  useEffect(() => {
    if (documentId) {
      loadDocument();
      loadTOC();
    }
  }, [documentId]);

  const loadDocument = async () => {
    if (!documentId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getDocument(documentId);
      setDocument(data);
    } catch (err) {
      setError('Failed to load document');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadTOC = async () => {
    if (!documentId) return;

    try {
      const data = await apiClient.getTableOfContents(documentId);
      setToc(data);

      // Auto-select first section if available
      if (data.entries.length > 0) {
        setSelectedSectionId(data.entries[0].id);
      }
    } catch (err) {
      console.error('Failed to load TOC:', err);
    }
  };

  const handleSectionClick = (sectionId: string) => {
    setSelectedSectionId(sectionId);

    // On mobile, hide TOC after selection
    if (window.innerWidth < 768) {
      setTocExpanded(false);
    }
  };

  const handleSearchResultClick = (sectionId: string) => {
    setSelectedSectionId(sectionId);
    // On mobile, hide TOC when jumping to search result
    if (window.innerWidth < 768) {
      setTocExpanded(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center text-red-600">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error || 'Document not found'}</span>
        </div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 flex items-center text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to documents
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Compact Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </button>
          <div className="border-l border-gray-300 pl-4">
            <h1 className="text-lg font-bold text-gray-900">{document.title}</h1>
            <p className="text-xs text-gray-500">
              {document.version} • {document.page_count || '?'} pages
            </p>
          </div>
        </div>

        <button
          onClick={() => setTocExpanded(!tocExpanded)}
          className="lg:hidden flex items-center px-3 py-2 text-sm text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
        >
          <Book className="h-4 w-4 mr-1" />
          {tocExpanded ? 'Hide' : 'Show'} TOC
        </button>
      </div>

      {/* Main Layout: TOC on Left, Content on Right */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Table of Contents */}
        {toc && toc.entries.length > 0 && (
          <aside
            className={`${
              tocExpanded ? 'block' : 'hidden'
            } lg:block w-80 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto`}
          >
            <div className="p-4">
              <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center uppercase tracking-wide">
                <Book className="h-4 w-4 mr-2" />
                Table of Contents
              </h2>

              {/* Search Bar in TOC */}
              {documentId && (
                <div className="mb-4">
                  <SearchBar
                    documentId={documentId}
                    onResultClick={handleSearchResultClick}
                    className="w-full"
                  />
                </div>
              )}

              <TableOfContents
                entries={toc.entries}
                onSectionClick={handleSectionClick}
                activeSectionId={selectedSectionId}
              />
            </div>
          </aside>
        )}

        {/* Main Content Area - Full Width */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="w-full p-6">
            {documentId && (
              <DocumentViewer
                documentId={documentId}
                selectedSectionId={selectedSectionId}
                onSectionChange={setSelectedSectionId}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DocumentViewerPage;
