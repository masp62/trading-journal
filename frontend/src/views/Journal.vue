<template>
  <div class="journal">
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3>Journal Entries</h3>
        <button @click="showAddForm = !showAddForm" class="btn btn-primary">
          {{ showAddForm ? 'Cancel' : '+ Add Entry' }}
        </button>
      </div>
      
      <div v-if="showAddForm" class="card" style="background: var(--bg-tertiary); border: 1px solid var(--border-color);">
        <h4>Add Journal Entry</h4>
        <form @submit.prevent="addEntry">
          <div class="form-group">
            <label>Date</label>
            <input v-model="newEntry.date" type="date" />
          </div>
          <div class="form-group">
            <label>Title *</label>
            <input v-model="newEntry.title" required placeholder="Entry title or summary" />
          </div>
          <div class="form-group">
            <label>Entry *</label>
            <textarea v-model="newEntry.content" required placeholder="What happened today? What did you learn?"></textarea>
          </div>
          <div class="form-group">
            <label>Tags (comma-separated)</label>
            <input v-model="newEntry.tags" placeholder="strategy, emotions, market-conditions" />
          </div>
          <button type="submit" class="btn btn-success">Add Entry</button>
        </form>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading journal entries...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div v-for="entry in entries" :key="entry.id" class="card journal-entry">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem; gap: 1rem;">
              <h4 style="margin: 0;">{{ entry.title }}</h4>
              <div style="color: #6c757d; font-size: 0.9rem; white-space: nowrap;">
                {{ formatDate(entry.timestamp) }}
              </div>
            </div>
            <div style="white-space: pre-wrap; line-height: 1.6;">
              {{ entry.content }}
            </div>
            <div v-if="entry.tags" style="margin-top: 1rem;">
              <span v-for="tag in entry.tags.split(',')" :key="tag" class="tag">
                {{ tag.trim() }}
              </span>
            </div>
          </div>
          <button @click="deleteEntry(entry)" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 1.5rem;">
            Delete
          </button>
        </div>
      </div>
      <p v-if="entries.length === 0" style="text-align: center; padding: 2rem; color: #6c757d;">
        No journal entries yet. Start documenting your trading journey!
      </p>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Journal-Eintrag löschen?</h3>
          <button @click="closeDeleteModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <p style="color: var(--text-secondary); margin-bottom: 1rem;">
            Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          <div v-if="entryToDelete" style="padding: 1rem; background: var(--bg-secondary); border-radius: 4px; margin-bottom: 1rem;">
            <p><strong>Titel:</strong> {{ entryToDelete.title }}</p>
            <p><strong>Datum:</strong> {{ formatDate(entryToDelete.timestamp) }}</p>
          </div>
          <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button @click="closeDeleteModal" class="btn">Abbrechen</button>
            <button @click="confirmDelete" class="btn btn-danger">Löschen</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'Journal',
  data() {
    return {
      entries: [],
      loading: true,
      error: null,
      showAddForm: false,
      showDeleteModal: false,
      entryToDelete: null,
      newEntry: this.getEmptyEntry()
    }
  },
  mounted() {
    this.loadEntries()
  },
  methods: {
    async loadEntries() {
      try {
        this.loading = true
        this.error = null
        const response = await api.getJournalEntries(100)
        this.entries = response.data
      } catch (err) {
        this.error = 'Failed to load journal entries: ' + (err.response?.data?.detail || err.message)
      } finally {
        this.loading = false
      }
    },
    async addEntry() {
      try {
        await api.createJournalEntry(this.newEntry)
        this.showAddForm = false
        this.newEntry = this.getEmptyEntry()
        await this.loadEntries()
      } catch (err) {
        alert('Failed to add entry: ' + (err.response?.data?.detail || err.message))
      }
    },
    deleteEntry(entry) {
      this.entryToDelete = entry;
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (!this.entryToDelete) return;
      
      try {
        await api.deleteJournalEntry(this.entryToDelete.id);
        this.closeDeleteModal();
        await this.loadEntries();
      } catch (err) {
        alert('Failed to delete entry: ' + (err.response?.data?.detail || err.message));
        this.closeDeleteModal();
      }
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.entryToDelete = null;
    },
    getEmptyEntry() {
      const today = new Date().toISOString().split('T')[0]
      return {
        date: today,
        title: '',
        content: '',
        tags: ''
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.journal-entry {
  border-left: 4px solid #3498db;
}

.tag {
  display: inline-block;
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-right: 0.5rem;
  margin-top: 0.25rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 2rem;
  overflow-y: auto;
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}
</style>
