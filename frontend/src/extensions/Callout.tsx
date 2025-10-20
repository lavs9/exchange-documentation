/**
 * Callout Extension for TipTap
 *
 * Custom node for visual callout blocks (info, warning, tip, note).
 * Provides styled, colored blocks for highlighting important information.
 *
 * Features:
 * - Multiple callout types: info, warning, tip, note, important
 * - Distinct styling with icons and colors
 * - Serializes to Obsidian-style > [!type] blockquote syntax
 * - Can contain block-level content
 * - Type can be changed via commands
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import React from 'react';
import { NodeViewWrapper } from '@tiptap/react';
import { Info, AlertCircle, Lightbulb, FileText } from 'lucide-react';

export type CalloutType = 'info' | 'warning' | 'tip' | 'note' | 'important';

export interface CalloutAttributes {
  type: CalloutType;
}

// Callout styling configuration
const calloutConfig: Record<CalloutType, {
  bgColor: string;
  borderColor: string;
  textColor: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}> = {
  info: {
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-800',
    icon: Info,
    label: 'Info',
  },
  important: {
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-800',
    icon: Lightbulb,
    label: 'Important',
  },
  warning: {
    bgColor: 'bg-orange-100',
    borderColor: 'border-orange-500',
    textColor: 'text-orange-800',
    icon: AlertCircle,
    label: 'Warning',
  },
  tip: {
    bgColor: 'bg-green-100',
    borderColor: 'border-green-500',
    textColor: 'text-green-800',
    icon: Lightbulb,
    label: 'Tip',
  },
  note: {
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-500',
    textColor: 'text-gray-800',
    icon: FileText,
    label: 'Note',
  },
};

// React component for rendering the callout in the editor
const CalloutComponent = ({ node, updateAttributes, deleteNode }: any) => {
  const calloutType: CalloutType = node.attrs.type || 'info';
  const config = calloutConfig[calloutType];
  const Icon = config.icon;

  const handleTypeChange = (newType: CalloutType) => {
    updateAttributes({ type: newType });
  };

  return (
    <NodeViewWrapper className="callout-wrapper">
      <div
        className={`callout ${config.bgColor} border-l-4 ${config.borderColor} rounded-r-lg p-4 my-4 relative`}
        data-callout-type={calloutType}
      >
        {/* Type Selector and Delete Button */}
        <div className="absolute top-2 right-2 flex items-center gap-2">
          <select
            value={calloutType}
            onChange={(e) => handleTypeChange(e.target.value as CalloutType)}
            className="text-xs px-2 py-1 rounded bg-white border border-gray-300 shadow-sm"
            contentEditable={false}
          >
            <option value="info">Info</option>
            <option value="important">Important</option>
            <option value="warning">Warning</option>
            <option value="tip">Tip</option>
            <option value="note">Note</option>
          </select>
          <button
            onClick={deleteNode}
            className="text-xs text-red-600 hover:text-red-800 bg-white px-2 py-1 rounded shadow-sm"
            contentEditable={false}
          >
            ✕
          </button>
        </div>

        {/* Callout Header */}
        <div className="flex items-start gap-3 mb-2">
          <Icon className={`w-5 h-5 ${config.textColor} flex-shrink-0 mt-0.5`} />
          <div className={`font-semibold ${config.textColor}`}>
            {config.label}
          </div>
        </div>

        {/* Editable Content */}
        <div
          className="callout-content pl-8"
          data-node-view-content
          suppressContentEditableWarning
        />
      </div>
    </NodeViewWrapper>
  );
};

export const Callout = Node.create({
  name: 'callout',

  group: 'block',

  content: 'block+',

  defining: true,

  addAttributes() {
    return {
      type: {
        default: 'info',
        parseHTML: element => element.getAttribute('data-callout-type') || 'info',
        renderHTML: attributes => ({
          'data-callout-type': attributes.type,
        }),
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="callout"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(HTMLAttributes, {
        'data-type': 'callout',
        class: 'callout',
      }),
      0, // 0 means "render children here"
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(CalloutComponent as any);
  },

  addCommands() {
    return {
      setCallout:
        (attributes?: Partial<CalloutAttributes>) =>
        ({ commands }: any) => {
          return commands.wrapIn(this.name, {
            type: attributes?.type || 'info',
          });
        },
      toggleCallout:
        (attributes?: Partial<CalloutAttributes>) =>
        ({ commands }: any) => {
          return commands.toggleWrap(this.name, {
            type: attributes?.type || 'info',
          });
        },
      updateCalloutType:
        (type: CalloutType) =>
        ({ commands }: any) => {
          return commands.updateAttributes(this.name, { type });
        },
    } as any;
  },

  addKeyboardShortcuts() {
    return {
      // Optional: Add keyboard shortcut for toggling callout
      'Mod-Shift-c': () => (this.editor.commands as any).toggleCallout(),
    };
  },
});

export default Callout;
