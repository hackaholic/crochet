/** Saved cart-line content; text rendering keeps customer markup inert. */
export default function PersonalizationNote({personalization}: {personalization?: Record<string, unknown>}) {
  const note = personalization?.note;
  return typeof note === 'string' && note.trim()
    ? <p className="mt-1 text-xs text-[#8B6F5E] whitespace-pre-wrap break-words">Note: {note}</p>
    : null;
}
