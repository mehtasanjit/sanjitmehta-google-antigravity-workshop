import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export const NotificationToast = () => {
  const { toasts, removeToast } = useWorkbench();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        let icon = <Info className="h-4 w-4 text-blue-500" />;
        let border = "border-blue-200 dark:border-blue-900";
        if (toast.type === 'success') {
          icon = <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
          border = "border-emerald-200 dark:border-emerald-900";
        } else if (toast.type === 'warning' || toast.type === 'error') {
          icon = <AlertCircle className="h-4 w-4 text-rose-500" />;
          border = "border-rose-200 dark:border-rose-900";
        }

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-2xl p-4 shadow-xl border ${border} flex items-start gap-3 transition-all duration-300 transform translate-y-0`}
          >
            <div className="mt-0.5 flex-shrink-0">{icon}</div>
            <div className="flex-1 min-w-0">
              <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
                {toast.title}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-normal">
                {toast.message}
              </p>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
