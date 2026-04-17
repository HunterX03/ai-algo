import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, TrendingUp, Layers, Activity, Shield, Newspaper, Clock, Zap } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  const navItems = [
    { path: '/', icon: BarChart3, label: 'Command Center' },
    { path: '/deep-dive', icon: TrendingUp, label: 'Stock Deep Dive' },
    { path: '/strategy-lab', icon: Layers, label: 'Strategy Lab' },
    { path: '/backtest', icon: Activity, label: 'Backtest Suite' },
    { path: '/risk', icon: Shield, label: 'Risk Manager' },
    { path: '/sentiment', icon: Newspaper, label: 'Sentiment Hub' },
    { path: '/intraday', icon: Clock, label: 'Intraday Monitor' },
    { path: '/quant', icon: Zap, label: 'Quant Engine' },
  ];
  
  return (
    <div className="w-64 bg-[#111827] border-r border-[#1F2937] h-screen flex flex-col" data-testid="sidebar">
      <div className="p-6 border-b border-[#1F2937]">
        <h1 className="text-xl font-semibold text-[#F9FAFB] font-mono" data-testid="app-title">JPM-SwingEdge</h1>
        <p className="text-xs text-[#6B7280] mt-1 font-mono">QUANTITATIVE TRADING</p>
      </div>
      
      <nav className="flex-1 p-4" data-testid="nav-menu">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium
                  transition-colors duration-150
                  ${
                    active
                      ? 'bg-[#3B82F6]/10 text-[#3B82F6] border-l-2 border-[#3B82F6]'
                      : 'text-[#9CA3AF] hover:text-[#F9FAFB] hover:bg-[#1F2937]/50'
                  }
                `}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
      
      <div className="p-4 border-t border-[#1F2937]">
        <div className="text-xs text-[#6B7280] font-mono">
          <p>© 2025 JPM-SwingEdge Pro</p>
          <p className="mt-1">Signal Generation Platform</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;