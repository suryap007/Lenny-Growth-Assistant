import React, { useState } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import ArtifactTabs from './ArtifactTabs';
import ArtifactToolbar from './ArtifactToolbar';
import { X } from 'lucide-react';

export default function ArtifactViewer({ artifact, onClose }) {
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' or 'code'

  if (!artifact) return null;

  const isHtml = artifact.artifact_type === 'html';

  return (
    <div className="artifact-viewer">
      <div className="artifact-header">
        <div className="artifact-header-left">
          <h3 className="artifact-title">{artifact.artifact_title}</h3>
          <ArtifactTabs activeTab={activeTab} onTabChange={setActiveTab} />
        </div>
        <div className="artifact-header-right">
          <ArtifactToolbar artifact={artifact} activeTab={activeTab} />
          <button className="close-btn" onClick={onClose} title="Close Artifact">
            <X size={20} />
          </button>
        </div>
      </div>
      
      <div className="artifact-content">
        {activeTab === 'preview' ? (
          isHtml ? (
            <iframe 
              srcDoc={artifact.artifact_content} 
              sandbox="allow-scripts allow-same-origin"
              className="artifact-iframe"
              title={artifact.artifact_title}
            />
          ) : (
            <div className="markdown-body artifact-padding">
              <MarkdownRenderer content={artifact.artifact_content} />
            </div>
          )
        ) : (
          <div className="artifact-code-view">
            <pre>
              <code>{artifact.artifact_content}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
