import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Guide from "./pages/Guide";
import SdgView from "./pages/SdgView";
import { ResultProvider } from "./state/ResultContext";
import ModelPerformance from "./pages/ModelPerformance";
import ExplainableAI from "./pages/ExplainableAI";
import Methodology from "./pages/Methodology";

export default function App() {

  return (
    <ResultProvider>
    <HashRouter future={{ v7_startTransition: true }}>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 min-w-0 px-5 py-8 md:px-10 md:py-10 animate-fade-in">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/guide" element={<Guide />} />
            <Route path="/sdg" element={<SdgView />} />
            <Route path="/overview" element={<Dashboard />} />
            <Route path="/model-performance" element={<ModelPerformance />} />
            <Route path="/explainable-ai" element={<ExplainableAI />} />
            <Route path="/methodology" element={<Methodology />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
    </ResultProvider>
  );
}
