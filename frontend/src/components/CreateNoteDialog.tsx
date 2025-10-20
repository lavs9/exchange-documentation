import React, { useState } from 'react';
import { X, FileText, BookOpen, Link2 } from 'lucide-react';
import WikiLinkEditor from './WikiLinkEditor';

type NoteType = 'note' | 'reference';

interface CreateNoteDialogProps {
  open: boolean;
  onClose: () => void;
  documentId: string;
  version: string;
  selectedText?: string;
  sourceChapter?: string;
  onNoteCreated?: () => void;
}

/**
 * Dialog for creating a new note or reference.
 *
 * Features:
 * - Pre-fill with selected text
 * - Choose note type (note/reference)
 * - Option to insert [[wikilink]] in source chapter
 * - Use WikiLinkEditor for content
 */
const CreateNoteDialog: React.FC<CreateNoteDialogProps> = ({
  open,
  onClose,
  documentId,
  version,
  selectedText = '',
  sourceChapter,
  onNoteCreated
}) => {
  const [title, setTitle] = useState('');
  const [noteType, setNoteType] = useState<NoteType>('note');
  const [insertWikilink, setInsertWikilink] = useState(!!sourceChapter);
  const [content, setContent] = useState(
    selectedText ? `# ${title || 'Untitled'}\n\n${selectedText}\n\n` : '# Untitled\n\n'
  );
  const [tags, setTags] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update content heading when title changes
  React.useEffect(() => {
    if (title) {
      const lines = content.split('\n');
      if (lines[0].startsWith('# ')) {
        lines[0] = `# ${title}`;
        setContent(lines.join('\n'));
      }
    }
  }, [title]);

  // Initialize content when dialog opens
  React.useEffect(() => {
    if (open && selectedText) {
      setContent(`# ${title || 'Untitled'}\n\n${selectedText}\n\n`);
    }
  }, [open, selectedText]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      // Parse tags
      const tagArray = tags
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);

      // Prepare request body
      const requestBody = {
        title: title.trim(),
        content: content,
        doc_type: noteType,
        tags: tagArray,
        created_by: 'user', // TODO: Get from auth context
        link_to_source: insertWikilink ? sourceChapter : null
      };

      const response = await fetch(
        `http://localhost:8000/api/documents/${documentId}/versions/${version}/notes`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create note');
      }

      const createdNote = await response.json();
      console.log('Note created:', createdNote);

      // Reset form and close
      setTitle('');
      setContent('# Untitled\n\n');
      setTags('');
      setNoteType('note');
      setInsertWikilink(!!sourceChapter);

      if (onNoteCreated) {
        onNoteCreated();
      }

      onClose();
    } catch (err) {
      console.error('Error creating note:', err);
      setError(err instanceof Error ? err.message : 'Failed to create note');
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Create Note</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              disabled={saving}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Error message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                {error}
              </div>
            )}

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Order Validation Rules"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={saving}
              />
            </div>

            {/* Note Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type
              </label>
              <div className="flex gap-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="noteType"
                    value="note"
                    checked={noteType === 'note'}
                    onChange={(e) => setNoteType(e.target.value as NoteType)}
                    disabled={saving}
                  />
                  <FileText className="w-4 h-4 text-green-600" />
                  <span className="text-sm">Note</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="noteType"
                    value="reference"
                    checked={noteType === 'reference'}
                    onChange={(e) => setNoteType(e.target.value as NoteType)}
                    disabled={saving}
                  />
                  <BookOpen className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">Reference</span>
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Notes are personal annotations. References are guides or documentation.
              </p>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (optional)
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="orders, validation, rules (comma-separated)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={saving}
              />
            </div>

            {/* Insert Wikilink option */}
            {sourceChapter && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="insertWikilink"
                  checked={insertWikilink}
                  onChange={(e) => setInsertWikilink(e.target.checked)}
                  disabled={saving}
                />
                <label htmlFor="insertWikilink" className="text-sm text-gray-700 flex items-center gap-2">
                  <Link2 className="w-4 h-4 text-blue-600" />
                  Insert [[wikilink]] in source chapter
                </label>
              </div>
            )}

            {/* Content Editor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content
              </label>
              <WikiLinkEditor
                value={content}
                onChange={setContent}
                documentId={documentId}
                version={version}
                placeholder="Write your note with [[wikilinks]] to other documents..."
              />
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
                disabled={saving}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={saving}
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    Create {noteType === 'note' ? 'Note' : 'Reference'}
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default CreateNoteDialog;
