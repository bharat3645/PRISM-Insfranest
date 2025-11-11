"""
Agentic Analyzer with Generator and Discriminator
Generates system insights and validates requirements
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Tuple
import json
import yaml

class RequirementsGenerator(nn.Module):
    """Generator: Requirements → Analysis"""
    
    def __init__(self, input_dim: int = 512, hidden_dim: int = 1024, output_dim: int = 256):
        super().__init__()
        
        # Encoder layers
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU()
        )
        
        # Self-attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim // 2,
            num_heads=8,
            dropout=0.1,
            batch_first=True
        )
        
        # Decoder layers
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid()
        )
        
    def forward(self, requirements: torch.Tensor) -> torch.Tensor:
        # Encode requirements
        encoded = self.encoder(requirements)
        
        # Apply self-attention
        attended, _ = self.attention(encoded, encoded, encoded)
        
        # Decode to analysis
        analysis = self.decoder(attended)
        return analysis

class AnalysisDiscriminator(nn.Module):
    """Discriminator: Valid/Invalid Analysis"""
    
    def __init__(self, input_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
    def forward(self, analysis: torch.Tensor) -> torch.Tensor:
        return self.classifier(analysis)

class AgenticAnalyzer:
    """Main Agentic Analyzer combining Generator and Discriminator"""
    
    def __init__(self):
        self.generator = RequirementsGenerator()
        self.discriminator = AnalysisDiscriminator()
        self.optimizer_g = torch.optim.Adam(self.generator.parameters(), lr=0.0002)
        self.optimizer_d = torch.optim.Adam(self.discriminator.parameters(), lr=0.0002)
        self.criterion = nn.BCELoss()
        
    def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements and generate system insights"""
        
        # Convert requirements to tensor
        req_vector = self._requirements_to_vector(requirements)
        
        # Generate analysis
        with torch.no_grad():
            analysis_vector = self.generator(req_vector)
            analysis = self._vector_to_analysis(analysis_vector)
        
        # Validate analysis
        validity_score = self.discriminator(analysis_vector).item()
        
        return {
            'analysis': analysis,
            'validity_score': validity_score,
            'is_valid': validity_score > 0.5,
            'insights': self._generate_insights(analysis, requirements)
        }
    
    def _requirements_to_vector(self, requirements: Dict[str, Any]) -> torch.Tensor:
        """Convert requirements to numerical vector"""
        # Feature extraction from requirements
        features = []
        
        # Project complexity
        complexity = len(requirements.get('must_have_features', []))
        features.append(min(complexity / 10.0, 1.0))
        
        # User audience scale
        audience = requirements.get('user_audience', 'My team')
        audience_scale = {'Just me': 0.1, 'My team': 0.5, 'My customers': 1.0}.get(audience, 0.5)
        features.append(audience_scale)
        
        # Platform complexity
        platform = requirements.get('platform', 'Website')
        platform_complexity = {'Website': 0.3, 'Mobile app': 0.7, 'Desktop': 0.5, 'Chatbot': 0.8}.get(platform, 0.3)
        features.append(platform_complexity)
        
        # Project area complexity
        area = requirements.get('project_area', 'Web app')
        area_complexity = {
            'Web app': 0.3, 'E-commerce': 0.8, 'Healthcare': 0.9, 
            'Finance': 0.9, 'Education': 0.6, 'Analytics': 0.7
        }.get(area, 0.3)
        features.append(area_complexity)
        
        # Security requirements
        security_level = requirements.get('security_level', 'standard')
        security_score = {'basic': 0.2, 'standard': 0.5, 'high': 0.9}.get(security_level, 0.5)
        features.append(security_score)
        
        # Pad to required dimension
        while len(features) < 512:
            features.append(0.0)
        
        return torch.tensor(features[:512], dtype=torch.float32).unsqueeze(0)
    
    def _vector_to_analysis(self, vector: torch.Tensor) -> Dict[str, Any]:
        """Convert analysis vector to structured analysis"""
        vector_np = vector.squeeze().numpy()
        
        return {
            'complexity_score': float(vector_np[0]),
            'scalability_requirements': float(vector_np[1]),
            'security_level': float(vector_np[2]),
            'performance_requirements': float(vector_np[3]),
            'integration_complexity': float(vector_np[4]),
            'maintenance_effort': float(vector_np[5]),
            'deployment_complexity': float(vector_np[6]),
            'monitoring_requirements': float(vector_np[7])
        }
    
    def _generate_insights(self, analysis: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from analysis"""
        insights = []
        
        if analysis['complexity_score'] > 0.7:
            insights.append("High complexity project requiring experienced development team")
        
        if analysis['scalability_requirements'] > 0.8:
            insights.append("High scalability requirements - consider microservices architecture")
        
        if analysis['security_level'] > 0.8:
            insights.append("High security requirements - implement comprehensive security measures")
        
        if analysis['performance_requirements'] > 0.7:
            insights.append("High performance requirements - optimize for speed and efficiency")
        
        if analysis['integration_complexity'] > 0.6:
            insights.append("Complex integration requirements - plan for API management")
        
        if analysis['deployment_complexity'] > 0.7:
            insights.append("Complex deployment requirements - consider containerization and orchestration")
        
        return insights
    
    def train_step(self, real_requirements: List[Dict[str, Any]], fake_requirements: List[Dict[str, Any]]):
        """Train the generator and discriminator"""
        # Train discriminator
        self.optimizer_d.zero_grad()
        
        # Real data
        real_vectors = torch.stack([self._requirements_to_vector(req) for req in real_requirements])
        real_labels = torch.ones(len(real_requirements), 1)
        real_pred = self.discriminator(self.generator(real_vectors))
        real_loss = self.criterion(real_pred, real_labels)
        
        # Fake data
        fake_vectors = torch.stack([self._requirements_to_vector(req) for req in fake_requirements])
        fake_labels = torch.zeros(len(fake_requirements), 1)
        fake_pred = self.discriminator(self.generator(fake_vectors))
        fake_loss = self.criterion(fake_pred, fake_labels)
        
        d_loss = real_loss + fake_loss
        d_loss.backward()
        self.optimizer_d.step()
        
        # Train generator
        self.optimizer_g.zero_grad()
        
        fake_vectors = torch.stack([self._requirements_to_vector(req) for req in fake_requirements])
        fake_labels = torch.ones(len(fake_requirements), 1)  # Fool discriminator
        fake_pred = self.discriminator(self.generator(fake_vectors))
        g_loss = self.criterion(fake_pred, fake_labels)
        
        g_loss.backward()
        self.optimizer_g.step()
        
        return {
            'generator_loss': g_loss.item(),
            'discriminator_loss': d_loss.item()
        }
