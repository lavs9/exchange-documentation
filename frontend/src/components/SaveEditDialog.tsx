import React, { useState } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';

type SaveType = 'direct' | 'manual';
type MarkerType = 'callout' | 'note' | 'warning' | 'tip' | 'code';

interface SaveEditDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (saveType: SaveType, markerType?: MarkerType) => void;
  editedContent: string;
}

/**
 * Dialog for choosing how to save edits:
 * - Direct Edit: Overwrite chapter content
 * - Manual Note: Wrap with markers (preserved during version merge)
 */
const SaveEditDialog: React.FC<SaveEditDialogProps> = ({
  open,
  onClose,
  onSave,
  editedContent
}) => {
  const [saveType, setSaveType] = useState<SaveType>('direct');
  const [markerType, setMarkerType] = useState<MarkerType>('note');

  if (!open) return null;

  const handleSave = () => {
    if (saveType === 'manual') {
      onSave(saveType, markerType);
    } else {
      onSave(saveType);
    }
    onClose();
  };

  // Generate preview of how edit will appear with marker
  const getMarkerPreview = () => {
    const markers = {
      callout: {
        start: '<!-- MANUAL:START:CALLOUT -->',
        end: '<!-- MANUAL:END:CALLOUT -->',
        style: 'border-l-4 border-blue-500 bg-blue-50 text-blue-900'
      },
      note: {
        start: '<!-- MANUAL:START:NOTE -->',
        end: '<!-- MANUAL:END:NOTE -->',
        style: 'border-l-4 border-green-500 bg-green-50 text-green-900'
      },
      warning: {
        start: '<!-- MANUAL:START:WARNING -->',
        end: '<!-- MANUAL:END:WARNING -->',
        style: 'border-l-4 border-yellow-500 bg-yellow-50 text-yellow-900'
      },
      tip: {
        start: '<!-- MANUAL:START:TIP -->',
        end: '<!-- MANUAL:END:TIP -->',
        style: 'border-l-4 border-purple-500 bg-purple-50 text-purple-900'
      },
      code: {
        start: '<!-- MANUAL:START:CODE -->',
        end: '<!-- MANUAL:END:CODE -->',
        style: 'border-l-4 border-gray-500 bg-gray-50 text-gray-900 font-mono'
      }
    };

    const marker = markers[markerType];
    const preview = editedContent.split('\n').slice(0, 3).join('\n');
    const truncated = editedContent.split('\n').length > 3;

    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-xs text-gray-500 mb-2">Preview:</div>
        <div className={`p-3 rounded ${marker.style}`}>
          <pre className="text-xs whitespace-pre-wrap">
            {preview}
            {truncated && '\n...'}
          </pre>
        </div>
        <div className="mt-2 text-xs text-gray-600">
          <div>Start marker: <code className="bg-white px-1 py-0.5 rounded">{marker.start}</code></div>
          <div>End marker: <code className="bg-white px-1 py-0.5 rounded">{marker.end}</code></div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Save Edit</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            <p className="text-sm text-gray-600 mb-6">
              Choose how to save your changes:
            </p>

            {/* Save type options */}
            <div className="space-y-4">
              {/* Direct Edit */}
              <label className="flex items-start space-x-3 cursor-pointer p-4 border-2 rounded-lg transition-all hover:border-gray-300">
                <input
                  type="radio"
                  name="saveType"
                  value="direct"
                  checked={saveType === 'direct'}
                  onChange={(e) => setSaveType(e.target.value as SaveType)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Direct Edit (Default)</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Overwrite the chapter content directly. This will replace the existing content.
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    <AlertCircle className="w-4 h-4" />
                    <span>May be lost during version merges</span>
                  </div>
                </div>
              </label>

              {/* Manual Note */}
              <label className="flex items-start space-x-3 cursor-pointer p-4 border-2 rounded-lg transition-all hover:border-gray-300">
                <input
                  type="radio"
                  name="saveType"
                  value="manual"
                  checked={saveType === 'manual'}
                  onChange={(e) => setSaveType(e.target.value as SaveType)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Manual Note (Preserved)</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Wrap content with HTML comment markers. These notes are preserved during version merges.
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-green-600">
                    <Save className="w-4 h-4" />
                    <span>Preserved across versions</span>
                  </div>
                </div>
              </label>
            </div>

            {/* Marker type selection (only if Manual Note selected) */}
            {saveType === 'manual' && (
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Marker Type:
                </label>
                <select
                  value={markerType}
                  onChange={(e) => setMarkerType(e.target.value as MarkerType)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="callout">Callout (Blue)</option>
                  <option value="note">Note (Green)</option>
                  <option value="warning">Warning (Yellow)</option>
                  <option value="tip">Tip (Purple)</option>
                  <option value="code">Code (Gray, Monospace)</option>
                </select>

                {/* Preview */}
                {getMarkerPreview()}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default SaveEditDialog;
