import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { SeasonParameters } from '@/types/parameters';

interface ParametersContextType {
  parameters: SeasonParameters | null;
  setParameters: (params: SeasonParameters) => void;
  clearParameters: () => void;
}

const ParametersContext = createContext<ParametersContextType | undefined>(
  undefined
);

export function ParametersProvider({ children }: { children: ReactNode }) {
  const [parameters, setParameters] = useState<SeasonParameters | null>(null);

  return (
    <ParametersContext.Provider
      value={{
        parameters,
        setParameters,
        clearParameters: () => setParameters(null),
      }}
    >
      {children}
    </ParametersContext.Provider>
  );
}

export function useParameters() {
  const context = useContext(ParametersContext);
  if (!context) {
    throw new Error('useParameters must be used within ParametersProvider');
  }
  return context;
}
