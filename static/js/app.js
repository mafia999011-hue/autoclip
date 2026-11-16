let currentVideoId = null;
let pollInterval = null;

// DOM Elements
const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const keyDot = document.getElementById('keyDot');

const dropZone = document.getElementById('dropZone');
const videoFileInput = document.getElementById('videoFileInput');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const generateBtn = document.getElementById('generateBtn');

const tabUpload = document.getElementById('tabUpload');
const tabYoutube = document.getElementById('tabYoutube');
const fileUploadContainer = document.getElementById('fileUploadContainer');
const youtubeContainer = document.getElementById('youtubeContainer');
const youtubeUrlInput = document.getElementById('youtubeUrlInput');
const fetchYtBtn = document.getElementById('fetchYtBtn');
const ytStatusDisplay = document.getElementById('ytStatusDisplay');

// Tabs
tabUpload.addEventListener('click', () => {
  tabUpload.classList.add('active');
  tabYoutube.classList.remove('active');
  fileUploadContainer.style.display = 'block';
  youtubeContainer.style.display = 'none';
});

tabYoutube.addEventListener('click', () => {
  tabYoutube.classList.add('active');
  tabUpload.classList.remove('active');
  fileUploadContainer.style.display = 'none';
  youtubeContainer.style.display = 'block';
});

// Fetch Video from Link (YouTube / Twitch / etc.)
fetchYtBtn.addEventListener('click', async () => {
  const url = youtubeUrlInput.value.trim();
  if (!url) {
    ytStatusDisplay.textContent = 'Please enter a valid video URL (YouTube, Twitch, etc.)';
    return;
  }

  const liveDuration = document.getElementById('liveDuration')?.value || 180;

  fetchYtBtn.disabled = true;
  ytStatusDisplay.textContent = 'Connecting & downloading video/live stream snippet (this may take a moment)...';

  try {
    const res = await fetch('/api/fetch_url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, live_duration: liveDuration })
    });
    const data = await res.json();
    if (data.video_id) {
      currentVideoId = data.video_id;
      const platformTag = data.platform ? `[${data.platform}] ` : '';
      ytStatusDisplay.textContent = `Ready: ${platformTag}${data.title} (${Math.round(data.duration || 0)}s)`;
      generateBtn.disabled = false;
    } else {
      ytStatusDisplay.textContent = `Failed: ${data.error || 'Could not download video'}`;
    }
  } catch (err) {
    ytStatusDisplay.textContent = `Error: ${err.message}`;
  } finally {
    fetchYtBtn.disabled = false;
  }
});

const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressPct = document.getElementById('progressPct');
const statusMessage = document.getElementById('statusMessage');

const resultsSection = document.getElementById('resultsSection');
const resultsSummary = document.getElementById('resultsSummary');
const clipsGrid = document.getElementById('clipsGrid');

// Init: check API key status
fetch('/api/config')
  .then(res => res.json())
  .then(data => {
    if (data.has_key) {
      keyDot.classList.add('active');
      apiKeyInput.placeholder = `AI Studio Key (${data.masked_key}) ✓`;
    }
  });

