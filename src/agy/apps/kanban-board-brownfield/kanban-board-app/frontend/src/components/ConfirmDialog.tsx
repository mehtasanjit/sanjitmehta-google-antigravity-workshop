import { useEffect, useRef } from "react";

interface Props {
  message: string;
  confirmLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({ message, confirmLabel, onConfirm, onCancel }: Props) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  useEffect(() => cancelRef.current?.focus(), []);

  return (
    <div className="overlay" onKeyDown={(e) => e.key === "Escape" && onCancel()}>
      <div className="dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-message">
        <p id="confirm-message">{message}</p>
        <div className="actions">
          <button ref={cancelRef} type="button" onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="danger" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
