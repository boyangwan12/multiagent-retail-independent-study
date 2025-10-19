import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import type { ToastType } from './ToastContainer';

interface ToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
}

const toastConfig = {
  success: {
    icon: CheckCircle2,
    bgColor: 'bg-success/10',
    borderColor: 'border-success',
    textColor: 'text-success',
  },
  error: {
    icon: AlertCircle,
    bgColor: 'bg-error/10',
    borderColor: 'border-error',
    textColor: 'text-error',
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-warning/10',
    borderColor: 'border-warning',
    textColor: 'text-warning',
  },
  info: {
    icon: Info,
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    textColor: 'text-primary',
  },
};

export const Toast = ({ type, message, onClose }: ToastProps) => {
  const config = toastConfig[type];
  const Icon = config.icon;

  return (
    <div
      role="status"
      className={`
        ${config.bgColor} ${config.borderColor}
        border rounded-lg p-4 pr-12 shadow-lg
        min-w-[320px] max-w-md
        animate-in slide-in-from-right-full
        relative
      `}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 ${config.textColor} flex-shrink-0 mt-0.5`} />
        <p className="text-sm text-text-primary flex-1">{message}</p>
      </div>

      <button
        onClick={onClose}
        className="absolute top-2 right-2 p-1 hover:bg-muted rounded transition-colors"
        aria-label="Close notification"
      >
        <X className="w-4 h-4 text-text-secondary" />
      </button>
    </div>
  );
};
