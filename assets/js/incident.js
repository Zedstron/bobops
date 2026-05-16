const incidents = [];

const grid = document.getElementById('incidentGrid');
const detailModal = document.getElementById('detailModal');

const STATUS_LABELS = {
    pending: { icon: 'fa-clock', text: 'Pending' },
    inspection: { icon: 'fa-search', text: 'Inspecting' },
    pm: { icon: 'fa-user-tie', text: 'PM Review' },
    development: { icon: 'fa-code', text: 'Developing' },
    security: { icon: 'fa-shield-alt', text: 'Security Audit' },
    qa: { icon: 'fa-vial', text: 'QA Testing' },
    fixed: { icon: 'fa-check', text: 'Fixed ✓' },
    failed: { icon: 'fa-times', text: 'Failed ✗' }
};

function renderIncidents(filter = 'all') {
    grid.innerHTML = '';
    const filtered = filter === 'all'
        ? incidents
        : incidents.filter(i => i.level === filter);

    if (filtered.length === 0) {
        grid.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
        <h3>All Clear</h3>
        <p>No incidents matching current filters</p>
      </div>
    `;
        return;
    }

    filtered.forEach(inc => {
        const levelColor = {
            'ERROR': 'var(--error)',
            'WARNING': 'var(--warning)',
            'CRITICAL': 'var(--critical)'
        }[inc.level] || 'var(--primary)';

        const levelClass = `level-${inc.level.toLowerCase()}`;
        const snippet = (inc.traceback || inc.raw).replace(/\n/g, ' • ');

        const displayTitle = inc.title.length > 45
            ? inc.title.substring(0, 45) + '...'
            : inc.title;

        let actionArea = '';

        if (inc.status === 'fixed' && inc.pr_url) {
            actionArea = `
        <a href="${inc.pr_url}" target="_blank" rel="noopener noreferrer" 
           class="btn-card btn-fix" style="text-decoration: none;">
          <i class="fab fa-github"></i> View PR
        </a>
      `;
        } else if (inc.status && inc.status !== 'pending') {
            const status = STATUS_LABELS[inc.status] || STATUS_LABELS.pending;
            actionArea = `
        <span class="status-flag" data-status="${inc.status}" id="status-${inc.id}" style="flex:1; justify-content:center; cursor:default;">
          <i class="fas ${status.icon}"></i>
          ${status.text}
        </span>
      `;
        } else {
            actionArea = `
        <button class="btn-card" onclick="openDetail('${inc.id}')">
          <i class="fas fa-eye"></i> View Detail
        </button>
        <button class="btn-card btn-fix" id="fix-btn-${inc.id}" onclick="startFix('${inc.id}')">
          <i class="fas fa-robot"></i> Fix This
        </button>
      `;
        }

        const card = document.createElement('div');
        card.className = 'incident-card';
        card.dataset.id = inc.id;
        card.dataset.status = inc.status || 'pending';
        card.style.setProperty('--level-color', levelColor);
        card.innerHTML = `
      <div class="card-header">
        <span class="level-badge ${levelClass}">${inc.level}</span>
        <span style="font-size: 0.8rem; color: var(--gray); font-family: monospace;">${inc.id}</span>
      </div>
      <h3 class="card-title" title="${inc.title}">${displayTitle}</h3>
      <div class="card-snippet" title="${inc.traceback || inc.raw}">${snippet}</div>
      <div class="card-actions" id="actions-${inc.id}">
        ${actionArea}
      </div>
    `;
        grid.appendChild(card);
    });
}

function updateIncidentStatusFlag(taskId, newStatus, prUrl = null) {
    const statusFlag = document.getElementById(`status-${taskId}`);
    if (!statusFlag) return false;

    const status = STATUS_LABELS[newStatus];
    if (!status) return false;

    if (newStatus === 'fixed' && prUrl) {
        const actionsContainer = document.getElementById(`actions-${taskId}`);
        if (actionsContainer) {
            actionsContainer.innerHTML = `
        <a href="${prUrl}" target="_blank" rel="noopener noreferrer" 
           class="btn-card btn-fix" style="text-decoration: none;">
          <i class="fab fa-github"></i> View PR
        </a>
      `;
        }

        const incident = incidents.find(i => i.id === taskId);
        if (incident) {
            incident.status = 'fixed';
            incident.pr_url = prUrl;
        }
        showToast(`✅ PR ready for ${taskId}`, 'success');
        return true;
    }

    statusFlag.dataset.status = newStatus;
    statusFlag.innerHTML = `<i class="fas ${status.icon}"></i> ${status.text}`;

    statusFlag.style.transform = 'scale(1.05)';
    setTimeout(() => { statusFlag.style.transform = 'scale(1)'; }, 200);

    const incident = incidents.find(i => i.id === taskId);
    if (incident) incident.status = newStatus;

    return true;
}

function openDetail(id) {
    const inc = incidents.find(i => i.id === id);
    if (!inc) return;

    document.getElementById('modalTitle').textContent = `${inc.level} • ${inc.title}`;
    document.getElementById('modalException').textContent = inc.exception_type || 'System Anomaly';

    let highlighted = (inc.traceback || inc.raw)
        .replace(/(File\s+"[^"]+", line \d+, in \w+)/g, '<span class="stack-frame">$1</span>')
        .replace(/(Traceback|Error|Exception|Timeout|AttributeError|DecodeError|JWTDecodeError|ConnectionTimeout)/g,
            '<span class="error-line">$1</span>');

    document.getElementById('modalTraceback').innerHTML = highlighted;
    document.getElementById('modalFixBtn').onclick = () => { closeModal(); startFix(id); };
    detailModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    detailModal.classList.remove('active');
    document.body.style.overflow = '';
}

async function startFix(id) {
    showToast(`🚀 Requesting Bob to fix ${id}...`, 'success');

    try 
    {
        const res = await fetch(`/incident/${id}`, { method: 'POST' });
        if (!res.ok) throw new Error('API Error');
        else updateIncidentStatus(id, 'pending');
    } catch (err) {
        console.error('Fix initiation failed:', err);
        showToast('Failed to start fix pipeline', 'error');
        updateIncidentStatus(id, 'failed');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    document.getElementById('toastMessage').textContent = message;
    toast.className = `toast ${type} show`;
    toast.querySelector('i').className = type === 'success'
        ? 'fas fa-check-circle'
        : 'fas fa-exclamation-circle';
    setTimeout(() => toast.classList.remove('show'), 4000);
}

function init() 
{
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderIncidents(tab.dataset.filter);
        });
    });

    detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) closeModal();
    });

    document.querySelector('.modal-close').addEventListener('click', closeModal);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && detailModal.classList.contains('active')) {
            closeModal();
        }
    });

    const ws = new WebSocket(`ws://localhost:8000/incidents/ws`);
    ws.onmessage = (event) => 
    {
        const data = JSON.parse(event.data);
        if (data && data.id && data.status)
            updateIncidentStatus(incident_id, status);
        else
        {
            incidents.push(data);
            renderIncidents();
        }
    };
}

if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init);
else
    init();