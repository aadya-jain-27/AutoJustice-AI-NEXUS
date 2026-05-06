/**
 * AutoJustice AI NEXUS — Citizen Portal JS
 * Handles DigiLocker verification, multi-step form, file upload, submission.
 */

let currentStep = 1;
let selectedFiles = [];
let submittedReportId = null;
let digilockerProfile = null;   // Set after successful DigiLocker verification
let digilockerSession = null;   // Session token from DigiLocker

// ── DigiLocker Modal State ───────────────────────────────────────────────────
let dlModalVerified = false;

// ── DigiLocker Identity Verification ────────────────────────────────────────

async function startDigiLocker() {
  const btn = document.getElementById('dlVerifyBtn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span style="display:inline-block;width:18px;height:18px;border:3px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin 0.7s linear infinite;margin-right:8px;vertical-align:middle"></span> Connecting...'; }

  // Switch modal to loading state
  _dlSetState('loading');
  document.getElementById('dlLoadingTitle').textContent = 'Connecting to DigiLocker...';
  document.getElementById('dlLoadingSub').textContent = 'Establishing secure OAuth connection';

  try {
    const statusRes = await fetch('/api/digilocker/status');
    const urlRes    = await fetch('/api/digilocker/auth-url');
    const urlData   = await urlRes.json();

    document.getElementById('dlLoadingTitle').textContent = 'Redirecting to DigiLocker...';
    document.getElementById('dlLoadingSub').textContent = 'A verification window will open shortly';
    document.getElementById('dlDot3').classList.add('active');

    if (urlData.demo_mode) {
      // Store state for submitDemoName() to pick up
      window._dlDemoState = urlData.state;
      // Show inline form — no browser prompt()
      _dlSetState('default');
      document.getElementById('dlDemoForm').style.display = 'block';
      document.getElementById('dlDemoNameInput').focus();
      if (btn) { btn.disabled = false; btn.innerHTML = '<span style="font-size:20px">🏛️</span><span>Continue with DigiLocker</span>'; }
    } else {
      _openVerificationPopup(urlData.auth_url);
    }

  } catch (err) {
    console.error('DigiLocker init error:', err);
    _dlSetState('default');
    if (btn) { btn.disabled = false; btn.innerHTML = '<span style="font-size:20px">🏛️</span><span>Continue with DigiLocker</span>'; }
    showToast('Could not connect to DigiLocker. Please try again.', 'error');
  }
}

async function submitDemoName() {
  const input = document.getElementById('dlDemoNameInput');
  const name = input ? input.value.trim() : '';
  if (!name) {
    input.style.borderColor = '#ef4444';
    input.placeholder = 'Please enter your name';
    input.focus();
    return;
  }
  // Hide the form, go to loading state — no popup, direct fetch
  document.getElementById('dlDemoForm').style.display = 'none';
  _dlSetState('loading');
  document.getElementById('dlLoadingTitle').textContent = 'Verifying with DigiLocker...';
  document.getElementById('dlLoadingSub').textContent = 'Authenticating your Aadhaar-linked identity';

  try {
    await new Promise(r => setTimeout(r, 1200)); // brief pause so the loading state is visible
    const res = await fetch(
      `/api/digilocker/demo-verify?state=${encodeURIComponent(window._dlDemoState || '')}&name=${encodeURIComponent(name)}`
    );
    const data = await res.json();
    if (!res.ok || !data.profile) throw new Error(data.detail || 'Verification failed');
    _onDigiLockerVerified(data.profile);
  } catch (err) {
    console.error('Demo verify error:', err);
    showToast('Demo verification failed — please try again.', 'error');
    _dlSetState('default');
    document.getElementById('dlDemoForm').style.display = 'block';
    document.getElementById('dlDemoNameInput').focus();
  }
}

function _cancelDemoForm() {
  document.getElementById('dlDemoForm').style.display = 'none';
  document.getElementById('dlDemoNameInput').value = '';
  _dlSetState('default');
}

function openDLModal() {
  document.getElementById('dlModal').classList.add('show');
  _dlSetState('default');
}

