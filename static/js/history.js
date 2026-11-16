let allClips = [];

const historyClipsGrid = document.getElementById('historyClipsGrid');
const emptyState = document.getElementById('emptyState');
const totalClipsCount = document.getElementById('totalClipsCount');
const searchInput = document.getElementById('searchInput');

const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const keyDot = document.getElementById('keyDot');

// Init API key check
fetch('/api/config')
  .then(res => res.json())
  .then(data => {
    if (data.has_key) {
      keyDot.classList.add('active');
      apiKeyInput.placeholder = `AI Studio Key (${data.masked_key}) ✓`;
    }
  });

saveKeyBtn.addEventListener('click', async () => {
  const key = apiKeyInput.value.trim();
  if (!key) return;

  if (key.startsWith('http://') || key.startsWith('https://') || key.includes('youtu') || key.includes('twitch')) {
    alert('⚠️ That looks like a video link, not an API key!\n\nTo clip a YouTube or Twitch video, go to the Studio tab and paste it into the Video link input.');
    window.location.href = '/';
    return;
  }

  const res = await fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: key })
  });
  const data = await res.json();
  if (data.has_key) {
    keyDot.classList.add('active');
    apiKeyInput.value = '';
    apiKeyInput.placeholder = `AI Studio Key (${data.masked_key}) ✓`;
  }
});

// Load History
async function loadHistory() {
  try {
    const res = await fetch('/api/history');
    allClips = await res.json();
    totalClipsCount.textContent = allClips.length;

    if (!allClips || allClips.length === 0) {
      emptyState.style.display = 'block';
      historyClipsGrid.innerHTML = '';
      return;
    }

    emptyState.style.display = 'none';
    renderClips(allClips);
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

function renderClips(clips) {
  historyClipsGrid.innerHTML = '';

  if (clips.length === 0) {
    historyClipsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #9ca3af; padding: 40px 0;">No matching clips found.</p>';
    return;
  }

  clips.forEach(clip => {
    const card = document.createElement('div');
    card.className = 'clip-card';
    card.id = `card_${clip.video_file.replace(/[^a-zA-Z0-9]/g, '_')}`;

    const social = clip.social_copy || {};
    const ytText = social.youtube || `${clip.title} #Shorts #Viral`;
    const ttText = social.tiktok || `${clip.hook || clip.title} #fyp #viral`;
    const igText = social.instagram || `${clip.title} #reels #explore`;

    card.innerHTML = `
      <div class="video-container">
        <video controls playsinline preload="metadata">
          <source src="${clip.preview_url}" type="video/mp4">
          Your browser does not support the video tag.
        </video>
      </div>
      <div class="clip-info">
        <div class="clip-header">
          <div class="clip-title">${clip.title}</div>
          <div class="viral-badge">🔥 ${clip.virality_score}/100</div>
        </div>
        <div class="clip-meta-date">Saved on: ${clip.created_at || 'Recent'}</div>
        <div class="clip-scores">
          <span class="score-chip">Hook: <strong>${clip.hook_score}%</strong></span>
          <span class="score-chip">Flow: <strong>${clip.flow_score}%</strong></span>
          <span class="score-chip">Engagement: <strong>${clip.engagement_score || 92}%</strong></span>
          <span class="score-chip">⏱ <strong>${clip.duration}s</strong></span>
        </div>
        ${clip.hook ? `<div class="clip-hook">"${clip.hook}"</div>` : ''}
        ${clip.reason ? `<div class="clip-reason">${clip.reason}</div>` : ''}

        <!-- Social Copy -->
        <div class="social-section">
          <div class="social-tabs">
            <button class="social-tab active" data-platform="yt">YouTube</button>
            <button class="social-tab" data-platform="tt">TikTok</button>
            <button class="social-tab" data-platform="ig">Instagram</button>
          </div>
          <div class="social-content-row">
            <span class="social-text" id="socialText_${clip.id}">${ytText}</span>
            <button class="btn-copy" id="copyBtn_${clip.id}">Copy</button>
          </div>
        </div>

        <div class="history-actions-row">
          <a href="${clip.download_url}" class="btn-download" download>
            ⬇️ Download Short
          </a>
          <button class="btn-delete" data-file="${clip.video_file}">
            🗑️
          </button>
        </div>
      </div>
    `;

    // Social tabs
    const textEl = card.querySelector(`#socialText_${clip.id}`);
    const copyBtn = card.querySelector(`#copyBtn_${clip.id}`);
    const tabBtns = card.querySelectorAll('.social-tab');
    const socialTexts = { yt: ytText, tt: ttText, ig: igText };

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        textEl.textContent = socialTexts[btn.dataset.platform];
      });
    });

    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(textEl.textContent).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy', 1500);
      });
    });

    // Delete handler
    const deleteBtn = card.querySelector('.btn-delete');
    deleteBtn.addEventListener('click', async () => {
      if (!confirm(`Are you sure you want to delete "${clip.title}"?`)) return;
      deleteBtn.disabled = true;
      try {
        const res = await fetch(`/api/history/${encodeURIComponent(clip.video_file)}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.status === 'deleted') {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => {
            card.remove();
            allClips = allClips.filter(c => c.video_file !== clip.video_file);
            totalClipsCount.textContent = allClips.length;
            if (allClips.length === 0) emptyState.style.display = 'block';
          }, 200);
        } else {
          alert('Could not delete clip');
        }
      } catch (err) {
        alert(`Error deleting clip: ${err.message}`);
      }
    });

    historyClipsGrid.appendChild(card);
  });
}

// Search filter
searchInput.addEventListener('input', () => {
  const q = searchInput.value.toLowerCase().trim();
  if (!q) {
    renderClips(allClips);
    return;
  }
  const filtered = allClips.filter(c => 
    (c.title && c.title.toLowerCase().includes(q)) || 
    (c.hook && c.hook.toLowerCase().includes(q)) ||
    (c.reason && c.reason.toLowerCase().includes(q))
  );
  renderClips(filtered);
});

// Run
loadHistory();
