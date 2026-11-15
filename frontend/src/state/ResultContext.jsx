import React, { createContext, useContext, useState } from "react";

// Keeps the latest recommendation so that the SDG view can reuse it without a new request.
const Ctx = createContext({ shared: null, setShared: () => {} });

export function ResultProvider({ children }) {
  const [shared, setShared] = useState(null);
  return <Ctx.Provider value={{ shared, setShared }}>{children}</Ctx.Provider>;
}

export const useSharedResult = () => useContext(Ctx);
