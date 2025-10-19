import { Monitor } from 'lucide-react';

export const MobileWarning = () => {
  return (
    <div className="md:hidden fixed inset-0 bg-background z-50 flex items-center justify-center p-6">
      <div className="max-w-sm text-center">
        <Monitor className="w-20 h-20 text-error mx-auto mb-6" />

        <h1 className="text-2xl font-bold text-text-primary mb-4">
          Desktop Required
        </h1>

        <p className="text-text-secondary mb-6">
          For the full functionality of the Multi-Agent Retail Forecasting Dashboard,
          please access this application from a desktop or laptop computer.
        </p>

        <div className="bg-muted rounded-lg p-4 text-sm text-text-secondary">
          <p className="mb-2 font-semibold">Minimum Requirements:</p>
          <ul className="text-left space-y-1">
            <li>• Screen width: 1280px or wider</li>
            <li>• Modern web browser (Chrome, Firefox, Safari)</li>
            <li>• JavaScript enabled</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
