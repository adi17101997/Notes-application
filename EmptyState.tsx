'use client';

interface EmptyStateProps {
  onAddNote: () => void;
}

export default function EmptyState({ onAddNote }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
        <svg
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-full h-full"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
          />
        </svg>
      </div>
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">No notes yet</h3>
      <p className="text-gray-600 mb-6 max-w-sm mx-auto">
        Get started by creating your first note. It's a great way to organize your thoughts and ideas.
      </p>
      
      <button
        onClick={onAddNote}
        className="btn-primary"
      >
        Create your first note
      </button>
    </div>
  );
}