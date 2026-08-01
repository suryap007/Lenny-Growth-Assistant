import React from 'react';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

export default function ArtifactToolbar({ artifact, activeTab }) {
  const handleCopy = () => {
    if (artifact?.artifact_content) {
      navigator.clipboard.writeText(artifact.artifact_content);
    }
  };

  const handleDownload = async () => {
    if (!artifact?.artifact_content) return;
    
    const zip = new JSZip();
    
    // Add metadata JSON
    const metadata = {
      title: artifact.artifact_title,
      type: artifact.artifact_type,
      generated_at: new Date().toISOString()
    };
    zip.file("artifact.json", JSON.stringify(metadata, null, 2));

    // Add actual artifact content
    if (artifact.artifact_type === 'html') {
      zip.file("index.html", artifact.artifact_content);
    } else {
      zip.file("README.md", artifact.artifact_content);
    }

    // Generate ZIP and trigger download
    try {
      const content = await zip.generateAsync({ type: "blob" });
      saveAs(content, "artifact.zip");
    } catch (err) {
      console.error("Failed to generate ZIP", err);
    }
  };

  return (
    <div className="artifact-toolbar">
      <button className="toolbar-btn" onClick={handleCopy} title="Copy Code">
        📋 Copy
      </button>
      <button className="toolbar-btn" onClick={handleDownload} title="Download ZIP">
        ⬇️ Download ZIP
      </button>
    </div>
  );
}
