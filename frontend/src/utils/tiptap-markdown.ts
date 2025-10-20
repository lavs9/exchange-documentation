/**
 * TipTap Markdown Serializer/Parser
 *
 * Converts between TipTap JSON and custom markdown format.
 * Handles:
 * - Internal markers (<!-- MANUAL:START --> ... <!-- MANUAL:END -->)
 * - Callout blocks (> [!type])
 * - Wikilinks ([[target]])
 * - Standard markdown (headings, lists, tables, code blocks)
 */

import { JSONContent } from '@tiptap/core';

export interface ManualMarker {
  id: string;
  author: string;
  timestamp: string;
  type: string;
  content: string;
}

/**
 * Extract manual markers from markdown
 */
export const extractManualMarkers = (markdown: string): ManualMarker[] => {
  const markers: ManualMarker[] = [];
  const regex = /<!--\s*MANUAL:START:([^:]+):([^:]+):([^:]+)\s*-->([\s\S]*?)<!--\s*MANUAL:END\s*-->/g;

  let match;
  while ((match = regex.exec(markdown)) !== null) {
    markers.push({
      id: `marker-${markers.length}`,
      author: match[1],
      timestamp: match[2],
      type: match[3],
      content: match[4].trim()
    });
  }

  return markers;
};

/**
 * Parse markdown to TipTap JSON
 * This is a simplified parser - for production, consider using a library like remark
 */
export const parseMarkdown = (markdown: string): JSONContent => {
  const lines = markdown.split('\n');
  const content: JSONContent[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip empty lines at start
    if (!line.trim() && content.length === 0) {
      i++;
      continue;
    }

    // Manual markers
    if (line.includes('<!-- MANUAL:START')) {
      const markerMatch = line.match(/<!--\s*MANUAL:START:([^:]+):([^:]+):([^:]+)\s*-->/);
      if (markerMatch) {
        const [, author, timestamp, type] = markerMatch;
        const markerContent: string[] = [];
        i++;

        while (i < lines.length && !lines[i].includes('<!-- MANUAL:END')) {
          markerContent.push(lines[i]);
          i++;
        }

        content.push({
          type: 'internalMarker',
          attrs: {
            author,
            timestamp,
            type,
            id: `marker-${Date.now()}`
          },
          content: parseMarkdown(markerContent.join('\n')).content
        });
        i++;
        continue;
      }
    }

    // Callout blocks (blockquotes with [!type])
    if (line.startsWith('> [!')) {
      const calloutMatch = line.match(/>\s*\[!(\w+)\]/);
      if (calloutMatch) {
        const calloutType = calloutMatch[1].toLowerCase();
        const calloutLines: string[] = [];
        i++;

        while (i < lines.length && lines[i].startsWith('>')) {
          calloutLines.push(lines[i].replace(/^>\s?/, ''));
          i++;
        }

        content.push({
          type: 'callout',
          attrs: {
            type: calloutType
          },
          content: parseMarkdown(calloutLines.join('\n')).content
        });
        continue;
      }
    }

    // Headings
    if (line.startsWith('#')) {
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2];

        content.push({
          type: 'heading',
          attrs: { level },
          content: parseInlineContent(text)
        });
        i++;
        continue;
      }
    }

    // Code blocks
    if (line.startsWith('```')) {
      const language = line.slice(3).trim() || null;
      const codeLines: string[] = [];
      i++;

      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }

      content.push({
        type: 'codeBlock',
        attrs: { language },
        content: [
          {
            type: 'text',
            text: codeLines.join('\n')
          }
        ]
      });
      i++;
      continue;
    }

    // Bullet lists
    if (line.match(/^[\s]*[-*+]\s+/)) {
      const listItems: JSONContent[] = [];

      while (i < lines.length && lines[i].match(/^[\s]*[-*+]\s+/)) {
        const itemText = lines[i].replace(/^[\s]*[-*+]\s+/, '');
        listItems.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineContent(itemText)
            }
          ]
        });
        i++;
      }

      content.push({
        type: 'bulletList',
        content: listItems
      });
      continue;
    }

    // Numbered lists
    if (line.match(/^[\s]*\d+\.\s+/)) {
      const listItems: JSONContent[] = [];

      while (i < lines.length && lines[i].match(/^[\s]*\d+\.\s+/)) {
        const itemText = lines[i].replace(/^[\s]*\d+\.\s+/, '');
        listItems.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineContent(itemText)
            }
          ]
        });
        i++;
      }

      content.push({
        type: 'orderedList',
        content: listItems
      });
      continue;
    }

    // Paragraphs
    if (line.trim()) {
      const paragraphLines: string[] = [line];
      i++;

      while (i < lines.length && lines[i].trim() && !lines[i].match(/^[#>`\-*+]|^\d+\./)) {
        paragraphLines.push(lines[i]);
        i++;
      }

      content.push({
        type: 'paragraph',
        content: parseInlineContent(paragraphLines.join(' '))
      });
      continue;
    }

    i++;
  }

  return {
    type: 'doc',
    content: content.length > 0 ? content : [{ type: 'paragraph' }]
  };
};

/**
 * Parse inline content (bold, italic, links, wikilinks, code)
 */
