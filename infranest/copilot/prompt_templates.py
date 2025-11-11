"""
InfraNest Prompt Templates
Dynamic prompt generation based on user answers and project context
"""

from typing import Dict, Any, List
import json


class PromptTemplate:
    """Base class for prompt templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load all prompt templates"""
        return {
            "base_template": self._get_base_template(),
            "domain_templates": self._get_domain_templates(),
            "platform_templates": self._get_platform_templates(),
            "framework_templates": self._get_framework_templates(),
            "security_templates": self._get_security_templates(),
            "scale_templates": self._get_scale_templates()
        }
    
    def _get_base_template(self) -> str:
        """Base template structure"""
        return """Create a {framework} backend API for: {description}

**Project Details:**
- Name: {name}
- Description: {description}
- User Audience: {user_audience}
- Platform: {platform}
- Project Area: {project_area}
- Framework: {framework}
- Database: {database}
- Authentication: {auth_type}

**Must-Have Features:**
{features}

{domain_specific_requirements}

{platform_specific_requirements}

{framework_specific_requirements}

{security_requirements}

{scale_requirements}

**Technical Requirements:**
- API Style: {api_style}
- Rate limiting: {rate_limiting}
- Caching: {caching}
- Pagination: {pagination}

**Deployment:**
- Target: {deployment_target}

{followup_clarifications}

Generate production-ready code with proper error handling, validation, documentation, and following {framework} best practices for a {project_area} application."""

    def _get_domain_templates(self) -> Dict[str, str]:
        """Domain-specific template additions"""
        return {
            "ecommerce": """
**E-commerce Specific Requirements:**
- Product catalog with categories and search
- Shopping cart and checkout flow
- Order management and tracking
- Payment gateway integration
- Inventory management
- Customer reviews and ratings""",
            
            "healthcare": """
**Healthcare Specific Requirements:**
- Patient data management (HIPAA compliant)
- Appointment scheduling system
- Medical records management
- Prescription tracking
- Doctor-patient communication
- Insurance verification""",
            
            "finance": """
**Finance Specific Requirements:**
- Transaction processing and history
- Account management
- Multi-currency support
- Financial reporting and analytics
- Fraud detection
- Regulatory compliance""",
            
            "education": """
**Education Specific Requirements:**
- Course management system
- Student enrollment and progress tracking
- Assignment and grading system
- Learning management features
- Teacher-student communication
- Certificate generation""",
            
            "analytics": """
**Analytics Specific Requirements:**
- Data collection and processing
- Real-time dashboards
- Custom report generation
- Data export capabilities
- Visualization components
- Performance metrics tracking""",
            
            "iot": """
**IoT Specific Requirements:**
- Device management and monitoring
- Real-time data streaming
- Sensor data processing
- Alert and notification system
- Device authentication
- Data aggregation and analysis"""
        }
    
    def _get_platform_templates(self) -> Dict[str, str]:
        """Platform-specific template additions"""
        return {
            "mobile": """
**Mobile App Specific Requirements:**
- Push notification system
- Offline data synchronization
- Mobile-optimized API responses
- Image and media handling
- Location services integration
- Mobile authentication flow""",
            
            "website": """
**Web Application Specific Requirements:**
- Responsive design support
- SEO-friendly API structure
- WebSocket support for real-time features
- File upload and management
- Cross-browser compatibility
- Progressive Web App features""",
            
            "desktop": """
**Desktop Application Specific Requirements:**
- Local data storage
- System integration capabilities
- Offline functionality
- Native OS features integration
- Auto-update mechanism
- System tray integration""",
            
            "chatbot": """
**Chatbot Specific Requirements:**
- Natural language processing
- Conversation state management
- Integration with messaging platforms
- Context-aware responses
- Multi-language support
- Analytics and conversation tracking"""
        }
    
    def _get_framework_templates(self) -> Dict[str, str]:
        """Framework-specific template additions"""
        return {
            "django": """
**Django Best Practices:**
- Use Django REST Framework for API endpoints
- Implement proper model relationships and constraints
- Use Django's built-in authentication system
- Follow Django's security guidelines
- Implement proper serialization and validation
- Use Django's admin interface for data management""",
            
            "nodejs": """
**Node.js Best Practices:**
- Use Express.js or Fastify for the web framework
- Implement proper middleware for authentication and validation
- Use TypeScript for type safety
- Follow RESTful API design principles
- Implement proper error handling and logging
- Use environment variables for configuration""",
            
            "spring": """
**Spring Boot Best Practices:**
- Use Spring Security for authentication and authorization
- Implement proper exception handling with @ControllerAdvice
- Use Spring Data JPA for database operations
- Follow Spring's dependency injection patterns
- Implement proper validation with Bean Validation
- Use Spring Boot Actuator for monitoring""",
            
            "go-fiber": """
**Go Fiber Best Practices:**
- Use GORM for database operations
- Implement proper middleware for authentication
- Use structured logging
- Follow Go's error handling patterns
- Implement proper request validation
- Use Go's context package for request lifecycle""",
            
            "rust": """
**Rust Best Practices:**
- Use Actix-web or Axum for the web framework
- Implement proper error handling with Result types
- Use Diesel or SQLx for database operations
- Follow Rust's ownership and borrowing rules
- Implement proper serialization with serde
- Use tokio for async runtime"""
        }
    
    def _get_security_templates(self) -> Dict[str, str]:
        """Security-specific template additions"""
        return {
            "high": """
**High Security Requirements:**
- End-to-end encryption for sensitive data
- Multi-factor authentication
- Role-based access control (RBAC)
- Audit logging for all operations
- Data anonymization capabilities
- Compliance with industry standards (HIPAA, PCI-DSS)""",
            
            "standard": """
**Standard Security Requirements:**
- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- CORS configuration
- Rate limiting and throttling
- HTTPS enforcement""",
            
            "basic": """
**Basic Security Requirements:**
- Simple authentication system
- Basic input validation
- Environment variable configuration
- Basic error handling
- CORS setup"""
        }
    
    def _get_scale_templates(self) -> Dict[str, str]:
        """Scale-specific template additions"""
        return {
            "small": """
**Small Scale Requirements:**
- Single server deployment
- Basic caching with Redis
- Simple database setup
- Basic monitoring
- Cost-effective solutions""",
            
            "medium": """
**Medium Scale Requirements:**
- Load balancing capabilities
- Database replication
- Caching strategies
- Monitoring and logging
- Auto-scaling preparation""",
            
            "large": """
**Large Scale Requirements:**
- Microservices architecture
- Database sharding
- Advanced caching strategies
- Comprehensive monitoring
- Auto-scaling and load balancing
- CDN integration"""
        }
    
    def generate_prompt(self, requirements: Dict[str, Any]) -> str:
        """Generate a dynamic prompt based on user requirements"""
        
        # Get base template
        template = self.templates["base_template"]
        
        # Prepare context variables
        context = {
            "framework": requirements.get("framework", "django"),
            "description": requirements.get("description", ""),
            "name": requirements.get("name", "my-project"),
            "user_audience": requirements.get("user_audience", "My team"),
            "platform": requirements.get("platform", "Website"),
            "project_area": requirements.get("project_area", "Web app"),
            "database": requirements.get("database", "postgresql"),
            "auth_type": requirements.get("auth_type", "jwt"),
            "api_style": requirements.get("api_style", "rest"),
            "rate_limiting": "Yes" if requirements.get("rate_limiting", True) else "No",
            "caching": "Yes" if requirements.get("caching", True) else "No",
            "pagination": "Yes" if requirements.get("pagination", True) else "No",
            "deployment_target": requirements.get("deployment_target", "cloud")
        }
        
        # Add features
        features = requirements.get("must_have_features", [])
        if features:
            context["features"] = "\n".join([f"- {feature}" for feature in features])
        else:
            context["features"] = "- Basic CRUD operations\n- User authentication"
        
        # Add domain-specific requirements
        project_area = requirements.get("project_area", "").lower()
        domain_template = self.templates["domain_templates"].get(project_area, "")
        context["domain_specific_requirements"] = domain_template
        
        # Add platform-specific requirements
        platform = requirements.get("platform", "").lower()
        platform_template = self.templates["platform_templates"].get(platform, "")
        context["platform_specific_requirements"] = platform_template
        
        # Add framework-specific requirements
        framework = requirements.get("framework", "django")
        framework_template = self.templates["framework_templates"].get(framework, "")
        context["framework_specific_requirements"] = framework_template
        
        # Add security requirements
        security_level = requirements.get("security_level", "standard")
        security_template = self.templates["security_templates"].get(security_level, "")
        context["security_requirements"] = security_template
        
        # Add scale requirements
        expected_users = requirements.get("expected_users", 50)
        if expected_users <= 10:
            scale = "small"
        elif expected_users <= 1000:
            scale = "medium"
        else:
            scale = "large"
        
        scale_template = self.templates["scale_templates"].get(scale, "")
        context["scale_requirements"] = scale_template
        
        # Add follow-up clarifications
        followup_clarifications = self._generate_followup_clarifications(requirements)
        context["followup_clarifications"] = followup_clarifications
        
        # Format the template with context
        return template.format(**context)
    
    def _generate_followup_clarifications(self, requirements: Dict[str, Any]) -> str:
        """Generate follow-up clarifications section"""
        followup_questions = requirements.get("_followup_questions", [])
        followup_answers = {}
        
        # Extract follow-up answers
        for key, value in requirements.items():
            if key.startswith("followup_") and key != "_followup_questions":
                followup_answers[key] = value
        
        if not followup_questions or not followup_answers:
            return ""
        
        clarifications = ["**Follow-up Clarifications:**"]
        for i, question in enumerate(followup_questions, 1):
            answer_key = f"followup_{i}"
            if answer_key in followup_answers:
                clarifications.append(f"- {question}: {followup_answers[answer_key]}")
        
        return "\n".join(clarifications)
    
    def get_template_preview(self, requirements: Dict[str, Any]) -> str:
        """Get a preview of what the generated prompt will look like"""
        return self.generate_prompt(requirements)
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """Get list of available templates for each category"""
        return {
            "domains": list(self.templates["domain_templates"].keys()),
            "platforms": list(self.templates["platform_templates"].keys()),
            "frameworks": list(self.templates["framework_templates"].keys()),
            "security_levels": list(self.templates["security_templates"].keys()),
            "scales": list(self.templates["scale_templates"].keys())
        }


# Global template instance
prompt_template = PromptTemplate()

