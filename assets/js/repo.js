function openModal() {
    document.getElementById('modalOverlay').classList.add('active');
    document.getElementById('repoName').focus();
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('cloneForm').reset();
}

document.getElementById('modalOverlay').addEventListener('click', function (e) {
    if (e.target === this) {
        closeModal();
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

document.getElementById('cloneForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const btn = document.getElementById('cloneBtn');
    const originalText = btn.innerHTML;
    const repoName = document.getElementById('repoName').value.trim();

    const repoPattern = /^[\w\-\.]+\/[\w\-\.]+$/;
    if (!repoPattern.test(repoName)) {
        showToast('Please use format: username/reponame', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cloning...';

    try {
        const response = await fetch('/repo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: repoName })
        });

        if (response.ok) {
            showToast(`✓ ${repoName} connected successfully!`, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            const error = await response.text();
            showToast(`Error: ${error || 'Failed to connect repository'}`, 'error');
        }
    } catch (err) {
        showToast('Network error. Please try again.', 'error');
        console.error('Clone error:', err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
});

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const icon = toast.querySelector('i');

    toastMessage.textContent = message;
    toast.className = `toast ${type} show`;

    if (type === 'success') {
        icon.className = 'fas fa-check-circle';
    } else {
        icon.className = 'fas fa-exclamation-circle';
    }

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function removeRepo(repoFullName) {
    if (confirm(`Are you sure you want to remove ${repoFullName}?`)) {
        fetch(`/repo?repo_name=${encodeURIComponent(repoFullName)}`, {
            method: 'DELETE'
        })
            .then(res => res.ok ? window.location.reload() : showToast('Failed to remove repo', 'error'))
            .catch(() => showToast('Network error', 'error'));
    }
}

function startMonitoring(repoFullName) {
    showToast(`🚀 Starting monitoring for ${repoFullName}...`, 'success');
}

window.addEventListener('load', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    const status = urlParams.get('status');

    if (message) {
        showToast(message, status === 'error' ? 'error' : 'success');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

const fab = document.getElementById('fab');
if (fab) {
    fab.addEventListener('mouseenter', () => {
        fab.style.animation = 'none';
    });
    fab.addEventListener('animationend', () => {
        fab.style.animation = '';
    });
}