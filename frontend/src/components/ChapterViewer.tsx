/**
 * ChapterViewer Component
 *
 * Container component that toggles between read and edit modes.
 * - Default: Read mode with MarkdownRenderer
 * - Edit mode: TipTapEditor (lazy loaded)
 * - Handles save/cancel operations
 * - Draft recovery from localStorage
 * - Unsaved changes warning
 */
import React, { useState, useEffect, lazy, Suspense } from 'react';
import { Edit3, Save, X, AlertTriangle, Loader2 } from 'lucide-react';
import MarkdownRenderer from './MarkdownRenderer';

// Lazy load TipTapEditor to reduce initial bundle size
const TipTapEditor = lazy(() => import('./TipTapEditor'));

interface ChapterViewerProps {
  chapterId: string;
  documentId: string;
  version: string;
  initialContent: string;
  chapterTitle?: string;
  pageRange?: string;
  wordCount?: number;
  onSave: (content: string) => Promise<void>;
  onWikilinkClick?: (target: string, anchor?: string) => void;
}

type ViewMode = 'read' | 'edit';

const ChapterViewer: React.FC<ChapterViewerProps> = ({
  chapterId,
  documentId,
  version,
  initialContent,
  chapterTitle,
  pageRange,
  wordCount,
  onSave,
  onWikilinkClick
}) => {
  const [mode, setMode] = useState<ViewMode>('read');
  const [content, setContent] = useState(initialContent);
  const [editingContent, setEditingContent] = useState(initialContent);
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showDraftBanner, setShowDraftBanner] = useState(false);
  const [draftContent, setDraftContent] = useState<string | null>(null);

  const draftKey = `chapter-draft-${chapterId}`;
  const draftTimestampKey = `${draftKey}-timestamp`;

  // Check for draft on mount
  useEffect(() => {
    const draft = localStorage.getItem(draftKey);
    const draftTimestamp = localStorage.getItem(draftTimestampKey);

    if (draft && draftTimestamp) {
      const draftTime = new Date(draftTimestamp).getTime();
      const contentTime = new Date().getTime(); // Assume current time for saved content

      if (draft !== initialContent) {
        setDraftContent(draft);
        setShowDraftBanner(true);
      }
    }
  }, [chapterId, initialContent, draftKey, draftTimestampKey]);

  // Autosave to localStorage every 30 seconds
  useEffect(() => {
    if (mode === 'edit' && isDirty) {
      const autosaveInterval = setInterval(() => {
        localStorage.setItem(draftKey, editingContent);
        localStorage.setItem(draftTimestampKey, new Date().toISOString());
        console.log('Draft autosaved');
      }, 30000); // 30 seconds

      return () => clearInterval(autosaveInterval);
    }
  }, [mode, isDirty, editingContent, draftKey, draftTimestampKey]);

  // Warn before leaving page with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  const handleEditClick = () => {
    setEditingContent(content);
    setMode('edit');
    setIsDirty(false);
  };

  const handleCancelClick = () => {
    if (isDirty) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to discard them?'
      );
      if (!confirmed) return;
    }

    setMode('read');
    setEditingContent(content);
    setIsDirty(false);

    // Clear draft
    localStorage.removeItem(draftKey);
    localStorage.removeItem(draftTimestampKey);
  };

  const handleSaveClick = async () => {
    try {
      setSaving(true);
      await onSave(editingContent);

      // Update content and switch to read mode
      setContent(editingContent);
      setMode('read');
      setIsDirty(false);

      // Clear draft
      localStorage.removeItem(draftKey);
      localStorage.removeItem(draftTimestampKey);

      // Show success message (could use a toast library)
      console.log('Chapter saved successfully');
    } catch (error) {
      console.error('Failed to save chapter:', error);
      alert('Failed to save chapter. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleEditorChange = (newContent: string) => {
    setEditingContent(newContent);
    setIsDirty(newContent !== content);
  };

  const handleRestoreDraft = () => {
    if (draftContent) {
      setEditingContent(draftContent);
      setContent(draftContent);
      setShowDraftBanner(false);
      setMode('edit');
    }
  };

  const handleDiscardDraft = () => {
    localStorage.removeItem(draftKey);
    localStorage.removeItem(draftTimestampKey);
    setShowDraftBanner(false);
    setDraftContent(null);
  };

  return (
    <div className="chapter-viewer flex flex-col h-full">
      {/* Draft Recovery Banner */}
      {showDraftBanner && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-yellow-800">
                  Unsaved changes found
                </p>
                <p className="text-xs text-yellow-700 mt-1">
                  A draft from a previous session was found. Would you like to restore it?
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleRestoreDraft}
                className="px-3 py-1.5 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
              >
                Restore
              </button>
              <button
                onClick={handleDiscardDraft}
                className="px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header with Metadata and Actions */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex-1">
          {chapterTitle && (
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {chapterTitle}
            </h1>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            {pageRange && (
              <span>Pages: {pageRange}</span>
            )}
            {wordCount && (
              <span>Words: {wordCount.toLocaleString()}</span>
            )}
            {isDirty && mode === 'edit' && (
              <span className="text-orange-600 font-medium flex items-center gap-1">
                <span className="w-2 h-2 bg-orange-600 rounded-full"></span>
                Unsaved changes
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {mode === 'read' ? (
            <button
              onClick={handleEditClick}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              Edit Chapter
            </button>
          ) : (
            <>
              <button
                onClick={handleCancelClick}
                disabled={saving}
                className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
              <button
                onClick={handleSaveClick}
                disabled={saving || !isDirty}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {mode === 'read' ? (
          <MarkdownRenderer
            content={content}
            documentId={documentId}
            version={version}
            onWikilinkClick={onWikilinkClick}
          />
        ) : (
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            }
          >
            <TipTapEditor
              initialContent={editingContent}
              onChange={handleEditorChange}
              onSave={handleSaveClick}
              onCancel={handleCancelClick}
              documentId={documentId}
              version={version}
            />
          </Suspense>
        )}
      </div>

      {/* Keyboard Shortcuts Hint (shown in edit mode) */}
      {mode === 'edit' && (
        <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500 flex items-center justify-between">
          <div className="flex gap-4">
            <span><kbd className="px-2 py-1 bg-gray-100 rounded">Cmd+S</kbd> Save</span>
            <span><kbd className="px-2 py-1 bg-gray-100 rounded">Esc</kbd> Cancel</span>
            <span><kbd className="px-2 py-1 bg-gray-100 rounded">/</kbd> Commands</span>
          </div>
          <span>Draft autosaves every 30 seconds</span>
        </div>
      )}
    </div>
  );
};

export default ChapterViewer;
