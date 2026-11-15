import React from "react";

export default function Header({ title, subtitle, badge }) {
  return (
    <div className="mb-2 animate-fade-in">
      <div className="flex flex-wrap items-center gap-3 mb-1.5">
        <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">{title}</h1>
        {badge}
      </div>
      {subtitle && <p className="text-sm text-slate-400 max-w-2xl">{subtitle}</p>}
    </div>
  );
}
