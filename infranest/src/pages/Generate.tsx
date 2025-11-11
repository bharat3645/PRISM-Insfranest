import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { Code, Download, ArrowRight } from 'lucide-react';
import { useProjectData } from '../lib/store';
import { api } from '../lib/api';

const Generate: React.FC = () => {
  const { currentDSL } = useProjectData();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<any>(null);
  const [selectedFramework, setSelectedFramework] = useState('django');
  const navigate = useNavigate();

  // Check if DSL is available - removed auto-redirect, let user click button
  // They'll get a helpful error message if no DSL exists

  const handleGenerate = async () => {
    if (!currentDSL) {
      toast.error('No DSL specification found. Please create one first.');
      setTimeout(() => navigate('/prompt'), 2000);
      return;
    }

    setIsGenerating(true);
    
    try {
      // Call backend API to generate code
      const result = await api.generateCode(currentDSL, selectedFramework);
      
      // Convert files array to object format
      const filesObj: Record<string, string> = {};
      result.files.forEach(file => {
        filesObj[file.path] = file.content;
      });
      
      setGeneratedCode({ files: filesObj });
      setIsGenerated(true);
      toast.success(`Code generated successfully! ${result.files.length} files created.`);
    } catch (error) {
      console.error('Code generation error:', error);
      toast.error('Failed to generate code. Please try again.');
      setIsGenerated(false);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeploy = () => {
    toast.success('Proceeding to deployment...');
    navigate('/deploy');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Code Generator</h1>
        {isGenerated && (
          <div className="flex space-x-3">
            <button
              className="flex items-center px-4 py-2 bg-[#1a1a1a] hover:bg-[#252525] border border-[#333] rounded-lg text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </button>
            <button
              onClick={handleDeploy}
              className="flex items-center px-4 py-2 bg-gradient-to-r from-[#00ff88] to-[#00ccff] hover:from-[#33ffaa] hover:to-[#33ddff] text-black font-medium rounded-lg"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              Deploy
            </button>
          </div>
        )}
      </div>

      <div className="bg-[#111111] border border-[#333333] rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Code className="w-5 h-5 mr-2 text-[#00ff88]" />
            <h2 className="text-xl font-semibold">Generated Code</h2>
          </div>
          {!isGenerated && !isGenerating && (
            <select
              value={selectedFramework}
              onChange={(e) => setSelectedFramework(e.target.value)}
              className="px-4 py-2 bg-[#1a1a1a] border border-[#333] rounded-lg text-white focus:outline-none focus:border-[#00ff88]"
            >
              <option value="django">Django (Python)</option>
              <option value="rails">Rails (Ruby)</option>
              <option value="go">Go (Golang)</option>
            </select>
          )}
        </div>
        
        {!isGenerated && !isGenerating && (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="text-gray-400 mb-2">Select a framework and click the button below</p>
            <p className="text-gray-500 text-sm mb-6">Code will be generated from your DSL specification</p>
            <button
              onClick={handleGenerate}
              className="px-6 py-3 bg-gradient-to-r from-[#00ff88] to-[#00ccff] hover:from-[#33ffaa] hover:to-[#33ddff] text-black font-medium rounded-lg"
            >
              Generate Code
            </button>
          </div>
        )}
        
        {isGenerating && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#00ff88] mb-4"></div>
            <p className="text-gray-400">Generating code, please wait...</p>
          </div>
        )}
        
        {isGenerated && generatedCode && (
          <div className="space-y-4">
            <div className="mb-4">
              <p className="text-gray-400 text-sm">
                Generated {Object.keys(generatedCode.files || {}).length} files using <span className="text-[#00ff88]">{selectedFramework}</span> framework
              </p>
            </div>
            {Object.entries(generatedCode.files || {}).map(([filename, content]: [string, any]) => {
              const extension = filename.split('.').pop() || '';
              const languageMap: Record<string, string> = {
                'json': 'JSON',
                'js': 'JavaScript',
                'py': 'Python',
                'rb': 'Ruby',
                'go': 'Go',
                'yml': 'YAML',
                'yaml': 'YAML',
                'html': 'HTML',
                'css': 'CSS',
                'ts': 'TypeScript',
                'tsx': 'TypeScript',
              };
              const language = languageMap[extension] || extension.toUpperCase();
              
              return (
                <div key={filename} className="bg-[#0a0a0a] p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">{filename}</span>
                    <span className="text-xs px-2 py-1 bg-[#1a1a1a] rounded text-gray-400">{language}</span>
                  </div>
                  <pre className="text-sm text-white font-mono overflow-x-auto max-h-96">
                    {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
                  </pre>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Generate;