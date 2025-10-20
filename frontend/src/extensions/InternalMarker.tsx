/**
 * InternalMarker Extension for TipTap
 *
 * Custom node for internal markers that are preserved during version diffs.
 * Renders as a lightly styled block with minimal interference to content visibility.
 *
 * Features:
 * - Contains block-level content (paragraphs, headings, lists, etc.)
 * - Serializes to <!-- MANUAL:START --> ... <!-- MANUAL:END --> format
 * - Light background styling to identify marker blocks
 * - Cannot be nested inside other markers
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import React from 'react';
import { NodeViewWrapper } from '@tiptap/react';

// Define the node attributes
export interface InternalMarkerAttributes {
  author: string;
  timestamp: string;
  type: string;
  id: string;
}

// React component for rendering the marker in the editor
const InternalMarkerComponent = ({ node, updateAttributes, deleteNode, editor }: any) => {
  const { author, timestamp, type } = node.attrs;

  // Format timestamp for display
  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleString()
    : new Date().toLocaleString();

  return (
    <NodeViewWrapper className="internal-marker-wrapper">
      <div
        className="internal-marker bg-blue-50 border-l-4 border-blue-300 rounded-r p-4 my-4 relative"
        data-marker-type={type}
      >
        {/* Marker Label */}
        <div className="absolute top-2 right-2 flex items-center gap-2">
          <span className="text-xs font-semibold text-blue-600 bg-white px-2 py-1 rounded shadow-sm">
            Internal Note
          </span>
          <button
            onClick={deleteNode}
            className="text-xs text-red-600 hover:text-red-800 bg-white px-2 py-1 rounded shadow-sm"
            contentEditable={false}
          >
            ✕
          </button>
        </div>

        {/* Metadata */}
        <div className="text-xs text-gray-600 mb-3 pr-24">
          <span>By {author}</span>
          <span className="mx-2">•</span>
          <span>{formattedTime}</span>
        </div>

        {/* Editable Content */}
        <div
          className="internal-marker-content"
          data-node-view-content
          suppressContentEditableWarning
        />
      </div>
    </NodeViewWrapper>
  );
};

export const InternalMarker = Node.create({
  name: 'internalMarker',

  group: 'block',

  content: 'block+',

  defining: true,

  addAttributes() {
    return {
      author: {
        default: 'user',
        parseHTML: element => element.getAttribute('data-author'),
        renderHTML: attributes => ({
          'data-author': attributes.author,
        }),
      },
      timestamp: {
        default: new Date().toISOString(),
        parseHTML: element => element.getAttribute('data-timestamp'),
        renderHTML: attributes => ({
          'data-timestamp': attributes.timestamp,
        }),
      },
      type: {
        default: 'note',
        parseHTML: element => element.getAttribute('data-type'),
        renderHTML: attributes => ({
          'data-type': attributes.type,
        }),
      },
      id: {
        default: `marker-${Date.now()}`,
        parseHTML: element => element.getAttribute('data-id'),
        renderHTML: attributes => ({
          'data-id': attributes.id,
        }),
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="internal-marker"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(HTMLAttributes, {
        'data-type': 'internal-marker',
        class: 'internal-marker',
      }),
      0, // 0 means "render children here"
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(InternalMarkerComponent as any);
  },

  addCommands() {
    return {
      setInternalMarker:
        (attributes?: Partial<InternalMarkerAttributes>) =>
        ({ commands }: any) => {
          return commands.wrapIn(this.name, {
            author: attributes?.author || 'user',
            timestamp: attributes?.timestamp || new Date().toISOString(),
            type: attributes?.type || 'note',
            id: attributes?.id || `marker-${Date.now()}`,
          });
        },
      toggleInternalMarker:
        (attributes?: Partial<InternalMarkerAttributes>) =>
        ({ commands }: any) => {
          return commands.toggleWrap(this.name, {
            author: attributes?.author || 'user',
            timestamp: attributes?.timestamp || new Date().toISOString(),
            type: attributes?.type || 'note',
            id: attributes?.id || `marker-${Date.now()}`,
          });
        },
    } as any;
  },

  addKeyboardShortcuts() {
    return {
      // Optional: Add keyboard shortcut for toggling marker
      'Mod-Shift-m': () => (this.editor.commands as any).toggleInternalMarker(),
    };
  },
});

export default InternalMarker;