function closeDLModal(verified) {
  document.getElementById('dlModal').classList.remove('show');
  if (!verified) {
    // Show unverified strip
    const strip = document.getElementById('dlStatusStrip');
    if (strip) strip.style.display = 'flex';
  }
}

function _dlSetState(state) {
  // state: 'default' | 'loading' | 'success'
  document.getElementById('dlStateDefault').style.display = state === 'default'  ? 'block' : 'none';
  document.getElementById('dlStateLoading').style.display = state === 'loading'  ? 'block' : 'none';
  document.getElementById('dlStateSuccess').style.display = state === 'success'  ? 'block' : 'none';
  // Always hide demo form when switching states (unless going to default with demo active)
  if (state !== 'default') {
    const f = document.getElementById('dlDemoForm');
    if (f) f.style.display = 'none';
  }
}

function _openVerificationPopup(url) {
  // Listen for message from popup/callback page
  const messageHandler = (event) => {
    if (event.origin !== window.location.origin) return;
    if (!event.data || event.data.type !== 'DIGILOCKER_VERIFIED') return;

    window.removeEventListener('message', messageHandler);
    _onDigiLockerVerified(event.data.profile);
  };

  window.addEventListener('message', messageHandler);

  // Open popup window
  const w = 520, h = 620;
  const left = (screen.width  - w) / 2;
  const top  = (screen.height - h) / 2;
  const popup = window.open(url, 'DigiLockerVerify',
    `width=${w},height=${h},left=${left},top=${top},scrollbars=yes,resizable=yes`
  );

  if (!popup) {
    // Popup blocked — try same-tab redirect
    window.removeEventListener('message', messageHandler);
    sessionStorage.setItem('digilocker_return', window.location.href);
    window.location.href = url;
    return;
  }

  // Poll for popup close (handles same-tab redirect fallback)
  const pollTimer = setInterval(() => {
    if (popup.closed) {
      clearInterval(pollTimer);
      // Check sessionStorage in case of same-tab redirect
      const stored = sessionStorage.getItem('digilocker_profile');
      if (stored) {
        try {
          const profile = JSON.parse(stored);
          sessionStorage.removeItem('digilocker_profile');
          sessionStorage.removeItem('digilocker_session');
          _onDigiLockerVerified(profile);
        } catch (_) {}
      } else {
        // Popup closed without verification
        _dlSetState('default');
        const btn = document.getElementById('dlVerifyBtn');
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span style="font-size:20px">🏛️</span><span>Continue with DigiLocker</span>';
        }
      }
    }
  }, 500);
}

function _onDigiLockerVerified(profile) {
  if (!profile || !profile.verified) {
    showToast('Verification failed. Please try again.', 'error');
    const btn = document.getElementById('dlVerifyBtn');
    if (btn) { btn.disabled = false; btn.innerHTML = '<span style="font-size:20px">🏛️</span><span>Continue with DigiLocker</span>'; }
    return;
  }

  digilockerProfile = profile;
  digilockerSession = profile.session_token;
  dlModalVerified = true;

  // Show success state in modal
  _dlSetState('success');
  const nameEl = document.getElementById('dlSuccessName');
  const methodEl = document.getElementById('dlSuccessMethod');
  if (nameEl) nameEl.textContent = profile.name || 'Verified Citizen';
  if (methodEl) methodEl.textContent = profile.digilocker_verified ? 'Aadhaar-Linked · DigiLocker' : 'Demo Verification';

  // Update verified strip on the form
  const verifiedStrip = document.getElementById('dlVerifiedStrip');
  const unverifiedStrip = document.getElementById('dlStatusStrip');
  const nameStripEl = document.getElementById('dlVerifiedNameStrip');
  if (unverifiedStrip) unverifiedStrip.style.display = 'none';
  if (verifiedStrip) { verifiedStrip.style.display = 'flex'; }
  if (nameStripEl) nameStripEl.textContent = `${profile.name || 'Verified Citizen'} · Verified via DigiLocker`;

  // Auto-fill name if not already filled
  const nameInput = document.getElementById('complainant_name');
  if (nameInput && !nameInput.value && profile.name) nameInput.value = profile.name;
}

