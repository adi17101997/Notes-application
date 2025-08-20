import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useNotesStore } from '../store/notesStore';
import { Note, NoteFormData } from '../types';
import { Header } from '../components/layout/Header';
import { NoteCard } from '../components/notes/NoteCard';
import { NoteForm } from '../components/notes/NoteForm';
import { EmptyState } from '../components/notes/EmptyState';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const Home: React.FC = () => {
  const { user } = useAuthStore();
  const {
    notes,
    loading,
    error,
    total,
    page,
    per_page,
    loadNotes,
    addNote,
    updateNote,
    deleteNote,
    clearError
  } = useNotesStore();

  const [showNoteForm, setShowNoteForm] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'title'>('newest');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Load notes when user changes or search term changes
  useEffect(() => {
    if (user) {
      loadNotes(1, per_page, debouncedSearchTerm);
    }
  }, [user, debouncedSearchTerm, per_page, loadNotes]);

  const filteredAndSortedNotes = React.useMemo(() => {
    let filtered = notes.filter(note =>
      note.note_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.note_content.toLowerCase().includes(searchTerm.toLowerCase())
    );

    switch (sortBy) {
      case 'newest':
        return filtered.sort((a, b) => new Date(b.last_update).getTime() - new Date(a.last_update).getTime());
      case 'oldest':
        return filtered.sort((a, b) => new Date(a.last_update).getTime() - new Date(b.last_update).getTime());
      case 'title':
        return filtered.sort((a, b) => a.note_title.localeCompare(b.note_title));
      default:
        return filtered;
    }
  }, [notes, searchTerm, sortBy]);

  const handleCreateNote = () => {
    setEditingNote(null);
    setShowNoteForm(true);
  };

  const handleEditNote = (note: Note) => {
    setEditingNote(note);
    setShowNoteForm(true);
  };

  const handleDeleteNote = async (noteId: string) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      await deleteNote(noteId);
    }
  };

  const handleSubmitNote = async (data: NoteFormData) => {
    if (editingNote) {
      await updateNote(editingNote.note_id, data);
    } else {
      await addNote(data);
    }
    setShowNoteForm(false);
    setEditingNote(null);
  };

  const handleCloseForm = () => {
    setShowNoteForm(false);
    setEditingNote(null);
  };

  const handleLoadMore = () => {
    loadNotes(page + 1, per_page, debouncedSearchTerm);
  };

  if (loading && notes.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle size={20} className="text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearError}
              className="text-red-600 hover:text-red-800"
            >
              Dismiss
            </Button>
          </div>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div className="mb-4 sm:mb-0">
            <h1 className="text-2xl font-bold text-gray-900">My Notes</h1>
            <p className="text-gray-600">{total} notes total</p>
          </div>

          <Button onClick={handleCreateNote} className="flex items-center">
            <Plus size={20} className="mr-2" />
            New Note
          </Button>
        </div>

        {notes.length > 0 && (
          <div className="mb-6 flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Input
                type="text"
                placeholder="Search notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
              <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            </div>

            <div className="flex items-center space-x-2">
              <Filter size={16} className="text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
                <option value="title">By title</option>
              </select>
            </div>
          </div>
        )}

        {filteredAndSortedNotes.length === 0 ? (
          notes.length === 0 ? (
            <EmptyState onCreateNote={handleCreateNote} />
          ) : (
            <div className="text-center py-16">
              <p className="text-gray-500">No notes match your search.</p>
            </div>
          )
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAndSortedNotes.map((note) => (
                <NoteCard
                  key={note.note_id}
                  note={note}
                  onEdit={handleEditNote}
                  onDelete={handleDeleteNote}
                />
              ))}
            </div>

            {/* Load More Button */}
            {notes.length < total && (
              <div className="mt-8 text-center">
                <Button
                  onClick={handleLoadMore}
                  loading={loading}
                  variant="outline"
                  className="px-8"
                >
                  Load More Notes
                </Button>
              </div>
            )}
          </>
        )}
      </main>

      <Modal
        isOpen={showNoteForm}
        onClose={handleCloseForm}
        title={editingNote ? 'Edit Note' : 'Create New Note'}
      >
        <NoteForm
          note={editingNote || undefined}
          onSubmit={handleSubmitNote}
          onCancel={handleCloseForm}
          isLoading={loading}
        />
      </Modal>
    </div>
  );
};