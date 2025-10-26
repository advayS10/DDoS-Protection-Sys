import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function CWatchLandingPage() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: 'https://cdn-icons-png.flaticon.com/512/2092/2092663.png',
      title: 'Advanced Threat Detection',
      description: 'Real-time monitoring and AI-powered threat detection to identify and neutralize cyber threats before they cause damage.',
    },
    {
      icon: 'https://cdn-icons-png.flaticon.com/512/1041/1041916.png',
      title: 'Lightning Fast Response',
      description: 'Automated incident response system that acts quickly to contain and eliminate security threats.',
    },
    {
      icon: 'https://cdn-icons-png.flaticon.com/512/2920/2920349.png',
      title: 'Real-Time Analytics',
      description: 'Comprehensive dashboard with actionable insights and detailed analytics of your security posture.',
    },
    {
      icon: 'https://cdn-icons-png.flaticon.com/512/3043/3043822.png',
      title: 'Network Protection',
      description: 'Multi-layered network security with protection, DDoS mitigation, and intrusion prevention.',
    },
  ];

  return (
    <div className="bg-black text-white font-sans overflow-x-hidden relative">
      {/* Animated Background for entire page */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400 rounded-full opacity-30 animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 10}s`,
              animationDuration: `${15 + Math.random() * 10}s`,
            }}
          />
        ))}
      </div>

      <style>
        {`
          html {
            scroll-behavior: smooth;
          }
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          @keyframes float {
            0%, 100% {
              transform: translate(0, 0) rotate(0deg);
            }
            25% {
              transform: translate(100px, 100px) rotate(90deg);
            }
            50% {
              transform: translate(200px, 50px) rotate(180deg);
            }
            75% {
              transform: translate(100px, 150px) rotate(270deg);
            }
          }
          .animate-fadeInUp {
            animation: fadeInUp 1s ease-out;
          }
          .animate-float {
            animation: float 20s infinite;
          }
          .hero-gradient {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
          }
          .text-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .btn-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
          }
          .card-gradient {
            background: linear-gradient(135deg, rgba(0, 255, 170, 0.05) 0%, rgba(0, 204, 255, 0.05) 100%);
          }
          .border-gradient {
            border-color: rgba(0, 255, 170, 0.2);
          }
          .filter-white {
            filter: brightness(0) invert(1);
          }
        `}
      </style>

      {/* Header */}
      {/* Header */}
      <header 
        className={`fixed top-0 w-full z-50 px-12 py-5 flex justify-between items-center transition-all duration-300 ${
          scrollY > 50 
            ? 'bg-black bg-opacity-95 backdrop-blur-lg border-b border-gradient' 
            : 'bg-transparent'
        }`}
      >
        <div className="text-3xl font-bold text-gradient tracking-wider">
          CWatch
        </div>
        <nav className="flex gap-10 items-center">
          <a 
            href="#about" 
            className="text-white text-base font-medium transition-colors duration-300 hover:text-cyan-400 cursor-pointer"
          >
            About
          </a>
          <a 
            href="#features" 
            className="text-white text-base font-medium transition-colors duration-300 hover:text-cyan-400 cursor-pointer"
          >
            Features
          </a>
          <a 
            href="#resources" 
            className="text-white text-base font-medium transition-colors duration-300 hover:text-cyan-400 cursor-pointer"
          >
            Resources
          </a>
          <Link 
            to="/dashboard"
            className="btn-gradient text-black px-8 py-3 text-base font-bold rounded-full transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-cyan-500/40 inline-block text-center"
          >
            Get Started
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden z-10" style={{background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)'}}>
        {/* Additional floating particles for hero section */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          {[...Array(25)].map((_, i) => (
            <div
              key={`hero-${i}`}
              className="absolute w-1 h-1 bg-cyan-400 rounded-full opacity-40 animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${15 + Math.random() * 10}s`,
              }}
            />
          ))}
        </div>
        
        {/* Hero Content */}
        <div className="text-center z-10 max-w-5xl px-5 animate-fadeInUp">
          {/* Shield Icon */}
          <div className="mb-10 flex justify-center">
            <div className="relative animate-pulse-slow">
              <svg 
                className="w-48 h-48 drop-shadow-2xl" 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor: '#00ffaa', stopOpacity: 1}} />
                    <stop offset="100%" style={{stopColor: '#00ccff', stopOpacity: 1}} />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <path 
                  d="M12 2L4 6V12C4 16.55 7.16 20.74 12 22C16.84 20.74 20 16.55 20 12V6L12 2Z" 
                  fill="url(#shieldGradient)" 
                  filter="url(#glow)"
                  opacity="0.9"
                />
                <path 
                  d="M10 14L8 12L7 13L10 16L17 9L16 8L10 14Z" 
                  fill="#000000" 
                  opacity="0.8"
                />
              </svg>
              {/* Glowing rings */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-52 h-52 border-2 border-cyan-400 rounded-full opacity-20 animate-ping-slow"></div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-60 h-60 border border-cyan-400 rounded-full opacity-10 animate-ping-slower"></div>
              </div>
            </div>
          </div>
          </div>
        <div className="text-center z-10 max-w-4xl px-5 animate-fadeInUp">
          <h1 className="text-7xl font-bold mb-5 text-gradient leading-tight">
            Advanced Cybersecurity Solutions
          </h1>
          <p className="text-2xl text-gray-400 mb-10 leading-relaxed">
            Protect your digital assets with cutting-edge AI-powered security. 
            Real-time threat detection and automated response for complete peace of mind.
          </p>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-32 px-12 relative z-10">
        <h2 className="text-5xl font-bold mb-5 text-center text-gradient">
          About CWatch
        </h2>
        <p className="text-xl text-gray-400 text-center mb-10 max-w-4xl mx-auto leading-relaxed">
          CWatch is a next-generation cybersecurity platform designed to protect modern enterprises 
          from evolving cyber threats. With cutting-edge AI technology and real-time monitoring, 
          we provide comprehensive security solutions that keep your digital infrastructure safe 24/7.
        </p>
        <p className="text-lg text-gray-400 text-center max-w-3xl mx-auto leading-relaxed">
          Our mission is to make enterprise-grade security accessible to organizations of all sizes, 
          combining advanced threat detection with intuitive management tools that empower your team 
          to stay ahead of cyber criminals.
        </p>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-12 relative z-10">
        <h2 className="text-5xl font-bold mb-5 text-center text-gradient">
          Comprehensive Security Features
        </h2>
        <p className="text-xl text-gray-400 text-center mb-20 max-w-3xl mx-auto">
          Everything you need to secure your infrastructure and protect against modern cyber threats
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card-gradient border border-gradient rounded-3xl p-10 transition-all duration-300 hover:-translate-y-3 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/50 cursor-pointer"
            >
              <img 
                src={feature.icon} 
                alt={feature.title} 
                className="w-20 h-20 mb-6 filter-white opacity-90"
              />
              <h3 className="text-2xl font-bold mb-4 text-white">
                {feature.title}
              </h3>
              <p className="text-base text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>
      {/* Resources Section */}
<section id = "resources" className="py-32 px-12 relative z-10">
  <h2 className="text-5xl font-bold mb-5 text-center text-gradient">
    Resources & Insights
  </h2>
  <p className="text-xl text-gray-400 text-center mb-20 max-w-3xl mx-auto">
    Stay informed with our latest research and security best practices
  </p>
  
  <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-6xl mx-auto">
    {/* DDoS Best Practices Card */}
    <div className="card-gradient border border-gradient rounded-3xl p-10 transition-all duration-300 hover:-translate-y-3 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/50 cursor-pointer">
      <div className="mb-6">
        <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Whitepaper</span>
      </div>
      <h3 className="text-2xl font-bold mb-4 text-white">
        Best Practices for Mitigating DDoS Attacks
      </h3>
      <p className="text-base text-gray-400 leading-relaxed mb-6">
        Learn how to defend against rapidly evolving distributed denial-of-service (DDoS) threats and address vulnerabilities at every layer.
      </p>
      <a href="https://www.cisa.gov/sites/default/files/publications/understanding-and-responding-to-ddos-attacks_508c.pdf" target="_blank" rel="noopener noreferrer">
  <button className="btn-gradient text-black px-6 py-3 text-sm font-bold rounded-full transition-all duration-300 hover:scale-105 shadow-lg">
    Get the Whitepaper
  </button>
</a>
    </div>

    {/* DDoS Activity Report Card */}
    <div className="card-gradient border border-gradient rounded-3xl p-10 transition-all duration-300 hover:-translate-y-3 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/50 cursor-pointer">
      <div className="mb-6">
        <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Annual Report</span>
      </div>
      <h3 className="text-2xl font-bold mb-4 text-white">
        DDoS Activity Report
      </h3>
      <p className="text-base text-gray-400 leading-relaxed mb-6">
        Comprehensive analysis of DDoS attack trends, patterns, and emerging threats observed throughout the year. Essential reading for security professionals.
      </p>
      <a href="https://blog.cloudflare.com/ddos-threat-report-for-2025-q1/" target="_blank" rel="noopener noreferrer">
  <button className="btn-gradient text-black px-6 py-3 text-sm font-bold rounded-full transition-all duration-300 hover:scale-105 shadow-lg">
    Check Report
  </button>
</a>
    </div>
  </div>
</section>
      {/* Footer */}
      <footer className="relative z-10 py-8 border-t border-gradient">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-500 text-sm">
            © 2025 CWatch. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}