function _proceedToForm() {
  // Pre-fill name from verified DigiLocker profile (read-only)
  if (digilockerProfile && digilockerProfile.name) {
    const nameField = document.getElementById('complainant_name');
    if (nameField) {
      nameField.value = digilockerProfile.name;
      nameField.readOnly = true;
      nameField.style.background = '#f0fdf4';
      nameField.style.borderColor = '#16a34a';
      nameField.title = 'Pre-filled from DigiLocker verification';
    }
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
  showToast('Identity verified! Please fill in the complaint details.', 'success');
}

// Check sessionStorage on page load (for same-tab redirect flow)
document.addEventListener('DOMContentLoaded', () => {
  openDLModal();

  const stored = sessionStorage.getItem('digilocker_profile');
  if (stored) {
    try {
      const profile = JSON.parse(stored);
      sessionStorage.removeItem('digilocker_profile');
      sessionStorage.removeItem('digilocker_session');
      if (profile.verified) {
        _onDigiLockerVerified(profile);
        return; // Skip the rest of init
      }
    } catch (_) {}
  }
  // Normal init
});

// ── Step Navigation ─────────────────────────────────────────────────────────

function goToStep(step) {
  if (step === 2 && !validateStep1()) return;
  if (step === 3 && !validateStep2()) return;
  if (step === 4) buildReview();

  document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
  document.getElementById(`formStep${step}`).style.display = 'block';
  currentStep = step;

  // Update step indicators
  for (let i = 1; i <= 4; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    stepEl.classList.remove('active', 'done');
    if (i < step)  stepEl.classList.add('done');
    if (i === step) stepEl.classList.add('active');
  }

  // Update connecting lines
  for (let i = 1; i <= 3; i++) {
    const line = document.getElementById(`line-${i}`);
    if (line) line.classList.toggle('done', i < step);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateStep1() {
  const name = document.getElementById('complainant_name').value.trim();
  if (!name || name.length < 2) {
    showToast('Please enter your full name.', 'error');
    document.getElementById('complainant_name').focus();
    return false;
  }
  return true;
}

function validateStep2() {
  const desc = document.getElementById('incident_description').value.trim();
  if (!desc || desc.length < 20) {
    showToast('Please describe the incident in at least 20 characters.', 'error');
    document.getElementById('incident_description').focus();
    return false;
  }
  return true;
}

// ── Character Counter ────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const desc = document.getElementById('incident_description');
  const counter = document.getElementById('desc-counter');

  if (desc && counter) {
    desc.addEventListener('input', () => {
      const len = desc.value.length;
      if (len < 20) {
        counter.textContent = `${20 - len} more characters needed`;
        counter.style.color = 'var(--red)';
      } else {
        counter.textContent = `✓ ${len} characters`;
        counter.style.color = 'var(--success)';
      }
    });
  }

  setupDropzone();
  setupFormSubmit();
  loadLiveStats();
  setInterval(loadLiveStats, 30000); // Refresh every 30s
});

async function loadLiveStats() {
  try {
    const res  = await fetch('/api/dashboard/live-stats');
    const data = await res.json();
    setTickerEl('tickerTotal', data.total_reports_processed?.toLocaleString('en-IN'));
    setTickerEl('tickerFirs',  data.firs_auto_generated?.toLocaleString('en-IN'));
    setTickerEl('tickerToday', data.reports_today?.toLocaleString('en-IN'));
    setTickerEl('tickerFake',  data.fake_blocked?.toLocaleString('en-IN'));
  } catch (_) { /* silently ignore if server not ready */ }
}

function setTickerEl(id, val) {
  const el = document.getElementById(id);
  if (el && val != null) el.textContent = val;
}

// ── File Upload Dropzone ─────────────────────────────────────────────────────

function setupDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('evidence_files');
  const fileList  = document.getElementById('fileList');

  if (!dropzone) return;

  dropzone.addEventListener('dragover', e => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    addFiles(e.dataTransfer.files);
  });

  fileInput.addEventListener('change', () => addFiles(fileInput.files));
}

