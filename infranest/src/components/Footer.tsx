import React from 'react';
import { 
  Github, 
  Twitter, 
  Linkedin, 
  Mail, 
  Heart, 
  Code, 
  Zap,
  ExternalLink,
  BookOpen,
  MessageCircle,
  Shield,
  Globe
} from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = 2025;

  const footerLinks = {
    product: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Documentation', href: '#docs', icon: BookOpen },
      { label: 'API Reference', href: '#api', icon: Code },
      { label: 'Examples', href: '#examples' },
      { label: 'Changelog', href: '#changelog' }
    ],
    company: [
      { label: 'About', href: '#about' },
      { label: 'Blog', href: '#blog' },
      { label: 'Careers', href: '#careers' },
      { label: 'Contact', href: '#contact', icon: Mail },
      { label: 'Press Kit', href: '#press' },
      { label: 'Partners', href: '#partners' }
    ],
    developers: [
      { label: 'GitHub', href: 'https://github.com/infranest', icon: Github, external: true },
      { label: 'Discord', href: '#discord', icon: MessageCircle },
      { label: 'Stack Overflow', href: '#stackoverflow', external: true },
      { label: 'CLI Tools', href: '#cli', icon: Zap },
      { label: 'SDKs', href: '#sdks' },
      { label: 'Integrations', href: '#integrations' }
    ],
    legal: [
      { label: 'Privacy Policy', href: '#privacy', icon: Shield },
      { label: 'Terms of Service', href: '#terms' },
      { label: 'Cookie Policy', href: '#cookies' },
      { label: 'Security', href: '#security', icon: Shield },
      { label: 'Compliance', href: '#compliance' },
      { label: 'GDPR', href: '#gdpr' }
    ]
  };

  const socialLinks = [
    { icon: Github, href: 'https://github.com/infranest', label: 'GitHub' },
    { icon: Twitter, href: 'https://twitter.com/infranest', label: 'Twitter' },
    { icon: Linkedin, href: 'https://linkedin.com/company/infranest', label: 'LinkedIn' },
    { icon: Mail, href: 'mailto:hello@infranest.dev', label: 'Email' }
  ];

  const frameworks = [
    { name: 'Django', color: 'text-green-400' },
    { name: 'Go Fiber', color: 'text-blue-400' },
    { name: 'Rails', color: 'text-red-400' },
    { name: 'FastAPI', color: 'text-purple-400' },
    { name: 'Express', color: 'text-yellow-400' }
  ];

  return (
    <footer className="relative bg-black border-t border-gray-800 text-white mt-auto">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-6 md:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-3 mb-6">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-[#00ff88] to-[#00ccff] rounded-lg flex items-center justify-center">
                  <Code className="w-6 h-6 text-black" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#00ff88] rounded-full animate-pulse"></div>
              </div>
              <div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-[#00ff88] to-[#00ccff] bg-clip-text text-transparent">
                  InfraNest
                </h3>
                <p className="text-xs text-gray-400 font-mono">v2.0.0-beta</p>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-6 leading-relaxed">
              AI-powered backend generation platform. Transform natural language into production-ready APIs in minutes.
            </p>
            
            {/* Supported Frameworks */}
            <div className="mb-6">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Supported Frameworks</p>
              <div className="flex flex-wrap gap-2">
                {frameworks.map((framework, index) => (
                  <span
                    key={index}
                    className={`px-2 py-1 bg-[#1a1a1a] border border-[#333333] rounded text-xs ${framework.color}`}
                  >
                    {framework.name}
                  </span>
                ))}
              </div>
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-3">
              {socialLinks.map((social, index) => {
                const Icon = social.icon;
                return (
                  <a
                    key={index}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-[#1a1a1a] border border-[#333333] hover:border-[#00ff88] hover:bg-[#00ff88]/10 rounded-lg transition-all group"
                    title={social.label}
                  >
                    <Icon className="w-4 h-4 text-gray-400 group-hover:text-[#00ff88]" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="font-semibold text-white mb-4 flex items-center space-x-2">
              <Zap className="w-4 h-4 text-[#00ff88]" />
              <span>Product</span>
            </h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link, index) => {
                const Icon = link.icon;
                return (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-[#00ff88] text-sm transition-colors flex items-center space-x-2 group"
                    >
                      {Icon && <Icon className="w-3 h-3 group-hover:text-[#00ff88]" />}
                      <span>{link.label}</span>
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="font-semibold text-white mb-4 flex items-center space-x-2">
              <Globe className="w-4 h-4 text-[#00ccff]" />
              <span>Company</span>
            </h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link, index) => {
                const Icon = link.icon;
                return (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-[#00ccff] text-sm transition-colors flex items-center space-x-2 group"
                    >
                      {Icon && <Icon className="w-3 h-3 group-hover:text-[#00ccff]" />}
                      <span>{link.label}</span>
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Developers Links */}
          <div>
            <h4 className="font-semibold text-white mb-4 flex items-center space-x-2">
              <Code className="w-4 h-4 text-purple-400" />
              <span>Developers</span>
            </h4>
            <ul className="space-y-3">
              {footerLinks.developers.map((link, index) => {
                const Icon = link.icon;
                return (
                  <li key={index}>
                    <a
                      href={link.href}
                      target={link.external ? "_blank" : undefined}
                      rel={link.external ? "noopener noreferrer" : undefined}
                      className="text-gray-400 hover:text-purple-400 text-sm transition-colors flex items-center space-x-2 group"
                    >
                      {Icon && <Icon className="w-3 h-3 group-hover:text-purple-400" />}
                      <span>{link.label}</span>
                      {link.external && <ExternalLink className="w-3 h-3 opacity-50" />}
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="font-semibold text-white mb-4 flex items-center space-x-2">
              <Shield className="w-4 h-4 text-[#ffaa00]" />
              <span>Legal</span>
            </h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link, index) => {
                const Icon = link.icon;
                return (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-[#ffaa00] text-sm transition-colors flex items-center space-x-2 group"
                    >
                      {Icon && <Icon className="w-3 h-3 group-hover:text-[#ffaa00]" />}
                      <span>{link.label}</span>
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-800 bg-black">
        <div className="max-w-7xl mx-auto px-6 md:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span>© {currentYear} InfraNest. All rights reserved.</span>
              <div className="hidden md:flex items-center space-x-1">
                <span>Made with</span>
                <Heart className="w-4 h-4 text-[#ff4444] animate-pulse" />
                <span>for developers</span>
              </div>
            </div>

            {/* Status & Stats */}
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-[#00ff88] rounded-full animate-pulse"></div>
                <span className="text-gray-400">All systems operational</span>
              </div>
              <div className="hidden md:flex items-center space-x-4 text-gray-500">
                <span>1.2M+ APIs generated</span>
                <span>•</span>
                <span>99.9% uptime</span>
                <span>•</span>
                <span>24/7 support</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subtle Background Effect */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-5">
        <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/10 via-transparent to-transparent"></div>
      </div>
    </footer>
  );
};

export default Footer;