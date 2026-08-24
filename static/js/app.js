/* -------------------------------------------------------------
 * StudyMate AI Agent — Frontend Application Script
 * ------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {

  // STATE MANAGEMENT
  let state = {
    notes: [],
    totalDocs: 0,
    totalChars: 0,
    activeTab: 'chat',
    isSending: false
  };

  // DOM ELEMENTS
  const statusIndicator = document.getElementById('statusIndicator');
  const statusLabel = document.getElementById('statusLabel');
  const navTabs = document.querySelectorAll('.nav-tab');
  const tabContents = document.querySelectorAll('.tab-content');

  // Sidebar Elements
  const notesCountBadge = document.getElementById('notesCountBadge');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const uploadProgress = document.getElementById('uploadProgress');
  const uploadContent = document.querySelector('.upload-content');
  const notesList = document.getElementById('notesList');
  const totalDocsVal = document.getElementById('totalDocsVal');
  const totalCharsVal = document.getElementById('totalCharsVal');

  // Chat Elements
  const chatMessages = document.getElementById('chatMessages');
  const welcomeCard = document.getElementById('welcomeCard');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const chipBtns = document.querySelectorAll('.chip-btn');

  // Quiz Elements
  const quizGenForm = document.getElementById('quizGenForm');
  const quizTopicInput = document.getElementById('quizTopicInput');
  const generateQuizBtn = document.getElementById('generateQuizBtn');
  const quizContent = document.getElementById('quizContent');
  const quizTopicTag = document.getElementById('quizTopicTag');
  const currentTopicText = document.getElementById('currentTopicText');
  const evaluateForm = document.getElementById('evaluateForm');
  const evalQuestion = document.getElementById('evalQuestion');
  const evalAnswer = document.getElementById('evalAnswer');
  const evalBtn = document.getElementById('evalBtn');
  const evalResult = document.getElementById('evalResult');
  const evalText = document.getElementById('evalText');

  // Notes Library Elements
  const libraryGrid = document.getElementById('libraryGrid');
  const libraryUploadBtn = document.getElementById('libraryUploadBtn');

  // --- INITIALIZATION ---
  init();

  function init() {
    setupTabNavigation();
    setupFileUpload();
    setupChat();
    setupQuiz();
    checkHealth();
    fetchNotes();

    // Auto resize textarea
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
  }

  // --- HEALTH CHECK ---
  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      if (data.ollama_connected) {
        statusIndicator.className = 'status-indicator ready';
        statusLabel.textContent = `Ollama Ready (llama3.2)`;
      } else {
        statusIndicator.className = 'status-indicator error';
        statusLabel.textContent = 'Ollama Disconnected';
      }
    } catch (e) {
      statusIndicator.className = 'status-indicator error';
      statusLabel.textContent = 'Backend Offline';
    }
  }

  // --- TAB NAVIGATION ---
  function setupTabNavigation() {
    navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTab = tab.getAttribute('data-tab');
        switchTab(targetTab);
      });
    });
  }

  function switchTab(tabId) {
    state.activeTab = tabId;

    navTabs.forEach(tab => {
      if (tab.getAttribute('data-tab') === tabId) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    tabContents.forEach(content => {
      if (content.id === `tab-${tabId}`) {
        content.classList.add('active');
      } else {
        content.classList.remove('active');
      }
    });
  }

  // --- NOTES FETCHING & RENDERING ---
  async function fetchNotes() {
    try {
      const res = await fetch('/api/notes');
      const data = await res.json();

      state.notes = data.notes || [];
      state.totalDocs = data.total_documents || 0;
      state.totalChars = data.total_characters || 0;

      renderNotes();
    } catch (e) {
      console.error('Failed to load notes', e);
    }
  }

  function renderNotes() {
    notesCountBadge.textContent = `${state.totalDocs} file${state.totalDocs === 1 ? '' : 's'}`;
    totalDocsVal.textContent = state.totalDocs;
    totalCharsVal.textContent = state.totalChars.toLocaleString();

    // Render Sidebar List
    if (state.notes.length === 0) {
      notesList.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-dim); font-size: 12px;">No PDF notes uploaded yet.</div>`;
    } else {
      notesList.innerHTML = state.notes.map(note => `
        <div class="note-item">
          <div class="note-info">
            <i class="fa-solid fa-file-pdf note-icon"></i>
            <div class="note-details">
              <span class="note-name" title="${note.filename}">${note.filename}</span>
              <span class="note-meta">${note.pages} pages • ${note.size_kb} KB</span>
            </div>
          </div>
          <button class="note-delete-btn" data-filename="${note.filename}" title="Delete file">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      `).join('');

      // Add delete listeners
      document.querySelectorAll('.note-delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const filename = btn.getAttribute('data-filename');
          deleteNote(filename);
        });
      });
    }

    // Render Library Grid
    renderLibraryGrid();
  }

  function renderLibraryGrid() {
    if (state.notes.length === 0) {
      libraryGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
        <i class="fa-solid fa-folder-open" style="font-size: 40px; margin-bottom: 12px; color: var(--text-dim);"></i>
        <p>No study notes in your library yet. Click <strong>Upload PDF Note</strong> to add material.</p>
      </div>`;
      return;
    }

    libraryGrid.innerHTML = state.notes.map(note => `
      <div class="doc-card">
        <div class="doc-card-header">
          <div class="doc-card-icon">
            <i class="fa-solid fa-file-pdf"></i>
          </div>
          <div class="doc-card-title" title="${note.filename}">${note.filename}</div>
        </div>
        <div class="doc-card-meta">
          <span><i class="fa-solid fa-file-lines"></i> ${note.pages} pages</span>
          <span><i class="fa-solid fa-font"></i> ${note.char_count.toLocaleString()} chars</span>
          <span><i class="fa-solid fa-hard-drive"></i> ${note.size_kb} KB</span>
        </div>
        <div class="doc-card-actions">
          <button class="note-delete-btn" data-filename="${note.filename}" style="color: var(--accent-red); font-weight: 600; font-size: 12px; display: flex; align-items: center; gap: 4px;">
            <i class="fa-solid fa-trash"></i> Remove
          </button>
        </div>
      </div>
    `).join('');

    libraryGrid.querySelectorAll('.note-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const filename = btn.getAttribute('data-filename');
        deleteNote(filename);
      });
    });
  }

  // --- FILE UPLOADING & DELETION ---
  function setupFileUpload() {
    if (libraryUploadBtn) {
      libraryUploadBtn.addEventListener('click', () => fileInput.click());
    }

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleUploadFiles(e.target.files);
      }
    });

    // Drag and Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        handleUploadFiles(files);
      }
    });
  }

  async function handleUploadFiles(files) {
    const formData = new FormData();
    let pdfCount = 0;

    for (let i = 0; i < files.length; i++) {
      if (files[i].name.toLowerCase().endsWith('.pdf')) {
        formData.append('files', files[i]);
        pdfCount++;
      }
    }

    if (pdfCount === 0) {
      alert('Please select valid PDF files.');
      return;
    }

    uploadContent.classList.add('hidden');
    uploadProgress.classList.remove('hidden');

    try {
      const res = await fetch('/api/notes/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (data.errors && data.errors.length > 0) {
        alert('Upload warning:\n' + data.errors.join('\n'));
      }

      state.notes = data.notes || [];
      state.totalDocs = state.notes.length;
      state.totalChars = state.notes.reduce((sum, item) => sum + (item.char_count || 0), 0);
      renderNotes();
    } catch (e) {
      alert('Failed to upload PDF file.');
    } finally {
      uploadProgress.classList.add('hidden');
      uploadContent.classList.remove('hidden');
      fileInput.value = '';
    }
  }

  async function deleteNote(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
      const res = await fetch(`/api/notes/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      state.notes = data.notes || [];
      state.totalDocs = state.notes.length;
      state.totalChars = state.notes.reduce((sum, item) => sum + (item.char_count || 0), 0);
      renderNotes();
    } catch (e) {
      alert('Failed to delete note file.');
    }
  }

  // --- CHAT SYSTEM ---
  function setupChat() {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (message && !state.isSending) {
        sendChatMessage(message);
      }
    });

    // Handle suggestion chips
    chipBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        if (query) {
          sendChatMessage(query);
        }
      });
    });

    // Shift + Enter for newline
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  }

  async function sendChatMessage(query) {
    state.isSending = true;
    chatInput.value = '';
    chatInput.style.height = 'auto';

    if (welcomeCard) {
      welcomeCard.style.display = 'none';
    }

    // Append User Message
    appendMessage('user', query);

    // Append Loading Assistant Message
    const loadingId = appendLoadingBubble();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });
      const data = await res.json();

      removeLoadingBubble(loadingId);

      if (res.ok) {
        appendMessage('assistant', data.answer, data.sources);
      } else {
        appendMessage('assistant', `⚠️ ${data.detail || 'An error occurred while generating the answer.'}`);
      }
    } catch (e) {
      removeLoadingBubble(loadingId);
      appendMessage('assistant', '⚠️ Unable to connect to the backend server.');
    } finally {
      state.isSending = false;
    }
  }

  function appendMessage(role, content, sources = []) {
    const row = document.createElement('div');
    row.className = `chat-row ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-graduation-cap"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    // Simple markdown-style line formatting
    let formattedText = content
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');

    bubble.innerHTML = `<div>${formattedText}</div>`;

    // Render Sources if present
    if (sources && sources.length > 0) {
      const sourcesBox = document.createElement('div');
      sourcesBox.className = 'sources-box';

      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'sources-toggle';
      toggleBtn.innerHTML = `<i class="fa-solid fa-book-open"></i> View ${sources.length} Retrieved Snippets <i class="fa-solid fa-chevron-down"></i>`;

      const sourcesContent = document.createElement('div');
      sourcesContent.className = 'sources-content';

      sources.forEach(src => {
        const item = document.createElement('div');
        item.className = 'source-item';
        item.innerHTML = `
          <div class="source-tag"><i class="fa-solid fa-file-pdf"></i> ${src.filename} (Match Score: ${src.score})</div>
          <div class="source-snippet">"${src.snippet}"</div>
        `;
        sourcesContent.appendChild(item);
      });

      toggleBtn.addEventListener('click', () => {
        sourcesContent.classList.toggle('open');
      });

      sourcesBox.appendChild(toggleBtn);
      sourcesBox.appendChild(sourcesContent);
      bubble.appendChild(sourcesBox);
    }

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendLoadingBubble() {
    const id = 'loading-' + Date.now();
    const row = document.createElement('div');
    row.className = 'chat-row assistant';
    row.id = id;

    row.innerHTML = `
      <div class="avatar"><i class="fa-solid fa-graduation-cap"></i></div>
      <div class="bubble" style="display:flex; align-items:center; gap:8px; color:var(--text-muted);">
        <i class="fa-solid fa-circle-notch fa-spin"></i> Studying notes & thinking...
      </div>
    `;

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeLoadingBubble(id) {
    const elem = document.getElementById(id);
    if (elem) elem.remove();
  }

  // --- QUIZ GENERATOR & EVALUATOR ---
  function setupQuiz() {
    quizGenForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const topic = quizTopicInput.value.trim();
      if (!topic) return;

      generateQuizBtn.disabled = true;
      generateQuizBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Generating...`;
      quizContent.innerHTML = `<div class="empty-quiz-placeholder"><i class="fa-solid fa-spinner fa-spin"></i><p>Analyzing notes and generating quiz on "${topic}"...</p></div>`;

      try {
        const res = await fetch('/api/quiz/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic })
        });
        const data = await res.json();

        if (res.ok) {
          quizTopicTag.classList.remove('hidden');
          currentTopicText.textContent = data.topic;
          quizContent.innerText = data.quiz;
        } else {
          quizContent.innerHTML = `<div class="empty-quiz-placeholder" style="color:var(--accent-red);"><i class="fa-solid fa-triangle-exclamation"></i><p>${data.detail || 'Failed to generate quiz.'}</p></div>`;
        }
      } catch (e) {
        quizContent.innerHTML = `<div class="empty-quiz-placeholder" style="color:var(--accent-red);"><i class="fa-solid fa-plug-circle-xmark"></i><p>Error connecting to backend server.</p></div>`;
      } finally {
        generateQuizBtn.disabled = false;
        generateQuizBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Generate 5-Question Quiz`;
      }
    });

    evaluateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = evalQuestion.value.trim();
      const answer = evalAnswer.value.trim();
      if (!question || !answer) return;

      evalBtn.disabled = true;
      evalBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Evaluating...`;

      try {
        const res = await fetch('/api/quiz/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, answer })
        });
        const data = await res.json();

        if (res.ok) {
          evalResult.classList.remove('hidden');
          evalText.innerText = data.evaluation;
        } else {
          alert(data.detail || 'Evaluation failed.');
        }
      } catch (e) {
        alert('Failed to evaluate answer.');
      } finally {
        evalBtn.disabled = false;
        evalBtn.innerHTML = `<i class="fa-solid fa-user-check"></i> Evaluate My Answer`;
      }
    });
  }

});
