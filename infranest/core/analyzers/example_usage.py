"""
Example usage of the Intelligent Question Generation System with GGUF files
"""

import os
from intelligent_analyzer import IntelligentAnalyzer

def main():
    # Path to your GGUF file
    # Replace this with the actual path to your Mistral 7B GGUF file
    mistral_gguf_path = r"D:\multiagent_system\model\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    # Check if file exists
    if not os.path.exists(mistral_gguf_path):
        print(f"GGUF file not found at: {mistral_gguf_path}")
        print("Please update the path to your actual GGUF file")
        print("The system will work with fallback questions if no model is provided")
        mistral_gguf_path = None
    
    # Initialize analyzer with GGUF model
    print("Initializing Intelligent Analyzer...")
    analyzer = IntelligentAnalyzer(mistral_gguf_path)
    
    # Start new session
    session_id = analyzer.start_new_session()
    print(f"Started session: {session_id}")
    
    # Get core questions
    print("\n=== CORE QUESTIONS ===")
    core_questions = analyzer.get_core_questions()
    for i, q in enumerate(core_questions, 1):
        print(f"{i}. {q['text']}")
        if 'options' in q:
            print(f"   Options: {', '.join(q['options'])}")
    
    # Simulate answering core questions
    print("\n=== ANSWERING CORE QUESTIONS ===")
    sample_responses = {
        'description': 'A task management web application for remote teams',
        'userAudience': 'My team',
        'platform': 'Website',
        'projectArea': 'Web app',
        'programmingLanguage': 'Python',
        'mustHaveFeatures': ['User authentication', 'Task creation and assignment', 'Team collaboration', 'Due date tracking', 'File attachments']
    }
    
    for q_id, answer in sample_responses.items():
        result = analyzer.submit_core_response(q_id, answer)
        print(f"  {q_id}: {'OK' if result['success'] else 'FAIL'}")
    
    # Generate follow-up questions using Mistral 7B
    print(f"\n=== GENERATING FOLLOW-UP QUESTIONS ===")
    print("Using Mistral 7B to generate contextual questions...")
    
    followup_result = analyzer.generate_followup_questions(5)
    
    if followup_result['success']:
        print(f"Generated {followup_result['count']} follow-up questions:")
        for i, q in enumerate(followup_result['questions'], 1):
            print(f"  {i}. {q['text']}")
    else:
        print(f"Failed to generate questions: {followup_result['message']}")
    
    # Simulate answering some follow-up questions
    print("\n=== ANSWERING FOLLOW-UP QUESTIONS ===")
    if followup_result['success'] and len(followup_result['questions']) >= 3:
        sample_followup_answers = {
            followup_result['questions'][0]['id']: 'Yes, real-time updates would be very helpful',
            followup_result['questions'][1]['id']: 'We need admin, manager, and team member roles',
            followup_result['questions'][2]['id']: 'Yes, we need to integrate with Slack and Google Calendar'
        }
        
        for q_id, answer in sample_followup_answers.items():
            result = analyzer.submit_followup_response(q_id, answer)
            print(f"  {q_id}: {'OK' if result['success'] else 'FAIL'}")
    
    # Perform comprehensive analysis
    print("\n=== PERFORMING ANALYSIS ===")
    analysis_result = analyzer.analyze_requirements()
    
    if analysis_result['success']:
        print("Analysis completed successfully!")
        print(f"Validity Score: {analysis_result['analysis']['validity_score']:.2f}")
        print(f"Is Valid: {analysis_result['analysis']['is_valid']}")
        
        print(f"\nGenerated Insights ({len(analysis_result['analysis']['insights'])}):")
        for insight in analysis_result['analysis']['insights']:
            print(f"  • {insight}")
        
        print(f"\nContext Insights ({len(analysis_result['analysis']['context_insights'])}):")
        for insight in analysis_result['analysis']['context_insights']:
            print(f"  • {insight}")
        
        print(f"\nRecommendations ({len(analysis_result['analysis']['recommendations'])}):")
        for rec in analysis_result['analysis']['recommendations']:
            print(f"  • {rec}")
        
        print(f"\nRequirements Summary:")
        summary = analysis_result['requirements_summary']
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
    else:
        print(f"Analysis failed: {analysis_result['message']}")
    
    # Show session status
    print(f"\n=== SESSION STATUS ===")
    status = analyzer.get_session_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
