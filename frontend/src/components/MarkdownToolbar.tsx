/**
 * MarkdownToolbar Component
 *
 * Lightweight toolbar for inserting common markdown syntax
 * No external dependencies - uses only React and Tailwind
 */
import React from 'react';
import {
  Bold,
  Italic,
  Code,
  FileCode,
  Link,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Heading3,
  Quote,
  Minus,
} from 'lucide-react';

export interface MarkdownAction {
  type: 'insert' | 'wrap';
  syntax: string;
  endSyntax?: string;
  placeholder?: string;
  newLine?: boolean;
}

interface MarkdownToolbarProps {
  onAction: (action: MarkdownAction) => void;
}

interface ToolbarButton {
  icon: React.ReactNode;
  label: string;
  action: MarkdownAction;
}

const MarkdownToolbar: React.FC<MarkdownToolbarProps> = ({ onAction }) => {
  const buttons: ToolbarButton[] = [
    {
      icon: <Bold className="h-4 w-4" />,
      label: 'Bold (Ctrl+B)',
      action: { type: 'wrap', syntax: '**', endSyntax: '**', placeholder: 'bold text' },
    },
    {
      icon: <Italic className="h-4 w-4" />,
      label: 'Italic (Ctrl+I)',
      action: { type: 'wrap', syntax: '*', endSyntax: '*', placeholder: 'italic text' },
    },
    {
      icon: <Code className="h-4 w-4" />,
      label: 'Inline Code',
      action: { type: 'wrap', syntax: '`', endSyntax: '`', placeholder: 'code' },
    },
    {
      icon: <FileCode className="h-4 w-4" />,
      label: 'Code Block',
      action: {
        type: 'wrap',
        syntax: '```\n',
        endSyntax: '\n```',
        placeholder: 'code',
        newLine: true,
      },
    },
    {
      icon: <Link className="h-4 w-4" />,
      label: 'Link (Ctrl+K)',
      action: { type: 'wrap', syntax: '[', endSyntax: '](url)', placeholder: 'link text' },
    },
    {
      icon: <Heading1 className="h-4 w-4" />,
      label: 'Heading 1',
      action: { type: 'insert', syntax: '# ', placeholder: 'Heading 1', newLine: true },
    },
    {
      icon: <Heading2 className="h-4 w-4" />,
      label: 'Heading 2',
      action: { type: 'insert', syntax: '## ', placeholder: 'Heading 2', newLine: true },
    },
    {
      icon: <Heading3 className="h-4 w-4" />,
      label: 'Heading 3',
      action: { type: 'insert', syntax: '### ', placeholder: 'Heading 3', newLine: true },
    },
    {
      icon: <List className="h-4 w-4" />,
      label: 'Unordered List',
      action: { type: 'insert', syntax: '- ', placeholder: 'list item', newLine: true },
    },
    {
      icon: <ListOrdered className="h-4 w-4" />,
      label: 'Ordered List',
      action: { type: 'insert', syntax: '1. ', placeholder: 'list item', newLine: true },
    },
    {
      icon: <Quote className="h-4 w-4" />,
      label: 'Blockquote',
      action: { type: 'insert', syntax: '> ', placeholder: 'quote', newLine: true },
    },
    {
      icon: <Minus className="h-4 w-4" />,
      label: 'Horizontal Rule',
      action: { type: 'insert', syntax: '\n---\n', newLine: true },
    },
  ];

  return (
    <div className="sticky top-0 z-10 bg-gray-100 border-b border-gray-300 px-3 py-2 flex flex-wrap gap-1">
      {buttons.map((button, index) => (
        <button
          key={index}
          onClick={() => onAction(button.action)}
          className="p-2 text-gray-700 hover:bg-gray-200 hover:text-gray-900 rounded transition-colors"
          title={button.label}
          type="button"
        >
          {button.icon}
        </button>
      ))}
    </div>
  );
};

export default MarkdownToolbar;