const parseInlineContent = (text: string): JSONContent[] => {
  if (!text) return [{ type: 'text', text: '' }];

  const content: JSONContent[] = [];
  let remaining = text;

  // Simple regex-based parsing (for production, use a proper markdown parser)
  const inlinePatterns = [
    { regex: /\[\[([^\]]+)\]\]/g, type: 'wikilink' }, // [[wikilink]]
    { regex: /\[([^\]]+)\]\(([^)]+)\)/g, type: 'link' }, // [text](url)
    { regex: /\*\*([^*]+)\*\*/g, type: 'bold' }, // **bold**
    { regex: /\*([^*]+)\*/g, type: 'italic' }, // *italic*
    { regex: /`([^`]+)`/g, type: 'code' }, // `code`
  ];

  // For simplicity, just return text node
  // A full implementation would parse all inline styles
  content.push({
    type: 'text',
    text: remaining
  });

  return content;
};

/**
 * Serialize TipTap JSON to markdown
 */
export const serializeToMarkdown = (json: JSONContent): string => {
  if (!json.content) return '';

  return json.content.map(node => serializeNode(node)).join('\n\n');
};

/**
 * Serialize a single TipTap node to markdown
 */
const serializeNode = (node: JSONContent, indent = ''): string => {
  switch (node.type) {
    case 'heading':
      const level = node.attrs?.level || 1;
      const headingText = serializeContent(node.content || []);
      return `${'#'.repeat(level)} ${headingText}`;

    case 'paragraph':
      return indent + serializeContent(node.content || []);

    case 'codeBlock':
      const language = node.attrs?.language || '';
      const code = node.content?.[0]?.text || '';
      return `\`\`\`${language}\n${code}\n\`\`\``;

    case 'bulletList':
      return (node.content || [])
        .map(item => serializeNode(item, indent + '- '))
        .join('\n');

    case 'orderedList':
      return (node.content || [])
        .map((item, idx) => serializeNode(item, indent + `${idx + 1}. `))
        .join('\n');

    case 'listItem':
      const itemContent = (node.content || [])
        .map(child => {
          if (child.type === 'paragraph') {
            return serializeContent(child.content || []);
          }
          return serializeNode(child, indent + '  ');
        })
        .join('\n');
      return indent + itemContent;

    case 'blockquote':
      return (node.content || [])
        .map(child => '> ' + serializeNode(child))
        .join('\n');

    case 'internalMarker':
      const { author = 'user', timestamp = new Date().toISOString(), type = 'note' } = node.attrs || {};
      const markerContent = (node.content || [])
        .map(child => serializeNode(child))
        .join('\n\n');
      return `<!-- MANUAL:START:${author}:${timestamp}:${type} -->\n${markerContent}\n<!-- MANUAL:END -->`;

    case 'callout':
      const calloutType = node.attrs?.type || 'info';
      const calloutContent = (node.content || [])
        .map(child => '> ' + serializeNode(child))
        .join('\n');
      return `> [!${calloutType}]\n${calloutContent}`;

    case 'table':
      return serializeTable(node);

    case 'horizontalRule':
      return '---';

    case 'hardBreak':
      return '  \n';

    default:
      // Unknown node type, try to serialize content
      if (node.content) {
        return (node.content || []).map(child => serializeNode(child, indent)).join('');
      }
      return '';
  }
};

/**
 * Serialize inline content (text with marks)
 */
const serializeContent = (content: JSONContent[]): string => {
  return content.map(node => {
    if (node.type === 'text') {
      let text = node.text || '';
      const marks = node.marks || [];

      // Apply marks in order
      for (const mark of marks) {
        switch (mark.type) {
          case 'bold':
            text = `**${text}**`;
            break;
          case 'italic':
            text = `*${text}*`;
            break;
          case 'code':
            text = `\`${text}\``;
            break;
          case 'link':
            const href = mark.attrs?.href || '';
            text = `[${text}](${href})`;
            break;
          case 'wikilink':
            const target = mark.attrs?.target || text;
            text = `[[${target}]]`;
            break;
        }
      }

      return text;
    }

    if (node.type === 'hardBreak') {
      return '  \n';
    }

    return serializeNode(node);
  }).join('');
};

/**
 * Serialize table to markdown
 */
const serializeTable = (table: JSONContent): string => {
  const rows = table.content || [];
  if (rows.length === 0) return '';

  const lines: string[] = [];

  rows.forEach((row, rowIndex) => {
    const cells = row.content || [];
    const cellTexts = cells.map(cell => {
      const content = cell.content || [];
      return serializeContent(content).trim();
    });

    lines.push('| ' + cellTexts.join(' | ') + ' |');

    // Add separator after first row (header)
    if (rowIndex === 0) {
      lines.push('| ' + cellTexts.map(() => '---').join(' | ') + ' |');
    }
  });

  return lines.join('\n');
};

/**
 * Helper to inject manual markers back into markdown
 */
export const injectManualMarkers = (
  markdown: string,
  markers: ManualMarker[]
): string => {
  let result = markdown;

  markers.forEach(marker => {
    const markerText = `<!-- MANUAL:START:${marker.author}:${marker.timestamp}:${marker.type} -->\n${marker.content}\n<!-- MANUAL:END -->`;
    // Simple injection - for production, use proper AST manipulation
    result = result + '\n\n' + markerText;
  });

  return result;
};
