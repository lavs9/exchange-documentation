/**
 * DocumentViewerV2 Component
 *
 * Updated document viewer using ChapterViewer with TipTap editor.
 * Replaces the old DocumentViewer with improved editing capabilities.
 */
import React, { useState, useEffect } from 'react';
import { Loader2, AlertCircle, FileText } from 'lucide-react';
import { apiClient } from '../services/api';
import ChapterViewer from './ChapterViewer';
import BacklinksPanel from './BacklinksPanel';
import CreateNoteDialog from './CreateNoteDialog';
import type { Section } from '../types';

interface DocumentViewerV2Props {
  documentId: string;
  selectedSectionId?: string | null;
  onSectionChange?: (sectionId: string) => void;
  showBacklinks?: boolean;
}

const DocumentViewerV2: React.FC<DocumentViewerV2Props> = ({
  documentId,
  selectedSectionId,
  onSectionChange,
  showBacklinks = true,
}) => {
  const [section, setSection] = useState<Section | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState('');
  const [showCreateNoteDialog, setShowCreateNoteDialog] = useState(false);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; text: string } | null>(null);

  useEffect(() => {
    if (selectedSectionId) {
      loadSection(selectedSectionId);
    } else {
      setSection(null);
      setLoading(false);
    }
  }, [selectedSectionId]);

  const loadSection = async (sectionId: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(`/documents/${documentId}/sections/${sectionId}`);
      setSection(response.data);
    } catch (err) {
      console.error('Error loading section:', err);
      setError('Failed to load section');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveChapter = async (content: string) => {
    if (!section) return;

    try {
      await apiClient.put(
        `/documents/${documentId}/sections/${section.id}`,
        { content }
      );

      // Reload section to get updated content
      await loadSection(section.id);
    } catch (err) {
      console.error('Error saving chapter:', err);
      throw new Error('Failed to save chapter');
    }
  };

  const handleWikilinkClick = (target: string, anchor?: string) => {
    console.log('Wikilink clicked:', target, anchor);
    // TODO: Implement navigation to target document/chapter
    // This would integrate with your routing system
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 0) {
      e.preventDefault();
      setContextMenu({
        x: e.clientX,
        y: e.clientY,
        text: text
      });
      setSelectedText(text);
    }
  };

  const handleCreateNoteFromContext = () => {
    setContextMenu(null);
    setShowCreateNoteDialog(true);
  };

  const handleNoteCreated = () => {
    if (selectedSectionId) {
      loadSection(selectedSectionId);
    }
  };

  // Close context menu when clicking elsewhere
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    if (contextMenu) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!section) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-gray-500">
          <FileText className="h-12 w-12 mx-auto mb-4" />
          <p>Select a chapter to view</p>
        </div>
      </div>
    );
  }

  // Extract filename from file_path for backlinks
  const chapterFilename = section.file_path
    ? section.file_path.split('/').pop()?.replace('.md', '') || section.id
    : section.id;

  return (
    <div className="flex h-full" onContextMenu={handleContextMenu}>
      {/* Main Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <ChapterViewer
          chapterId={section.id}
          documentId={documentId}
          version="v6.1" // TODO: Get from document context
          initialContent={section.content}
          chapterTitle={section.title}
          pageRange={section.page_number ? `${section.page_number}` : undefined}
          wordCount={section.content.split(/\s+/).length}
          onSave={handleSaveChapter}
          onWikilinkClick={handleWikilinkClick}
        />
      </div>

      {/* Backlinks Panel */}
      {showBacklinks && (
        <BacklinksPanel
          documentId={documentId}
          version="v6.1" // TODO: Get from document context
          filename={chapterFilename}
          className="w-96 overflow-y-auto border-l border-gray-200"
        />
      )}

      {/* Context Menu for Creating Notes */}
      {contextMenu && (
        <div
          className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg py-1"
          style={{
            top: `${contextMenu.y}px`,
            left: `${contextMenu.x}px`
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={handleCreateNoteFromContext}
            className="w-full px-4 py-2 text-left hover:bg-blue-50 flex items-center gap-2 text-sm"
          >
            <FileText className="w-4 h-4 text-blue-600" />
            <span>Create Note from Selection</span>
          </button>
        </div>
      )}

      {/* Create Note Dialog */}
      <CreateNoteDialog
        open={showCreateNoteDialog}
        onClose={() => setShowCreateNoteDialog(false)}
        documentId={documentId}
        version="v6.1" // TODO: Get from document context
        selectedText={selectedText}
        sourceChapter={section.id}
        onNoteCreated={handleNoteCreated}
      />
    </div>
  );
};

export default DocumentViewerV2;