// Save API Key
saveKeyBtn.addEventListener('click', async () => {
  const key = apiKeyInput.value.trim();
  if (!key) return;

  // Check if user accidentally pasted a video or web link
  if (key.startsWith('http://') || key.startsWith('https://') || key.includes('youtu') || key.includes('twitch')) {
    alert('⚠️ That looks like a video link, not an API key!\n\nWe have automatically moved it to the Video URL tab for you.');
    tabYoutube.click();
    youtubeUrlInput.value = key;
    apiKeyInput.value = '';
    apiKeyInput.placeholder = 'Enter Google AI Studio Key...';
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

// Drag and drop events
dropZone.addEventListener('click', () => videoFileInput.click());

['dragenter', 'dragover'].forEach(eventName => {
  dropZone.addEventListener(eventName, e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
  });
});

dropZone.addEventListener('drop', e => {
  if (e.dataTransfer.files.length) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
});

videoFileInput.addEventListener('change', () => {
  if (videoFileInput.files.length) {
    handleFileUpload(videoFileInput.files[0]);
  }
});

async function handleFileUpload(file) {
  fileNameDisplay.textContent = `Uploading: ${file.name}...`;
  const formData = new FormData();
  formData.append('video', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.video_id) {
      currentVideoId = data.video_id;
      fileNameDisplay.textContent = `Ready: ${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
      generateBtn.disabled = false;
    } else {
      fileNameDisplay.textContent = `Upload failed: ${data.error || 'Unknown error'}`;
    }
  } catch (err) {
    fileNameDisplay.textContent = `Upload error: ${err.message}`;
  }
}

// Generate Shorts
generateBtn.addEventListener('click', async () => {
  if (!currentVideoId) return;

  generateBtn.disabled = true;
  progressSection.style.display = 'block';
  resultsSection.style.display = 'none';
  clipsGrid.innerHTML = '';

  const reframeMode = document.getElementById('reframeMode').value;
  const subtitlePreset = document.getElementById('subtitlePreset').value;
  const lengthPref = document.getElementById('lengthPref').value;
  const clipCount = document.getElementById('clipCount').value;
  const captionLanguage = document.getElementById('captionLanguage')?.value || 'auto';
  const enableEmojis = document.getElementById('enableEmojis').checked;

  try {
    const res = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_id: currentVideoId,
        reframe_mode: reframeMode,
        subtitle_preset: subtitlePreset,
        enable_emojis: enableEmojis,
        length_pref: lengthPref,
        clip_count: clipCount,
        caption_language: captionLanguage
      })
    });
    const data = await res.json();
    if (data.task_id) {
      pollTask(data.task_id);
    } else {
      alert(`Error starting pipeline: ${data.error || 'Unknown'}`);
      generateBtn.disabled = false;
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
    generateBtn.disabled = false;
  }
});

function pollTask(taskId) {
  if (pollInterval) clearInterval(pollInterval);

  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/status/${taskId}`);
      const task = await res.json();

      progressBar.style.width = `${task.progress}%`;
      progressPct.textContent = `${task.progress}%`;
      statusMessage.textContent = task.message;

      if (task.status === 'completed') {
        clearInterval(pollInterval);
        progressSection.style.display = 'none';
        generateBtn.disabled = false;
        renderResults(task.result);
      } else if (task.status === 'failed') {
        clearInterval(pollInterval);
        progressSection.style.display = 'none';
        generateBtn.disabled = false;
        alert(`Generation failed: ${task.error}`);
      }
    } catch (err) {
      console.error('Polling error', err);
    }
  }, 1000);
}

function renderResults(result) {
  resultsSummary.textContent = result.summary || 'Generated short-form vertical clips:';
  resultsSection.style.display = 'block';

  clipsGrid.innerHTML = '';
  result.clips.forEach(clip => {
    const card = document.createElement('div');
    card.className = 'clip-card';

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
        <div class="clip-scores">
          <span class="score-chip">Hook: <strong>${clip.hook_score}%</strong></span>
          <span class="score-chip">Flow: <strong>${clip.flow_score}%</strong></span>
          <span class="score-chip">Engagement: <strong>${clip.engagement_score || 92}%</strong></span>
          <span class="score-chip">⏱ <strong>${clip.duration}s</strong></span>
        </div>
        ${clip.hook ? `<div class="clip-hook">"${clip.hook}"</div>` : ''}
        ${clip.reason ? `<div class="clip-reason">${clip.reason}</div>` : ''}

        <!-- Opus Social Copy Box -->
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

        <a href="${clip.download_url}" class="btn-download" download>
          ⬇️ Download Vertical Short
        </a>
      </div>
    `;

    // Hook up social tab switcher for this card
    const textEl = card.querySelector(`#socialText_${clip.id}`);
    const copyBtn = card.querySelector(`#copyBtn_${clip.id}`);
    const tabBtns = card.querySelectorAll('.social-tab');

    const socialTexts = { yt: ytText, tt: ttText, ig: igText };
    let currentPlatform = 'yt';

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPlatform = btn.dataset.platform;
        textEl.textContent = socialTexts[currentPlatform];
      });
    });

    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(textEl.textContent).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy', 1500);
      });
    });

    clipsGrid.appendChild(card);
  });
}
