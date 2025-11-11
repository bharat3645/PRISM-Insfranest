import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { Code, Save, Play } from 'lucide-react';
import { useProjectData } from '../lib/store';
import yaml from 'js-yaml';

const Builder: React.FC = () => {
  const { currentDSL, setCurrentDSL } = useProjectData();
  const [dslCode, setDslCode] = useState(`# InfraNest DSL Example
name: my-web-app
type: web-application

frontend:
  framework: react
  styling: tailwind
  features:
    - authentication
    - responsive-design
    - dark-mode

backend:
  language: node
  framework: express
  database: mongodb
  features:
    - rest-api
    - jwt-auth
    - rate-limiting

deployment:
  provider: aws
  services:
    - ec2
    - s3
    - cloudfront
  scaling: auto
`);
  const navigate = useNavigate();

  // Load DSL from store when component mounts
  useEffect(() => {
    if (currentDSL) {
      try {
        // Convert DSL object to YAML string
        const yamlString = yaml.dump(currentDSL, { indent: 2, noRefs: true });
        setDslCode(yamlString);
        console.log('Loaded DSL from store:', currentDSL);
      } catch (error) {
        console.error('Error converting DSL to YAML:', error);
        // If conversion fails, just stringify the DSL
        setDslCode(JSON.stringify(currentDSL, null, 2));
      }
    }
  }, [currentDSL]);

  const handleSave = () => {
    try {
      // Parse YAML back to object and save to store
      const dslObject = yaml.load(dslCode);
      setCurrentDSL(dslObject);
      toast.success('DSL saved successfully!');
    } catch (error) {
      toast.error('Invalid YAML format. Please check your DSL.');
    }
  };

  const handleGenerate = () => {
    // Save current DSL before navigating
    try {
      const dslObject = yaml.load(dslCode);
      setCurrentDSL(dslObject);
      toast.success('Proceeding to code generation...');
      navigate('/generate');
    } catch (error) {
      toast.error('Please save a valid DSL before generating code.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">DSL Builder</h1>
        <div className="flex space-x-3">
          <button
            onClick={handleSave}
            className="flex items-center px-4 py-2 bg-[#1a1a1a] hover:bg-[#252525] border border-[#333] rounded-lg text-white"
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </button>
          <button
            onClick={handleGenerate}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-[#00ff88] to-[#00ccff] hover:from-[#33ffaa] hover:to-[#33ddff] text-black font-medium rounded-lg"
          >
            <Play className="w-4 h-4 mr-2" />
            Generate Code
          </button>
        </div>
      </div>

      <div className="bg-[#111111] border border-[#333333] rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Code className="w-5 h-5 mr-2 text-[#00ff88]" />
          <h2 className="text-xl font-semibold">DSL Editor</h2>
        </div>
        <div className="relative">
          <textarea
            value={dslCode}
            onChange={(e) => setDslCode(e.target.value)}
            className="w-full h-[500px] bg-[#0a0a0a] text-white font-mono p-4 border border-[#333333] rounded-lg focus:outline-none focus:border-[#00ff88] focus:ring-1 focus:ring-[#00ff88]"
          />
        </div>
      </div>
    </div>
  );
};

export default Builder;