function addFiles(fileList) {
  const MAX_MB = 25;
  const ALLOWED = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pdf', '.txt'];

  Array.from(fileList).forEach(file => {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED.includes(ext)) {
      showToast(`"${file.name}" is not a supported file type.`, 'error');
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      showToast(`"${file.name}" exceeds the 25MB limit.`, 'error');
      return;
    }
    if (selectedFiles.find(f => f.name === file.name && f.size === file.size)) return;
    selectedFiles.push(file);
  });

  renderFileList();
}

function renderFileList() {
  const container = document.getElementById('fileList');
  container.innerHTML = '';

  selectedFiles.forEach((file, idx) => {
    const ext = file.name.split('.').pop().toLowerCase();
    const icon = ['jpg','jpeg','png','gif','bmp','tiff'].includes(ext) ? '🖼️'
               : ext === 'pdf' ? '📄' : '📝';
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

    const item = document.createElement('div');
    item.className = 'file-item';
    item.innerHTML = `
      <span class="file-icon">${icon}</span>
      <span class="file-name">${escapeHtml(file.name)}</span>
      <span class="file-size">${sizeMB} MB</span>
      <span class="file-remove" onclick="removeFile(${idx})" title="Remove">✕</span>
    `;
    container.appendChild(item);
  });
}

function removeFile(idx) {
  selectedFiles.splice(idx, 1);
  renderFileList();
}

// ── Review Builder ───────────────────────────────────────────────────────────

