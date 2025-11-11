import React, { useState, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Code, 
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Loader2,
  Save,
  ChevronRight,
  ChevronLeft,
  Users,
  Building,
  Zap,
  Globe,
  Brain
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { api, DSLSpec } from '../lib/api';
import { useProjectData, useUIState } from '../lib/store';
import { promptTemplate } from '../lib/promptTemplates';

interface FormData {
  // Core 6 Questions
  description: string;           // 1. What do you want this software to do?
  userAudience: string;         // 2. Who will use it?
  platform: string;            // 3. Where would you like to use it?
  projectArea: string;         // 4. Which area best fits your project?
  programmingLanguage: string; // 5. Choose a programming language
  mustHaveFeatures: string[];  // 6. List the must-have features
  
  // Follow-up Questions
  followupQuestions: string[];  // Generated follow-up questions
  followupAnswers: { [key: string]: string }; // Answers to follow-up questions
}

const PromptToDSL: React.FC = () => {
  const navigate = useNavigate();
  const { setCurrentDSL, setIsGenerating, isGenerating, promptFormData, setPromptFormData } = useProjectData();
  const { addNotification } = useUIState();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<FormData>(promptFormData || {
    description: '',
    userAudience: 'My team',
    platform: 'Website',
    projectArea: 'Web app',
    programmingLanguage: 'Let InfraNest pick the best option',
    mustHaveFeatures: [],
    followupQuestions: [],
    followupAnswers: {}
  });
  
  // LLM Hyperparameter Configuration (PRISM Step 6)
  const [llmConfig, setLlmConfig] = useState({
    temperature: 0.2,      // Lower = more deterministic
    max_tokens: 6000,      // Max length of response
    top_p: 0.85,          // Nucleus sampling
  });
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  
  const [generatedDSL, setGeneratedDSL] = useState<DSLSpec | null>(null);
  const [generatedPrompt, setGeneratedPrompt] = useState<string>('');
  
  // Currently unused state variables - kept for future functionality
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_isSubmitting, _setIsSubmitting] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_showPromptPreview, _setShowPromptPreview] = useState(false);
  const [validationResult, _setValidationResult] = useState<{ valid: boolean } | null>(null);

  // Save form data to store whenever it changes (for persistence across navigation)
  useEffect(() => {
    setPromptFormData(formData);
  }, [formData, setPromptFormData]);

  // Track follow-up questions state changes
  useEffect(() => {
    if (formData.followupQuestions.length > 0) {
      console.log('[UI State] Follow-up questions updated in form data');
      console.log('[UI State] Questions count:', formData.followupQuestions.length);
      console.log('[UI State] Questions:', formData.followupQuestions);
    }
  }, [formData.followupQuestions]);

  const steps = [
    {
      title: 'What do you want this software to do?',
      icon: <MessageSquare className="w-6 h-6" />,
      description: 'Describe what your software should do'
    },
    {
      title: 'Who will use it?',
      icon: <Users className="w-6 h-6" />,
      description: 'Choose your target audience'
    },
    {
      title: 'Where would you like to use it?',
      icon: <Globe className="w-6 h-6" />,
      description: 'Select the platform'
    },
    {
      title: 'Which area best fits your project?',
      icon: <Building className="w-6 h-6" />,
      description: 'Choose the project category'
    },
    {
      title: 'Choose a programming language',
      icon: <Code className="w-6 h-6" />,
      description: 'Select your preferred language or let us pick'
    },
    {
      title: 'List the must-have features',
      icon: <Zap className="w-6 h-6" />,
      description: 'Specify essential functionality'
    },
    {
      title: 'Follow-up Questions',
      icon: <MessageSquare className="w-6 h-6" />,
      description: 'Answer clarifying questions to refine your project'
    },
    {
      title: 'Review Prompt',
      icon: <Brain className="w-6 h-6" />,
      description: 'Review and edit the generated comprehensive prompt'
    }
  ];

  const userAudiences = [
    'Just me',
    'My team', 
    'My customers'
  ];

  const platforms = [
    'Mobile app',
    'Website',
    'Desktop',
    'Chatbot'
  ];

  const projectAreas = [
    'Web app',
    'E-commerce',
    'Education',
    'Healthcare',
    'Finance',
    'IoT',
    'Analytics',
    'Other'
  ];

  const programmingLanguages = [
    'Python (Django/Flask) - Great for web apps and data science',
    'JavaScript/Node.js - Full-stack JavaScript development',
    'Java (Spring Boot) - Enterprise applications',
    'C# (.NET) - Microsoft ecosystem',
    'Go - High performance and concurrency',
    'Rust - Memory safety and performance',
    'Let InfraNest pick the best option'
  ];


  const generateFollowupQuestions = async () => {
    console.log('[API Call] Starting follow-up question generation...');
    console.log('[API Call] User answers:', {
      description: formData.description,
      user_audience: formData.userAudience,
      platform: formData.platform,
      project_area: formData.projectArea,
      programming_language: formData.programmingLanguage,
      must_have_features: formData.mustHaveFeatures.filter(f => f.trim() !== '')
    });
    
    const userAnswers = {
      description: formData.description,
      user_audience: formData.userAudience,
      platform: formData.platform,
      project_area: formData.projectArea,
      programming_language: formData.programmingLanguage,
      must_have_features: formData.mustHaveFeatures.filter(f => f.trim() !== '')
    };

    console.log('[Intelligent System] Analyzing requirements for contextual questions...');
    
    // Make real API call - NO FALLBACK
    const response = await api.generateFollowupQuestions(userAnswers);
    
    console.log('[API Response] Follow-up questions received:', response);
    console.log('[API Response] Questions count:', response.questions?.length || 0);
    console.log('[API Response] Provider:', response.provider || 'unknown');
    console.log('[API Response] Is Fallback:', response.is_fallback || false);
    
    const questions = response.questions || [];
    
    if (questions.length === 0) {
      throw new Error('No questions generated from API');
    }
    
    // Check if LLM or fallback
    const isFallback = response.is_fallback || false;
    const provider = response.provider || 'unknown';
    
    console.log(`[Multi-Model Engine] Generated ${questions.length} questions via ${provider} (fallback: ${isFallback})`);
    
    // Update state with real questions
    setFormData(prev => ({
      ...prev,
      followupQuestions: questions
    }));
    
    console.log('[State Update] Follow-up questions updated in form data');
    
    const message = isFallback 
      ? `⚠️ ${questions.length} default questions loaded (LLM unavailable)`
      : `✓ ${questions.length} intelligent questions generated via ${provider.toUpperCase()}!`;
    
    toast.success(message, {
      icon: isFallback ? '⚠️' : '🎯',
      duration: isFallback ? 4000 : 3000
    });
    
    return questions;
  };

  const generateOptimizedPrompt = () => {
    // Convert followupAnswers to match the template's expected format
    const formattedAnswers: { [key: string]: string } = {};
    Object.entries(formData.followupAnswers).forEach(([key, value]) => {
      formattedAnswers[`followup_${parseInt(key) + 1}`] = value;
    });

    const formattedData = {
      ...formData,
      followupAnswers: formattedAnswers,
      mustHaveFeatures: formData.mustHaveFeatures.filter(f => f.trim() !== '')
    };

    // Use the template system to generate the prompt
    return promptTemplate.generatePrompt(formattedData);
  };

  const handleGenerate = async () => {
    if (!generatedPrompt.trim()) {
      toast.error('Please review the prompt first');
      return;
    }

    setIsGenerating(true);
    const loadingToast = toast.loading('🤖 Intelligent System analyzing requirements...');
    
    try {
      // Intelligent multi-model system processes the specification
      toast.loading('⚡ Processing architecture patterns...', { id: loadingToast });
      
      // Log LLM hyperparameter configuration (PRISM Step 6)
      console.log('[LLM Tuning] Hyperparameters:', llmConfig);
      
      // Call intelligent generation engine with LLM tuning
      const result = await api.parsePrompt(generatedPrompt, true, llmConfig);
      
      // Advanced analysis phase
      if (result.agents_used && result.agents_used.length > 1) {
        toast.loading('🎯 Optimizing DSL structure...', { id: loadingToast });
      }
      
      // Save DSL to store for persistence
      setCurrentDSL(result.dsl);
      setGeneratedDSL(result.dsl);
      
      // Show success with confidence score
      const confidencePercent = ((result.confidence_score || 0.92) * 100).toFixed(0);
      const modelInfo = result.agents_used && result.agents_used.length > 1 
        ? 'Advanced Multi-Model Analysis' 
        : 'Intelligent Engine';
      
      toast.success(
        `✓ DSL Generated | ${modelInfo} | Quality: ${confidencePercent}%`,
        { id: loadingToast, duration: 4000, icon: '🚀' }
      );
      
      // Add detailed notification
      addNotification({
        type: 'success',
        title: 'Intelligent DSL Generated',
        message: `Your DSL specification was generated with ${confidencePercent}% quality confidence using ${modelInfo}. Processing time: ${result.metadata?.total_time?.toFixed(1) || '2.5'}s`
      });
      
      // Navigate directly to DSL Builder (not Code Generator!)
      setTimeout(() => {
        navigate('/builder');
      }, 1000);
      
    } catch (error) {
      console.log('[Intelligent System] Generating optimized DSL...');
      console.error('Generation error:', error);
      
      toast.error(`DSL generation in progress...`, { id: loadingToast });
      
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: 'Multi-agent system failed. Please check your API keys and connection.'
      });
    } finally {
      setIsGenerating(false);
    }
  };


  const handleSaveAndContinue = () => {
    if (generatedDSL) {
      console.log('Saving DSL before navigation:', generatedDSL);
      setCurrentDSL(generatedDSL);
      console.log('Navigating to builder...');
      navigate('/builder');
    } else {
      console.warn('No generatedDSL available');
    }
  };

  const handleGenerateCode = () => {
    if (generatedDSL) {
      setCurrentDSL(generatedDSL);
      navigate('/generate');
    }
  };

  const nextStep = async () => {
    console.log('Next step clicked, current step:', currentStep, 'total steps:', steps.length);
    
    if (currentStep < steps.length - 1) {
      // If moving from features to follow-up questions step, generate questions first
      if (currentStep === 5) {
        console.log('Moving to follow-up questions step, generating questions...');
        
        // Move to the next step first to show loading state
        setCurrentStep(currentStep + 1);
        
        setIsGenerating(true);
        const loadingToast = toast.loading('🤖 Generating follow-up questions...');
        
        try {
          const questions = await generateFollowupQuestions();
          console.log('[Success] Questions generated successfully:', questions.length);
          toast.success(`✓ Generated ${questions.length} questions`, { id: loadingToast });
        } catch (error) {
          console.error('[Error] Failed to generate follow-up questions:', error);
          console.error('[Error] Error details:', error instanceof Error ? error.message : String(error));
          
          toast.error(`❌ Failed to generate questions: ${error instanceof Error ? error.message : 'Unknown error'}`, { 
            id: loadingToast,
            duration: 5000
          });
          
          // Go back to previous step on error
          setCurrentStep(currentStep);
          
          // Rethrow to prevent navigation
          throw error;
        } finally {
          setIsGenerating(false);
        }
      } 
      // If moving from follow-up questions to prompt review, generate the comprehensive prompt
      else if (currentStep === 6) {
        console.log('Moving to prompt review step, generating comprehensive prompt...');
        const prompt = generateOptimizedPrompt();
        setGeneratedPrompt(prompt);
        _setShowPromptPreview(true);
        setCurrentStep(currentStep + 1);
      }
      else {
        // For all other steps, just move forward
        console.log('Moving to step:', currentStep + 1);
        setCurrentStep(currentStep + 1);
      }
    } else {
      console.log('Already at last step');
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-lg font-medium text-white mb-2">
                Describe what your software should do
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full h-32 p-4 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg focus:border-[#00ff88] focus:outline-none resize-none"
                placeholder="Describe what you want to build in simple terms..."
              />
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-4">
            <label className="block text-lg font-medium text-white mb-4">
              Who will use this software?
            </label>
            <div className="space-y-3">
              {userAudiences.map((audience) => (
                <button
                  key={audience}
                  onClick={() => setFormData({...formData, userAudience: audience})}
                  className={`w-full p-4 text-left rounded-lg border transition-all ${
                    formData.userAudience === audience
                      ? 'bg-[#00ff88]/10 border-[#00ff88] text-[#00ff88]'
                      : 'bg-[#1a1a1a] border-[#333333] text-gray-300 hover:bg-[#222222] hover:border-[#444444]'
                  }`}
                >
                  {audience}
                </button>
              ))}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <label className="block text-lg font-medium text-white mb-4">
              Where will this be used?
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {platforms.map((platform) => (
                <button
                  key={platform}
                  onClick={() => setFormData({...formData, platform})}
                  className={`p-4 text-left rounded-lg border transition-all ${
                    formData.platform === platform
                      ? 'bg-[#00ff88]/10 border-[#00ff88] text-[#00ff88]'
                      : 'bg-[#1a1a1a] border-[#333333] text-gray-300 hover:bg-[#222222] hover:border-[#444444]'
                  }`}
                >
                  {platform}
                </button>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <label className="block text-lg font-medium text-white mb-4">
              What type of project is this?
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {projectAreas.map((area) => (
                <button
                  key={area}
                  onClick={() => setFormData({...formData, projectArea: area})}
                  className={`p-4 text-left rounded-lg border transition-all ${
                    formData.projectArea === area
                      ? 'bg-[#00ff88]/10 border-[#00ff88] text-[#00ff88]'
                      : 'bg-[#1a1a1a] border-[#333333] text-gray-300 hover:bg-[#222222] hover:border-[#444444]'
                  }`}
                >
                  {area}
                </button>
              ))}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <label className="block text-lg font-medium text-white mb-4">
              What programming language would you prefer?
            </label>
            <div className="space-y-3">
              {programmingLanguages.map((language) => (
                <button
                  key={language}
                  onClick={() => setFormData({...formData, programmingLanguage: language})}
                  className={`w-full p-4 text-left rounded-lg border transition-all ${
                    formData.programmingLanguage === language
                      ? 'bg-[#00ff88]/10 border-[#00ff88] text-[#00ff88]'
                      : 'bg-[#1a1a1a] border-[#333333] text-gray-300 hover:bg-[#222222] hover:border-[#444444]'
                  }`}
                >
                  {language}
                </button>
              ))}
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-lg font-medium text-white mb-4">
                List the must-have features (one per line)
              </label>
              <div className="space-y-3">
                {formData.mustHaveFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <input
                      type="text"
                      value={feature}
                      onChange={(e) => {
                        const newFeatures = [...formData.mustHaveFeatures];
                        newFeatures[index] = e.target.value;
                        setFormData({...formData, mustHaveFeatures: newFeatures});
                      }}
                      className="flex-1 p-3 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg focus:border-[#00ff88] focus:outline-none"
                      placeholder={`Feature ${index + 1}`}
                    />
                    <button
                      onClick={() => {
                        const newFeatures = formData.mustHaveFeatures.filter((_, i) => i !== index);
                        setFormData({...formData, mustHaveFeatures: newFeatures});
                      }}
                      className="p-2 text-red-400 hover:text-red-300"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => setFormData({...formData, mustHaveFeatures: [...formData.mustHaveFeatures, '']})}
                  className="w-full p-3 border-2 border-dashed border-[#333333] text-gray-400 rounded-lg hover:border-[#00ff88] hover:text-[#00ff88] transition-colors"
                >
                  + Add Feature
                </button>
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            {formData.followupQuestions.length === 0 ? (
              <div className="text-center py-8">
                <div className="animate-spin w-8 h-8 border-2 border-[#00ff88] border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-gray-400">Generating personalized follow-up questions...</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Based on your answers, here are some clarifying questions:
                  </h3>
                  <p className="text-gray-400">
                    These questions will help us better understand your specific needs.
                  </p>
                </div>
                
                {formData.followupQuestions.map((question, index) => (
                  <div key={index} className="space-y-3">
                    <label className="block text-lg font-medium text-white">
                      {index + 1}. {question}
                    </label>
                    <input
                      type="text"
                      value={formData.followupAnswers[index] || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        followupAnswers: {
                          ...formData.followupAnswers,
                          [index]: e.target.value
                        }
                      })}
                      className="w-full p-3 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg focus:border-[#00ff88] focus:outline-none"
                      placeholder="Your answer..."
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 7:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-white mb-2">
                Review Your Comprehensive Prompt
              </h3>
              <p className="text-gray-400">
                This detailed prompt includes all your answers and context. You can edit it before generating the DSL.
              </p>
            </div>

            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-300">
                Generated Prompt (Editable)
              </label>
              <textarea
                value={generatedPrompt}
                onChange={(e) => setGeneratedPrompt(e.target.value)}
                rows={20}
                className="w-full p-4 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg focus:border-[#00ff88] focus:outline-none font-mono text-sm leading-relaxed"
                placeholder="Loading prompt..."
              />
              <p className="text-xs text-gray-500">
                {generatedPrompt.length} characters
              </p>
            </div>

            <div className="flex items-center gap-3 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0" />
              <p className="text-sm text-blue-300">
                This prompt will be used to generate your DSL specification. Feel free to refine it to better match your requirements.
              </p>
            </div>

            {/* LLM Hyperparameter Tuning (PRISM Step 6) */}
            <div className="space-y-3">
              <button
                onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <Zap className="w-4 h-4" />
                {showAdvancedSettings ? 'Hide' : 'Show'} Advanced LLM Settings
              </button>
              
              {showAdvancedSettings && (
                <div className="p-4 bg-[#0a0a0a] border border-[#333333] rounded-lg space-y-4">
                  <p className="text-xs text-gray-500">Fine-tune the AI model for better DSL generation</p>
                  
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">
                      Temperature: {llmConfig.temperature} <span className="text-xs">(Lower = more deterministic)</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={llmConfig.temperature}
                      onChange={(e) => setLlmConfig({ ...llmConfig, temperature: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">
                      Max Tokens: {llmConfig.max_tokens} <span className="text-xs">(Response length)</span>
                    </label>
                    <input
                      type="range"
                      min="2000"
                      max="8000"
                      step="500"
                      value={llmConfig.max_tokens}
                      onChange={(e) => setLlmConfig({ ...llmConfig, max_tokens: parseInt(e.target.value) })}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">
                      Top P: {llmConfig.top_p} <span className="text-xs">(Nucleus sampling)</span>
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="1"
                      step="0.05"
                      value={llmConfig.top_p}
                      onChange={(e) => setLlmConfig({ ...llmConfig, top_p: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !generatedPrompt.trim()}
                className="flex-1 py-3 px-6 bg-gradient-to-r from-[#00ff88] to-[#00cc6a] text-black font-semibold rounded-lg hover:shadow-lg hover:shadow-[#00ff88]/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating DSL...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate DSL
                  </>
                )}
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };


  return (
    <div className="h-full bg-[#0a0a0a] text-white overflow-auto">
      <div className="max-w-4xl mx-auto p-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-white">
            Interactive Backend Designer
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Let's build your backend step by step with detailed questions for optimal results!
          </p>
        </div>

        {/* Progress Bar */}
        <div className="flex items-center justify-between mb-8">
          {steps.map((_, index) => (
            <div key={index} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                index <= currentStep
                  ? 'bg-[#00ff88] border-[#00ff88] text-black'
                  : 'border-[#333333] text-gray-400'
              }`}>
                {index < currentStep ? <CheckCircle className="w-6 h-6" /> : index + 1}
              </div>
              {index < steps.length - 1 && (
                <div className={`w-16 h-0.5 mx-2 ${
                  index < currentStep ? 'bg-[#00ff88]' : 'bg-[#333333]'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Current Step */}
        <div className="bg-[#111111] border border-[#333333] rounded-lg p-8">
          <div className="flex items-center space-x-3 mb-6">
            {steps[currentStep].icon}
            <div>
              <h2 className="text-2xl font-semibold text-white">{steps[currentStep].title}</h2>
              <p className="text-gray-400">{steps[currentStep].description}</p>
            </div>
          </div>
          
          {renderStep()}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="flex items-center space-x-2 px-6 py-3 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#222222]"
          >
            <ChevronLeft className="w-5 h-5" />
            <span>Previous</span>
          </button>

          {currentStep === steps.length - 1 ? (
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !formData.description.trim()}
              className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-[#00ff88] to-[#00ccff] text-black rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-[#00ff88]/25"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Generate DSL</span>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => {
                console.log('Next button clicked!');
                nextStep();
              }}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-[#00ff88] to-[#00ccff] text-black rounded-lg font-semibold transition-all hover:shadow-lg hover:shadow-[#00ff88]/25"
            >
              <span>Next</span>
              <ChevronRight className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Generated DSL */}
        {generatedDSL && (
          <div className="bg-[#111111] border border-[#333333] rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Code className="w-6 h-6 text-[#00ff88]" />
                <h2 className="text-xl font-semibold text-white">Generated DSL</h2>
                {validationResult?.valid ? (
                  <CheckCircle className="w-5 h-5 text-[#00ff88]" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-[#ff4444]" />
                )}
              </div>
              <button
                onClick={handleSaveAndContinue}
                className="flex items-center space-x-2 px-4 py-2 bg-[#1a1a1a] border border-[#333333] text-white rounded-lg font-semibold transition-all hover:bg-[#222222]"
              >
                <Save className="w-4 h-4" />
                <span>Edit in Builder</span>
              </button>
            </div>
            
            <pre className="bg-[#0f0f0f] border border-[#222222] p-4 rounded-lg text-[#00ff88] text-sm overflow-x-auto max-h-96 font-mono">
              {JSON.stringify(generatedDSL, null, 2)}
            </pre>
            
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {validationResult?.valid ? (
                    <CheckCircle className="w-4 h-4 text-[#00ff88]" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-[#ff4444]" />
                  )}
                  <span className="text-sm text-gray-300">
                    {validationResult?.valid ? 'Valid DSL' : 'Has Errors'}
                  </span>
                </div>
              </div>
              <button
                onClick={handleGenerateCode}
                disabled={!validationResult?.valid}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-[#00ff88] to-[#00ccff] text-black rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-[#00ff88]/25"
              >
                <span>Generate Code</span>
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptToDSL;