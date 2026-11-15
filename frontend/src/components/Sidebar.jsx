import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  TrendingUp,
  GitCompareArrows,
  Brain,
  FlaskConical,
  Menu,
  X,
  ShieldCheck,
  BookOpen,
  Leaf,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Budget Explorer", icon: TrendingUp, end: true },
  { to: "/sdg", label: "SDG View", icon: Leaf },
  { to: "/guide", label: "How to use / Glossary", icon: BookOpen },
];
const MORE_ITEMS = [
  { to: "/overview", label: "Research summary", icon: LayoutDashboard },
  { to: "/model-performance", label: "Model performance", icon: GitCompareArrows },
  { to: "/explainable-ai", label: "Detailed explanations", icon: Brain },
  { to: "/methodology", label: "Methodology", icon: FlaskConical },
];

function NavItem({ to, label, icon: Icon, end, onNavigate }) {
  return (
    <NavLink
      to={to}
      end={end}
      onClick={onNavigate}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
          isActive
            ? "bg-gradient-to-r from-cyan-500/15 to-teal-500/10 text-cyan-300 ring-1 ring-cyan-500/20 shadow-glow"
            : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
        }`
      }
    >
      <Icon className="w-4 h-4 shrink-0" strokeWidth={2} />
      <span>{label}</span>
    </NavLink>
  );
}

function SidebarContent({ onNavigate }) {
  return (
    <div className="flex flex-col h-full">
      <div className="px-5 pt-6 pb-5 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center shadow-glow shrink-0">
            <ShieldCheck className="w-5 h-5 text-navy-950" strokeWidth={2.5} />
          </div>
          <div className="leading-tight">
            <div className="font-bold text-white tracking-tight text-[15px]">GovAllocXAI</div>
            <div className="text-[11px] text-slate-400">Government Budget Intelligence</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((i) => <NavItem key={i.to} {...i} onNavigate={onNavigate} />)}
        <div className="px-3 pt-5 pb-1 text-[10px] font-semibold tracking-widest uppercase text-slate-500">More details (optional)</div>
        {MORE_ITEMS.map((i) => <NavItem key={i.to} {...i} onNavigate={onNavigate} />)}
      </nav>

      <div className="px-4 py-5 border-t border-white/[0.06] space-y-2">
        <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wide uppercase text-cyan-400/80">
          <Brain className="w-3.5 h-3.5" />
          AI Decision Support System
        </div>
        <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wide uppercase text-amber-400/80">
          <ShieldCheck className="w-3.5 h-3.5" />
          Human Approval Required
        </div>
      </div>
    </div>
  );
}

export default function Sidebar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-col w-64 shrink-0 h-screen sticky top-0 bg-navy-900/80 border-r border-white/[0.06] backdrop-blur-md">
        <SidebarContent />
      </aside>

      {/* Mobile top bar */}
      <div className="lg:hidden sticky top-0 z-40 flex items-center justify-between px-4 py-3 bg-navy-900/90 backdrop-blur-md border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-navy-950" strokeWidth={2.5} />
          </div>
          <span className="font-bold text-white text-sm">GovAllocXAI</span>
        </div>
        <button
          onClick={() => setOpen(true)}
          className="p-2 rounded-lg text-slate-300 hover:bg-white/[0.06]"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div className="relative w-72 max-w-[80%] bg-navy-900 border-r border-white/[0.08] animate-slide-up">
            <button
              onClick={() => setOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:bg-white/[0.06]"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
            <SidebarContent onNavigate={() => setOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