function buildReview() {
  const fields = {
    'Full Name':       document.getElementById('complainant_name')?.value,
    'Mobile':          document.getElementById('complainant_phone')?.value || '—',
    'Email':           document.getElementById('complainant_email')?.value || '—',
    'Address':         document.getElementById('complainant_address')?.value || '—',
    'Incident Date':   document.getElementById('incident_date')?.value || '—',
    'Location':        document.getElementById('incident_location')?.value || '—',
  };

  const desc = document.getElementById('incident_description')?.value || '';
  const fileCount = selectedFiles.length;

  let html = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px">
      ${Object.entries(fields).map(([k, v]) => `
        <div>
          <div style="font-size:11px; color:var(--gray-400); font-weight:600; text-transform:uppercase">${k}</div>
          <div style="font-size:14px; font-weight:500; margin-top:2px">${escapeHtml(v || '—')}</div>
        </div>
      `).join('')}
    </div>
    <div style="margin-bottom:16px">
      <div style="font-size:11px; color:var(--gray-400); font-weight:600; text-transform:uppercase; margin-bottom:6px">Incident Description</div>
      <div style="background:var(--gray-50); padding:14px; border-radius:8px; font-size:13px; line-height:1.7">${escapeHtml(desc)}</div>
    </div>
    <div style="background:var(--blue-light); padding:12px 16px; border-radius:8px; font-size:13px">
      📁 <strong>${fileCount} evidence file${fileCount !== 1 ? 's' : ''}</strong> attached
      ${fileCount > 0 ? '— ' + selectedFiles.map(f => f.name).join(', ') : ''}
    </div>
  `;

  document.getElementById('reviewContent').innerHTML = html;
}

// ── Form Submission ──────────────────────────────────────────────────────────

function setupFormSubmit() {
  const form = document.getElementById('reportForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;

    showLoading(true, 'Uploading evidence files...');

    const formData = new FormData();
    // Attach DigiLocker session token if verified
    if (digilockerSession) {
      formData.append('digilocker_session_token', digilockerSession);
    }
    formData.append('complainant_name',    document.getElementById('complainant_name').value);
    formData.append('incident_description', document.getElementById('incident_description').value);
    formData.append('complainant_phone',   document.getElementById('complainant_phone').value || '');
    formData.append('complainant_email',   document.getElementById('complainant_email').value || '');
    formData.append('complainant_address', document.getElementById('complainant_address').value || '');
    formData.append('incident_date',       document.getElementById('incident_date').value || '');
    formData.append('incident_location',   document.getElementById('incident_location').value || '');

    selectedFiles.forEach(file => formData.append('evidence_files', file));

    // Simulate loading steps for UX
    const loadingSteps = [
      [800,  'Running OCR on evidence files...'],
      [1600, 'AI semantic analysis in progress...'],
      [2400, 'Running fake report detection...'],
      [3200, 'Extracting entities for Complaint Report...'],
      [4000, 'Generating Complaint Report PDF...'],
    ];
    loadingSteps.forEach(([delay, msg]) => {
      setTimeout(() => setLoadingText(msg), delay);
    });

    try {
      const response = await fetch('/api/reports/submit', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Submission failed.');
      }

      const data = await response.json();
      showLoading(false);
      displayResult(data);
      submittedReportId = data.id;

    } catch (err) {
      showLoading(false);
      submitBtn.disabled = false;
      showToast('Submission failed: ' + err.message, 'error');
    }
  });
}

// ── Result Display ───────────────────────────────────────────────────────────

function displayResult(data) {
  document.getElementById('reportForm').style.display = 'none';
  document.querySelector('.step-progress').style.display = 'none';
  document.getElementById('result-section').style.display = 'block';

  const risk = data.risk_level || 'PENDING';
  const header = document.getElementById('resultHeader');
  header.className = 'result-header ' + risk.toLowerCase();

  document.getElementById('resultBadge').textContent = '✓ Report Registered';
  document.getElementById('resultCaseNumber').textContent = data.case_number;
  document.getElementById('resultStatusMsg').textContent =
    risk === 'HIGH'   ? '⚠ High-risk threat detected. Complaint Report auto-registered. Police notified.' :
    risk === 'MEDIUM' ? '⚡ Medium-risk case. Under priority review.' :
                        '✓ Report submitted. Under standard review.';

  document.getElementById('resultRiskLevel').textContent = risk || '—';
  document.getElementById('resultRiskLevel').style.color =
    risk === 'HIGH' ? 'var(--red)' : risk === 'MEDIUM' ? 'var(--orange)' : 'var(--success)';

  document.getElementById('resultCrimeCategory').textContent = data.crime_category || '—';

  const firStatus = data.fir_path ? '✓ Complaint Report Auto-Generated' : 'Pending Officer Review';
  document.getElementById('resultFirStatus').textContent = firStatus;

  const auth = data.authenticity_score || 0;
  document.getElementById('resultAuthenticity').textContent =
    data.fake_recommendation === 'GENUINE' ? `✓ Genuine (${(auth * 100).toFixed(0)}%)` :
    data.fake_recommendation === 'REVIEW'  ? `⚠ Under Review (${(auth * 100).toFixed(0)}%)` :
    data.is_flagged_fake ? `⚠ Flagged (${(auth * 100).toFixed(0)}%)` :
    `${(auth * 100).toFixed(0)}%`;

  const authColor = auth > 0.65 ? 'var(--success)' : auth > 0.45 ? 'var(--orange)' : 'var(--red)';
  const authBar = document.getElementById('authBar');
  authBar.style.width = (auth * 100) + '%';
  authBar.style.background = authColor;

  document.getElementById('resultAiSummary').textContent = data.ai_summary || 'Analysis complete.';
  document.getElementById('resultHash').textContent = data.content_hash || 'N/A';

  if (data.fir_path) {
    document.getElementById('downloadFirBtn').style.display = 'inline-block';
  document.getElementById('downloadFirBtn').onclick = downloadComplaintReport;
  }

  document.querySelector('.result-card').scrollIntoView({ behavior: 'smooth' });
}

function downloadComplaintReport() {
  if (!submittedReportId) {
    showToast('No report ID found. Please resubmit.', 'error');
    return;
  }
  const url = `/api/reports/${submittedReportId}/fir/download`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `ComplaintReport_${submittedReportId}.pdf`;
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Downloading Complaint Report PDF...', 'success');
}

function submitAnother() {
  location.reload();
}

// ── Utilities ────────────────────────────────────────────────────────────────

function showLoading(show, text = 'Processing...') {
  const overlay = document.getElementById('loadingOverlay');
  const textEl  = document.getElementById('loadingText');
  overlay.classList.toggle('show', show);
  if (textEl) textEl.textContent = text;
}

function setLoadingText(text) {
  const el = document.getElementById('loadingText');
  if (el) el.textContent = text;
}

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  setTimeout(() => toast.classList.remove('show'), 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
