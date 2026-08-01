import React from 'react';

export default function ArtifactTabs({ activeTab, onTabChange }) {
  return (
    <div className="artifact-tabs">
      <button 
        className={`artifact-tab ${activeTab === 'preview' ? 'active' : ''}`}
        onClick={() => onTabChange('preview')}
      >
        Preview
      </button>
      <button 
        className={`artifact-tab ${activeTab === 'code' ? 'active' : ''}`}
        onClick={() => onTabChange('code')}
      >
        Code
      </button>
    </div>
  );
}
