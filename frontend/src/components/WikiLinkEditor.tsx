import React, { useEffect, useRef, useState } from 'react';

interface LinkableDocument {
  filename: string;
  title: string;
  file_type: string;
}

interface WikiLinkEditorProps {
  value: string;
  onChange: (value: string) => void;
  documentId: string;
  version: string;
  placeholder?: string;
}

/**
 * Markdown editor with wikilink autocomplete.
 *
 * Features:
 * - Trigger autocomplete with [[
 * - Filter suggestions as you type
 * - Navigate with arrow keys
 * - Insert with Enter/Tab
 * - Syntax highlighting for [[wikilinks]]
 */
const WikiLinkEditor: React.FC<WikiLinkEditorProps> = ({
  value,
  onChange,
  documentId,
  version,
  placeholder = 'Write markdown with [[wikilinks]]...'
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [linkableDocuments, setLinkableDocuments] = useState<LinkableDocument[]>([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [autocompletePosition, setAutocompletePosition] = useState({ top: 0, left: 0 });
  const [filteredSuggestions, setFilteredSuggestions] = useState<LinkableDocument[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch linkable documents on mount
  useEffect(() => {
    const fetchLinkableDocuments = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/documents/${documentId}/versions/${version}/search-linkable`
        );
        if (response.ok) {
          const data = await response.json();
          setLinkableDocuments(data);
        }
      } catch (error) {
        console.error('Failed to fetch linkable documents:', error);
      }
    };

    fetchLinkableDocuments();
  }, [documentId, version]);

  // Handle text changes and detect [[ trigger
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);

    const textarea = textareaRef.current;
    if (!textarea) return;

    const cursorPos = textarea.selectionStart;
    const textBeforeCursor = newValue.substring(0, cursorPos);

    // Check if we just typed [[
    const lastTwoChars = textBeforeCursor.slice(-2);
    if (lastTwoChars === '[[') {
      // Show autocomplete
      const position = getCaretCoordinates(textarea, cursorPos);
      setAutocompletePosition(position);
      setShowAutocomplete(true);
      setSearchQuery('');
      setFilteredSuggestions(linkableDocuments);
      setSelectedIndex(0);
      return;
    }

    // If autocomplete is open, check if we're still in a wikilink
    if (showAutocomplete) {
      const match = textBeforeCursor.match(/\[\[([^\]]+)$/);
      if (match) {
        // Update search query
        const query = match[1];
        setSearchQuery(query);

        // Filter suggestions
        const filtered = linkableDocuments.filter(doc =>
          doc.filename.toLowerCase().includes(query.toLowerCase()) ||
          doc.title.toLowerCase().includes(query.toLowerCase())
        );
        setFilteredSuggestions(filtered);
        setSelectedIndex(0);
      } else {
        // Closed the wikilink
        setShowAutocomplete(false);
      }
    }
  };

  // Handle keyboard navigation in autocomplete
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!showAutocomplete) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          Math.min(prev + 1, filteredSuggestions.length - 1)
        );
        break;

      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
        break;

      case 'Enter':
      case 'Tab':
        if (filteredSuggestions.length > 0) {
          e.preventDefault();
          insertWikilink(filteredSuggestions[selectedIndex]);
        }
        break;

      case 'Escape':
        e.preventDefault();
        setShowAutocomplete(false);
        break;
    }
  };

  // Insert selected wikilink
  const insertWikilink = (doc: LinkableDocument) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const cursorPos = textarea.selectionStart;
    const textBeforeCursor = value.substring(0, cursorPos);
    const textAfterCursor = value.substring(cursorPos);

    // Find the [[ that triggered autocomplete
    const match = textBeforeCursor.match(/\[\[([^\]]+)$/);
    if (!match) return;

    const linkStart = cursorPos - match[0].length;
    const newText =
      value.substring(0, linkStart) +
      `[[${doc.filename}]]` +
      textAfterCursor;

    onChange(newText);
    setShowAutocomplete(false);

    // Move cursor after the inserted wikilink
    setTimeout(() => {
      const newCursorPos = linkStart + `[[${doc.filename}]]`.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  // Get caret coordinates for positioning autocomplete dropdown
  const getCaretCoordinates = (element: HTMLTextAreaElement, position: number) => {
    const div = document.createElement('div');
    const style = getComputedStyle(element);

    // Copy styles to mirror element
    [
      'fontFamily', 'fontSize', 'fontWeight', 'letterSpacing',
      'lineHeight', 'padding', 'border', 'boxSizing'
    ].forEach(prop => {
      div.style[prop as any] = style[prop as any];
    });

    div.style.position = 'absolute';
    div.style.visibility = 'hidden';
    div.style.whiteSpace = 'pre-wrap';
    div.style.wordWrap = 'break-word';
    div.style.width = `${element.offsetWidth}px`;

    const textContent = element.value.substring(0, position);
    div.textContent = textContent;

    const span = document.createElement('span');
    span.textContent = element.value.substring(position) || '.';
    div.appendChild(span);

    document.body.appendChild(div);

    const rect = element.getBoundingClientRect();
    const spanRect = span.getBoundingClientRect();

    document.body.removeChild(div);

    return {
      top: spanRect.top - rect.top + element.scrollTop + 20,
      left: spanRect.left - rect.left + element.scrollLeft
    };
  };

  // Syntax highlighting for wikilinks (simple approach with overlays)
  const renderHighlightedText = () => {
    // Replace [[wikilinks]] with highlighted version
    const highlighted = value.replace(
      /\[\[([^\]]+)\]\]/g,
      '<span class="wikilink">&#91;&#91;$1&#93;&#93;</span>'
    );
    return { __html: highlighted };
  };

  return (
    <div className="relative">
      {/* Main textarea */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="w-full h-96 p-4 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
        style={{ lineHeight: '1.5' }}
      />

      {/* Autocomplete dropdown */}
      {showAutocomplete && filteredSuggestions.length > 0 && (
        <div
          className="absolute z-10 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto"
          style={{
            top: `${autocompletePosition.top}px`,
            left: `${autocompletePosition.left}px`,
            minWidth: '300px'
          }}
        >
          {filteredSuggestions.map((doc, index) => (
            <div
              key={doc.filename}
              className={`px-4 py-2 cursor-pointer ${
                index === selectedIndex
                  ? 'bg-blue-500 text-white'
                  : 'hover:bg-gray-100'
              }`}
              onClick={() => insertWikilink(doc)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="font-medium">{doc.title}</div>
              <div className={`text-sm ${
                index === selectedIndex ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {doc.file_type} · {doc.filename}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Helper text */}
      <div className="mt-2 text-sm text-gray-500">
        Type <code className="px-1 py-0.5 bg-gray-100 rounded">[[</code> to insert a wikilink
      </div>

      <style>{`
        .wikilink {
          color: #2563eb;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default WikiLinkEditor;
