let allClips = [];

const historyClipsGrid = document.getElementById('historyClipsGrid');
const emptyState = document.getElementById('emptyState');
const totalClipsCount = document.getElementById('totalClipsCount');
const searchInput = document.getElementById('searchInput');

const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const keyDot = document.getElementById('keyDot');

// Modal Elements
const videoModal = document.getElementById('videoModal');
const closeVideoModal = document.getElementById('closeVideoModal');
const modalVideoPlayer = document.getElementById('modalVideoPlayer');
const modalVideoTitle = document.getElementById('modalVideoTitle');
const modalViralityBadge = document.getElementById('modalViralityBadge');
const modalQualityBadge = document.getElementById('modalQualityBadge');
const modalDownloadLink = document.getElementById('modalDownloadLink');

// Toast Notification
function showToast(msg, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️');
  toast.innerHTML = `<span>${icon}</span> <span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(15px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 350);
  }, 3500);
}

// Modal Listeners
if (closeVideoModal && videoModal) {
  closeVideoModal.addEventListener('click', () => {
    videoModal.style.display = 'none';
    if (modalVideoPlayer) {
      modalVideoPlayer.pause();
      modalVideoPlayer.src = '';
    }
  });
}

if (videoModal) {
  videoModal.addEventListener('click', (e) => {
    if (e.target === videoModal) {
      videoModal.style.display = 'none';
      if (modalVideoPlayer) {
        modalVideoPlayer.pause();
        modalVideoPlayer.src = '';
      }
    }
  });
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && videoModal && videoModal.style.display === 'flex') {
    videoModal.style.display = 'none';
    if (modalVideoPlayer) {
      modalVideoPlayer.pause();
      modalVideoPlayer.src = '';
    }
  }
});

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
    showToast('API Key saved successfully!');
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

    let badgeClass = 'viral-blue';
    let badgeText = `⚡ ${clip.virality_score}/100`;
    if (clip.virality_score >= 95) {
      badgeClass = 'viral-gold';
      badgeText = `🔥 ${clip.virality_score}/100`;
    } else if (clip.virality_score >= 90) {
      badgeClass = 'viral-green';
      badgeText = `🚀 ${clip.virality_score}/100`;
    }

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
          <div class="viral-badge ${badgeClass}">${badgeText}</div>
        </div>
        <div class="clip-meta-date">Saved on: ${clip.created_at || 'Recent'}</div>

        ${clip.hook_type ? `<div class="hook-type-pill">${clip.hook_type}</div>` : ''}

        <div class="clip-scores">
          <span class="score-chip">Hook: <strong>${clip.hook_score}%</strong></span>
          <span class="score-chip">Flow: <strong>${clip.flow_score}%</strong></span>
          <span class="score-chip">Engagement: <strong>${clip.engagement_score || 95}%</strong></span>
          <span class="score-chip">Curiosity: <strong>${clip.curiosity_gap || '9.6/10'}</strong></span>
          <span class="score-chip risk-${(clip.drop_off_risk || 'low').toLowerCase().replace(/\s+/g, '-')}">Drop-off: <strong>${clip.drop_off_risk || 'Very Low'}</strong></span>
          <span class="score-chip">⏱ <strong>${clip.duration}s</strong></span>
          <span class="score-chip">📺 <strong>${clip.quality || '1080p'}</strong></span>
        </div>

        ${clip.hook_headline ? `
          <div class="hook-headline-preview">
            <span class="hook-badge-tag">TOP HOOK BANNER</span>
            <span>🔥 ${clip.hook_headline} 🔥</span>
          </div>
        ` : ''}

        ${clip.hook ? `<div class="clip-hook">"${clip.hook}"</div>` : ''}

        <!-- AI Virality & Algorithm Growth Insights -->
        <details class="virality-details">
          <summary>🧠 AI Virality & Algorithm Growth Insights</summary>
          <div class="virality-details-content">
            <p><strong>Retention Psychology:</strong> ${clip.reason || 'High emotional resonance and pattern interrupt.'}</p>
            ${clip.viral_action_tip ? `<p class="viral-tip"><strong>🚀 Growth Hack:</strong> ${clip.viral_action_tip}</p>` : ''}
          </div>
        </details>

        <!-- Social Copy -->
        <div class="social-section">
          <div class="social-tabs">
            <button class="social-tab active" data-platform="yt">YouTube</button>
            <button class="social-tab" data-platform="tt">TikTok</button>
            <button class="social-tab" data-platform="ig">Instagram</button>
          </div>
          <div class="social-content-row">
            <span class="social-text">${ytText}</span>
            <button class="btn-copy">Copy</button>
          </div>
        </div>

        <div class="history-actions-row">
          <button type="button" class="btn-preview-modal btn-sm" style="flex: 1; padding: 10px 12px; background: #1e293b; border: 1px solid #475569; color: #f8fafc; border-radius: 8px; cursor: pointer; font-weight: 700;">
            ▶️ Preview
          </button>
          <a href="${clip.download_url}" class="btn-download" style="flex: 1.5;" download>
            ⬇️ Download
          </a>
          <button class="btn-delete" data-file="${clip.video_file}" title="Delete this short">
            🗑️
          </button>
        </div>
      </div>
    `;

    // Hook up fullscreen preview modal
    const previewBtn = card.querySelector('.btn-preview-modal');
    if (previewBtn && videoModal && modalVideoPlayer) {
      previewBtn.addEventListener('click', () => {
        modalVideoPlayer.src = clip.preview_url;
        modalVideoTitle.textContent = clip.title;
        modalViralityBadge.textContent = `Virality: ${clip.virality_score}/100`;
        modalQualityBadge.textContent = clip.quality || '1080p';
        modalDownloadLink.href = clip.download_url;
        modalDownloadLink.setAttribute('download', clip.video_file || 'short.mp4');
        videoModal.style.display = 'flex';
        modalVideoPlayer.play().catch(() => {});
      });
    }

    // Social tabs
    const textEl = card.querySelector('.social-text');
    const copyBtn = card.querySelector('.btn-copy');
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
        showToast('Social copy copied to clipboard!');
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
          showToast(`Deleted: ${clip.title}`);
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => {
            card.remove();
            allClips = allClips.filter(c => c.video_file !== clip.video_file);
            totalClipsCount.textContent = allClips.length;
            if (allClips.length === 0) emptyState.style.display = 'block';
          }, 200);
        } else {
          showToast('Could not delete clip', 'error');
        }
      } catch (err) {
        showToast(`Error deleting clip: ${err.message}`, 'error');
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
