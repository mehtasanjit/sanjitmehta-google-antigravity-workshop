import { useEffect, useRef, useState, type FormEvent } from "react";
import { PRIORITIES, type Card, type CardInput, type Priority } from "../types";

export const TITLE_MAX = 120;

interface Props {
  heading: string;
  card?: Card;
  onSave: (input: CardInput) => Promise<void>;
  onCancel: () => void;
}

/** Create/edit form. Validates the title locally; the server remains the source of truth. */
export function CardDialog({ heading, card, onSave, onCancel }: Props) {
  const [title, setTitle] = useState(card?.title ?? "");
  const [description, setDescription] = useState(card?.description ?? "");
  const [priority, setPriority] = useState<Priority>(card?.priority ?? "Medium");
  const [assignee, setAssignee] = useState(card?.assignee ?? "");
  const [tags, setTags] = useState(card?.tags.join(", ") ?? "");
  const [dueDate, setDueDate] = useState(card?.due_date ?? "");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const titleRef = useRef<HTMLInputElement>(null);

  useEffect(() => titleRef.current?.focus(), []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) {
      setError("Title is required");
      return;
    }
    if (trimmed.length > TITLE_MAX) {
      setError(`Title must be at most ${TITLE_MAX} characters`);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onSave({
        title: trimmed,
        description,
        priority,
        assignee: assignee.trim(),
        tags: tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
        due_date: dueDate || null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save the card");
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onKeyDown={(e) => e.key === "Escape" && onCancel()}>
      <div className="dialog" role="dialog" aria-modal="true" aria-labelledby="card-dialog-title">
        <h2 id="card-dialog-title">{heading}</h2>
        <form onSubmit={handleSubmit} noValidate>
          <label>
            Title
            <input
              ref={titleRef}
              value={title}
              maxLength={TITLE_MAX + 20}
              onChange={(e) => setTitle(e.target.value)}
            />
          </label>
          <label>
            Description
            <textarea
              value={description}
              maxLength={2000}
              rows={3}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>
          <div className="row">
            <label>
              Priority
              <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
                {PRIORITIES.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
            <label>
              Due date
              <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
            </label>
          </div>
          <label>
            Assignee
            <input value={assignee} maxLength={60} onChange={(e) => setAssignee(e.target.value)} />
          </label>
          <label>
            Tags (comma-separated)
            <input value={tags} onChange={(e) => setTags(e.target.value)} />
          </label>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <div className="actions">
            <button type="button" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="primary" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
