/**
 * MarkdownEditor Component
 *
 * Live markdown editor with split-pane view: editor on left, preview on right
 * Supports editing and saving section content
 */
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import { Save, X, Eye, EyeOff, Loader2, Check } from 'lucide-react';
import MarkdownToolbar, { MarkdownAction } from './MarkdownToolbar';
import SaveEditDialog from './SaveEditDialog';

// Import highlight.js styles
import 'highlight.js/styles/github-dark.css';

type SaveType = 'direct' | 'manual';
type MarkerType = 'callout' | 'note' | 'warning' | 'tip' | 'code';

interface MarkdownEditorProps {
  content: string;
  onSave: (newContent: string) => Promise<void>;
  onCancel: () => void;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  content,
  onSave,
  onCancel,
}) => {
  const [editedContent, setEditedContent] = useState(content);
  const [showPreview, setShowPreview] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setEditedContent(content);
    setHasChanges(false);
  }, [content]);

  useEffect(() => {
    setHasChanges(editedContent !== content);
  }, [editedContent, content]);

  const handleSaveClick = () => {
    if (!hasChanges) return;
    setShowSaveDialog(true);
  };

  const handleSaveWithType = async (saveType: SaveType, markerType?: MarkerType) => {
    try {
      setSaving(true);

      let finalContent = editedContent;

      if (saveType === 'manual' && markerType) {
        // Find the diff between original and edited content
        const diff = findContentDiff(content, editedContent);

        if (diff) {
          const timestamp = new Date().toISOString();
          const user = 'user'; // TODO: Get from auth context

          // Create callout format based on marker type
          const calloutIcon = getCalloutIcon(markerType);
          const calloutTitle = getCalloutTitle(markerType);

          const manualMarker = `<!-- MANUAL:START:${user}:${timestamp}:${markerType} -->
> [!${markerType}] ${calloutIcon}
> **${calloutTitle}**: ${diff.addedText}
<!-- MANUAL:END -->`;

          // Insert the manual marker at the position where content was added
          finalContent = diff.beforeText + manualMarker + diff.afterText;
        }
      }

      await onSave(finalContent);
      setSaved(true);
      setHasChanges(false);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error('Failed to save:', err);
    } finally {
      setSaving(false);
    }
  };

  // Helper function to find what content was added
  const findContentDiff = (original: string, edited: string): { beforeText: string; addedText: string; afterText: string } | null => {
    if (original === edited) return null;

    // Simple approach: find where they start differing
    let startDiff = 0;
    while (startDiff < original.length && startDiff < edited.length && original[startDiff] === edited[startDiff]) {
      startDiff++;
    }

    // Find where they stop differing (from the end)
    let endDiffOriginal = original.length;
    let endDiffEdited = edited.length;
    while (
      endDiffOriginal > startDiff &&
      endDiffEdited > startDiff &&
      original[endDiffOriginal - 1] === edited[endDiffEdited - 1]
    ) {
      endDiffOriginal--;
      endDiffEdited--;
    }

    const beforeText = edited.substring(0, startDiff);
    const addedText = edited.substring(startDiff, endDiffEdited);
    const afterText = edited.substring(endDiffEdited);

    return { beforeText, addedText, afterText };
  };

  // Helper function to get callout icon based on marker type
  const getCalloutIcon = (type: MarkerType): string => {
    const icons: Record<MarkerType, string> = {
      callout: '💡',
      note: '📝',
      warning: '⚠️',
      tip: '💡',
      code: '💻'
    };
    return icons[type] || '💡';
  };

  // Helper function to get callout title based on marker type
  const getCalloutTitle = (type: MarkerType): string => {
    const titles: Record<MarkerType, string> = {
      callout: 'Important Note',
      note: 'Note',
      warning: 'Warning',
      tip: 'Tip',
      code: 'Code Example'
    };
    return titles[type] || 'Note';
  };

  const handleCancel = () => {
    if (hasChanges) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to cancel?'
      );
      if (!confirmed) return;
    }
    onCancel();
  };

  // Remove page references and YAML frontmatter from content for preview
  const cleanContent = (content: string): string => {
    // Remove YAML frontmatter (--- ... ---)
    let cleaned = content.replace(/^---\s*\n[\s\S]*?\n---\s*\n/m, '');
    // Remove page references with backticks: `[p.13]`
    cleaned = cleaned.replace(/`\[p\.\d+\]`/g, '');
    // Remove page references without backticks: [p.13]
    cleaned = cleaned.replace(/\[p\.\d+\]/g, '');
    return cleaned;
  };

  // Handle markdown toolbar actions
  const handleToolbarAction = (action: MarkdownAction) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = editedContent.substring(start, end);
    const beforeText = editedContent.substring(0, start);
    const afterText = editedContent.substring(end);

    let newText = '';
    let cursorPos = start;

    if (action.type === 'wrap') {
      // Wrap selected text or insert with placeholder
      const textToWrap = selectedText || action.placeholder || '';
      newText = beforeText + action.syntax + textToWrap + (action.endSyntax || '') + afterText;

      // Position cursor at end of wrapped text (before end syntax)
      cursorPos = start + action.syntax.length + textToWrap.length;

      // If no text was selected, select the placeholder for easy editing
      if (!selectedText && action.placeholder) {
        setTimeout(() => {
          textarea.focus();
          textarea.setSelectionRange(
            start + action.syntax.length,
            start + action.syntax.length + action.placeholder.length
          );
        }, 0);
      }
    } else {
      // Insert syntax (for headings, lists, etc.)
      const prefix = action.newLine && beforeText && !beforeText.endsWith('\n') ? '\n' : '';
      const textToInsert = selectedText || action.placeholder || '';
      newText = beforeText + prefix + action.syntax + textToInsert + afterText;

      // Position cursor after syntax
      cursorPos = start + prefix.length + action.syntax.length + textToInsert.length;

      // If no text was selected, select the placeholder
      if (!selectedText && action.placeholder) {
        setTimeout(() => {
          textarea.focus();
          textarea.setSelectionRange(
            start + prefix.length + action.syntax.length,
            start + prefix.length + action.syntax.length + action.placeholder.length
          );
        }, 0);
      }
    }

    setEditedContent(newText);

    // Restore focus and cursor position if no placeholder selection
    if (selectedText || !action.placeholder) {
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(cursorPos, cursorPos);
      }, 0);
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const isMod = e.metaKey || e.ctrlKey;

    if (isMod && e.key === 'b') {
      e.preventDefault();
      handleToolbarAction({ type: 'wrap', syntax: '**', endSyntax: '**', placeholder: 'bold text' });
    } else if (isMod && e.key === 'i') {
      e.preventDefault();
      handleToolbarAction({ type: 'wrap', syntax: '*', endSyntax: '*', placeholder: 'italic text' });
    } else if (isMod && e.key === 'k') {
      e.preventDefault();
      handleToolbarAction({ type: 'wrap', syntax: '[', endSyntax: '](url)', placeholder: 'link text' });
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center px-3 py-1.5 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-100"
          >
            {showPreview ? (
              <>
                <EyeOff className="h-4 w-4 mr-1" />
                Hide Preview
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-1" />
                Show Preview
              </>
            )}
          </button>
          {hasChanges && (
            <span className="text-xs text-orange-600 font-medium">
              • Unsaved changes
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCancel}
            className="flex items-center px-3 py-1.5 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-100"
          >
            <X className="h-4 w-4 mr-1" />
            Cancel
          </button>
          <button
            onClick={handleSaveClick}
            disabled={!hasChanges || saving}
            className={`flex items-center px-3 py-1.5 text-sm text-white rounded-md ${
              hasChanges && !saving
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Saving...
              </>
            ) : saved ? (
              <>
                <Check className="h-4 w-4 mr-1" />
                Saved
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-1" />
                Save
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor & Preview Panes */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor Pane */}
        <div className={`${showPreview ? 'w-1/2' : 'w-full'} border-r border-gray-200 flex flex-col`}>
          <div className="px-4 py-2 bg-gray-100 border-b border-gray-200">
            <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
              Markdown Editor
            </h3>
          </div>
          <MarkdownToolbar onAction={handleToolbarAction} />
          <textarea
            ref={textareaRef}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 w-full p-4 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
            placeholder="Enter markdown content..."
            spellCheck={false}
          />
        </div>

        {/* Preview Pane */}
        {showPreview && (
          <div className="w-1/2 flex flex-col">
            <div className="px-4 py-2 bg-gray-100 border-b border-gray-200">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                Live Preview
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-white">
              <article className="prose prose-slate max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight, rehypeRaw]}
                  components={{
                    // Responsive tables
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-6">
                        <table className="min-w-full divide-y divide-gray-300 border border-gray-300">
                          {children}
                        </table>
                      </div>
                    ),
                    thead: ({ children }) => (
                      <thead className="bg-gray-50">{children}</thead>
                    ),
                    th: ({ children }) => (
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider border-b border-gray-300">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="px-4 py-3 text-sm text-gray-700 border-b border-gray-200">
                        {children}
                      </td>
                    ),
                    // Enhanced code blocks
                    code: ({ node, inline, className, children, ...props }) => {
                      if (!inline) {
                        return (
                          <pre className={className}>
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        );
                      }
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {cleanContent(editedContent)}
                </ReactMarkdown>
              </article>
            </div>
          </div>
        )}
      </div>

      {/* Save Dialog */}
      <SaveEditDialog
        open={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSave={handleSaveWithType}
        editedContent={editedContent}
      />
    </div>
  );
};

export default MarkdownEditor;
