import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  MessageSquare,
  CheckCircle,
  Loader2,
  ChevronRight,
  ChevronLeft,
  Brain,
  ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../lib/api';
import { useProjectData, useUIState } from '../lib/store';

interface Question {
  id: string;
  text: string;
  type: 'core' | 'generated';
  category?: string;
  required: boolean;
  options?: string[];
}

interface FormData {
  [key: string]: any;
}

interface AnalysisResult {
  success: boolean;
  analysis: {
    validity_score: number;
    is_valid: boolean;
    insights: string[];
    context_insights: string[];
    recommendations: string[];
  };
  requirements_summary: any;
  metadata: any;
}

const IntelligentQuestionFlow: React.FC = () => {
  const { setCurrentDSL, setIsGenerating, isGenerating } = useProjectData();
  const { addNotification } = useUIState();
  
  const [sessionId, setSessionId] = useState<string>('');
  const [currentStep, setCurrentStep] = useState(0);
  const [coreQuestions, setCoreQuestions] = useState<Question[]>([]);
  const [followupQuestions, setFollowupQuestions] = useState<Question[]>([]);
  const [formData, setFormData] = useState<FormData>({});
  const [followupAnswers, setFollowupAnswers] = useState<FormData>({});
  const [isLoading, setIsLoading] = useState(false);
  const [coreComplete, setCoreComplete] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const steps = [
    { title: 'Core Questions', icon: <MessageSquare className="w-6 h-6" />, description: 'Answer 6 essential questions' },
    { title: 'Follow-up Questions', icon: <Brain className="w-6 h-6" />, description: 'AI-generated clarifying questions' },
    { title: 'Analysis & DSL', icon: <Sparkles className="w-6 h-6" />, description: 'Intelligent analysis and DSL generation' }
  ];

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setIsLoading(true);
      const response = await api.startIntelligentSession();
      setSessionId(response.session_id);
      
      const questionsResponse = await api.getCoreQuestions(response.session_id);
      setCoreQuestions(questionsResponse.questions);
      
      toast.success('Intelligent session started!');
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Failed to start session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCoreAnswer = async (questionId: string, answer: any) => {
    try {
      setFormData(prev => ({ ...prev, [questionId]: answer }));
      
      const response = await api.submitCoreAnswer(sessionId, questionId, answer);
      
      if (response.success) {
        setCoreComplete(response.core_complete);
        toast.success('Answer saved!');
      } else {
        toast.error('Failed to save answer');
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast.error('Failed to save answer');
    }
  };

  const generateFollowupQuestions = async () => {
    try {
      setIsLoading(true);
      
      // Prepare user answers from formData
      const userAnswers = formData;
      
      const response = await api.generateFollowupQuestions(userAnswers);
      
      // Transform string[] to Question[] objects
      const questionObjects: Question[] = response.questions.map((questionText, index) => ({
        id: `followup-${index}`,
        text: questionText,
        type: 'generated' as const,
        required: false
      }));
      
      setFollowupQuestions(questionObjects);
      setCurrentStep(1);
      toast.success(`Generated ${response.questions.length} follow-up questions!`);
    } catch (error) {
      console.error('Failed to generate follow-up questions:', error);
      toast.error('Failed to generate follow-up questions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowupAnswer = async (questionId: string, answer: any) => {
    try {
      setFollowupAnswers(prev => ({ ...prev, [questionId]: answer }));
      
      const response = await api.submitFollowupAnswer(sessionId, questionId, answer);
      
      if (response.success) {
        toast.success('Answer saved!');
      } else {
        toast.error('Failed to save answer');
      }
    } catch (error) {
      console.error('Failed to submit follow-up answer:', error);
      toast.error('Failed to save answer');
    }
  };

  const analyzeRequirements = async () => {
    try {
      setIsGenerating(true);
      const response = await api.analyzeIntelligentRequirements(sessionId);
      
      if (response.success) {
        setAnalysisResult(response);
        setCurrentStep(2);
        toast.success('Analysis completed successfully!');
        
        // Generate DSL from analysis
        const dsl = await generateDSLFromAnalysis(response);
        setCurrentDSL(dsl);
        
        addNotification({
          type: 'success',
          title: 'DSL Generated',
          message: 'Your backend specification has been created using intelligent analysis!'
        });
      } else {
        toast.error('Analysis failed');
      }
    } catch (error) {
      console.error('Failed to analyze requirements:', error);
      toast.error('Failed to analyze requirements');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateDSLFromAnalysis = async (analysis: AnalysisResult) => {
    // Create a comprehensive prompt from all the gathered data
    const prompt = `Create a comprehensive backend specification based on the following intelligent analysis:

PROJECT REQUIREMENTS:
${JSON.stringify(analysis.requirements_summary, null, 2)}

ANALYSIS INSIGHTS:
- Validity Score: ${analysis.analysis.validity_score}
- Valid: ${analysis.analysis.is_valid}

CONTEXT INSIGHTS:
${analysis.analysis.context_insights.map(insight => `- ${insight}`).join('\n')}

RECOMMENDATIONS:
${analysis.analysis.recommendations.map(rec => `- ${rec}`).join('\n')}

Generate a complete InfraNest DSL specification that addresses all these requirements and insights.`;

    try {
      const result = await api.parsePrompt(prompt);
      return result.dsl;
    } catch (error) {
      console.error('Failed to generate DSL:', error);
      // Return a basic DSL as fallback
      return {
        meta: {
          name: analysis.requirements_summary.project_description?.toLowerCase().replace(/\s+/g, '-') || 'intelligent-project',
          description: analysis.requirements_summary.project_description || 'Intelligently analyzed project',
          version: '1.0.0',
          framework: analysis.requirements_summary.technology_stack?.toLowerCase() || 'django',
          database: 'postgresql'
        },
        auth: {
          provider: 'jwt',
          user_model: 'User',
          required_fields: ['email', 'password']
        },
        models: {
          User: {
            fields: {
              id: { type: 'uuid', primary_key: true, auto_generated: true },
              email: { type: 'string', unique: true, required: true },
              password: { type: 'string', required: true, hashed: true }
            }
          }
        },
        api: {
          base_path: '/api/v1',
          endpoints: []
        }
      };
    }
  };

  const nextStep = () => {
    if (currentStep === 0 && coreComplete) {
      generateFollowupQuestions();
    } else if (currentStep === 1) {
      analyzeRequirements();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderCoreQuestions = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Core Questions</h2>
        <p className="text-gray-600">Answer these 6 essential questions to define your project</p>
      </div>

      {coreQuestions.map((question, index) => (
        <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-semibold">{index + 1}</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-900 mb-3">{question.text}</h3>
              
              {question.options ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {question.options.map((option) => (
                    <button
                      key={option}
                      onClick={() => handleCoreAnswer(question.id, option)}
                      className={`p-3 text-left border rounded-lg transition-colors ${
                        formData[question.id] === option
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              ) : question.id === 'mustHaveFeatures' ? (
                <div className="space-y-3">
                  <textarea
                    placeholder="List your must-have features (one per line)"
                    value={formData[question.id] || ''}
                    onChange={(e) => handleCoreAnswer(question.id, e.target.value.split('\n').filter(f => f.trim()))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                  />
                </div>
              ) : (
                <textarea
                  placeholder="Enter your answer..."
                  value={formData[question.id] || ''}
                  onChange={(e) => handleCoreAnswer(question.id, e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderFollowupQuestions = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI-Generated Follow-up Questions</h2>
        <p className="text-gray-600">These questions were generated by our AI to better understand your needs</p>
      </div>

      {followupQuestions.map((question) => (
        <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <Brain className="w-4 h-4 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-900 mb-3">{question.text}</h3>
              <textarea
                placeholder="Enter your answer..."
                value={followupAnswers[question.id] || ''}
                onChange={(e) => handleFollowupAnswer(question.id, e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows={3}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderAnalysisResults = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Intelligent Analysis Results</h2>
        <p className="text-gray-600">Your project has been analyzed and a DSL specification has been generated</p>
      </div>

      {analysisResult && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Analysis Overview */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Overview</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Validity Score</span>
                <span className={`font-semibold ${analysisResult.analysis.validity_score > 0.7 ? 'text-green-600' : 'text-yellow-600'}`}>
                  {(analysisResult.analysis.validity_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Status</span>
                <span className={`font-semibold ${analysisResult.analysis.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {analysisResult.analysis.is_valid ? 'Valid' : 'Needs Review'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Questions Answered</span>
                <span className="font-semibold">{analysisResult.metadata.total_questions_answered}</span>
              </div>
            </div>
          </div>

          {/* Context Insights */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Context Insights</h3>
            <ul className="space-y-2">
              {analysisResult.analysis.context_insights.map((insight, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{insight}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommendations */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
            <ul className="space-y-2">
              {analysisResult.analysis.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <ArrowRight className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Requirements Summary */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Summary</h3>
            <div className="space-y-3">
              <div>
                <span className="text-gray-600">Description:</span>
                <p className="font-medium">{analysisResult.requirements_summary.project_description}</p>
              </div>
              <div>
                <span className="text-gray-600">Platform:</span>
                <span className="ml-2 font-medium">{analysisResult.requirements_summary.platform}</span>
              </div>
              <div>
                <span className="text-gray-600">Technology:</span>
                <span className="ml-2 font-medium">{analysisResult.requirements_summary.technology_stack}</span>
              </div>
              <div>
                <span className="text-gray-600">Core Features:</span>
                <ul className="ml-4 mt-1">
                  {analysisResult.requirements_summary.core_features?.map((feature: string, index: number) => (
                    <li key={index} className="text-sm text-gray-700">• {feature}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (isLoading && !sessionId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Initializing intelligent session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  index === currentStep ? 'bg-blue-500 text-white' :
                  index < currentStep ? 'bg-green-500 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                  {index < currentStep ? <CheckCircle className="w-5 h-5" /> : step.icon}
                </div>
                <div className="ml-3 hidden sm:block">
                  <p className={`text-sm font-medium ${
                    index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                  <p className={`text-xs ${
                    index <= currentStep ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <ChevronRight className="w-5 h-5 text-gray-400 mx-4 hidden sm:block" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Current Step Content */}
        <div className="mb-8">
          {currentStep === 0 && renderCoreQuestions()}
          {currentStep === 1 && renderFollowupQuestions()}
          {currentStep === 2 && renderAnalysisResults()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <button
            onClick={nextStep}
            disabled={
              (currentStep === 0 && !coreComplete) ||
              (currentStep === 1 && followupQuestions.length === 0) ||
              isGenerating
            }
            className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating...</span>
              </>
            ) : currentStep === 2 ? (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Continue to Builder</span>
              </>
            ) : (
              <>
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default IntelligentQuestionFlow;


