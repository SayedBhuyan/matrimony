/**
 * Vivaha — Main JavaScript
 * Handles navigation, scroll effects, and interactive behaviors.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initHeaderScroll();
    initMessageDismiss();
    initActionModals();
    initAjaxForms();
});

/**
 * Mobile navigation toggle
 */
function initMobileNav() {
    const toggle = document.getElementById('mobile-toggle');
    const nav = document.getElementById('main-nav');

    if (!toggle || !nav) return;

    toggle.addEventListener('click', () => {
        const isOpen = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', isOpen);
    });

    // Close nav when clicking a link
    nav.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        });
    });

    // Close nav when clicking outside
    document.addEventListener('click', (e) => {
        if (!nav.contains(e.target) && !toggle.contains(e.target)) {
            nav.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });
}

/**
 * Header scroll shadow effect
 */
function initHeaderScroll() {
    const header = document.getElementById('main-header');
    if (!header) return;

    const onScroll = () => {
        header.classList.toggle('scrolled', window.scrollY > 10);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // Initial check
}

/**
 * Auto-dismiss flash messages after 5 seconds
 */
function initMessageDismiss() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-8px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
}

function getCsrfToken() {
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (metaToken && metaToken !== 'NOTPROVIDED') return metaToken;
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

function showToast(message, type = 'success') {
    const region = document.getElementById('toast-region');
    if (!region) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    region.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('is-visible'));
    setTimeout(() => {
        toast.classList.remove('is-visible');
        setTimeout(() => toast.remove(), 250);
    }, 3500);
}

function initActionModals() {
    const modal = document.getElementById('action-modal');
    const form = document.getElementById('action-modal-form');
    if (!modal || !form) return;

    let activeButton = null;
    const close = () => {
        modal.hidden = true;
        form.reset();
        activeButton = null;
    };

    modal.querySelectorAll('[data-modal-close]').forEach(button => button.addEventListener('click', close));
    modal.addEventListener('click', event => {
        if (event.target === modal) close();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !modal.hidden) close();
    });

    document.querySelectorAll('.js-action').forEach(button => {
        button.addEventListener('click', () => {
            activeButton = button;
            const action = button.dataset.action;
            const fields = document.getElementById('action-modal-fields');
            document.getElementById('action-modal-title').textContent = button.dataset.title || 'Confirm action';
            fields.innerHTML = '';

            if (action === 'interest') {
                document.getElementById('action-modal-icon').textContent = '💌';
                document.getElementById('action-modal-copy').textContent = 'Add a personal note to make your introduction memorable.';
                fields.innerHTML = '<label class="form-label" for="modal-message">Your note <span class="text-muted">(optional)</span></label><textarea class="form-input" id="modal-message" name="message" maxlength="500" rows="4" placeholder="Hello! I would love to connect..."></textarea>';
                document.getElementById('action-modal-submit').textContent = 'Send interest';
            } else if (action === 'report') {
                document.getElementById('action-modal-icon').textContent = '⚠️';
                document.getElementById('action-modal-copy').textContent = 'Help us keep Vivaha respectful and safe.';
                fields.innerHTML = '<label class="form-label" for="modal-report-type">What happened?</label><select class="form-input" id="modal-report-type" name="report_type"><option value="fake_profile">Fake profile</option><option value="inappropriate_content">Inappropriate content</option><option value="harassment">Harassment</option><option value="scam">Scam or fraud</option><option value="offensive_language">Offensive language</option><option value="other">Other</option></select><label class="form-label" for="modal-description">Details</label><textarea class="form-input" id="modal-description" name="description" maxlength="1000" rows="4" required placeholder="Tell us what we should review..."></textarea>';
                document.getElementById('action-modal-submit').textContent = 'Submit report';
            } else if (action === 'block') {
                document.getElementById('action-modal-icon').textContent = '🚫';
                document.getElementById('action-modal-copy').textContent = 'This person will no longer be able to contact you or appear in your discovery results.';
                fields.innerHTML = '<label class="form-label" for="modal-reason">Reason <span class="text-muted">(optional)</span></label><input class="form-input" id="modal-reason" name="reason" maxlength="50" placeholder="For example, unwanted messages">';
                document.getElementById('action-modal-submit').textContent = 'Block user';
            } else {
                document.getElementById('action-modal-icon').textContent = '⭐';
                document.getElementById('action-modal-copy').textContent = 'Keep this profile close so you can find it again anytime.';
                document.getElementById('action-modal-submit').textContent = 'Add to shortlist';
            }
            modal.hidden = false;
            fields.querySelector('textarea, input, select')?.focus();
        });
    });

    form.addEventListener('submit', async event => {
        event.preventDefault();
        if (!activeButton) return;
        const submit = document.getElementById('action-modal-submit');
        submit.disabled = true;
        try {
            const response = await fetch(activeButton.dataset.url, {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
                body: new FormData(form),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Action could not be completed.');
            showToast(data.message || 'Done.');
            if (activeButton.dataset.action === 'interest') {
                activeButton.textContent = '✓ Interest sent';
                activeButton.disabled = true;
            } else if (activeButton.dataset.action === 'favorite') {
                activeButton.textContent = '★ Shortlisted';
                activeButton.disabled = true;
            }
            close();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            submit.disabled = false;
        }
    });
}

function initAjaxForms() {
    document.querySelectorAll('form[data-ajax-action]').forEach(form => {
        const messageInput = form.dataset.ajaxAction === 'message' ? form.querySelector('[name="body"]') : null;
        if (messageInput) {
            messageInput.addEventListener('keydown', event => {
                if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
                    event.preventDefault();
                    form.requestSubmit();
                }
            });
        }
        form.addEventListener('submit', async event => {
            event.preventDefault();
            const button = form.querySelector('button[type="submit"]');
            if (button) button.disabled = true;
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {'X-CSRFToken': getCsrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
                    body: new FormData(form),
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Action could not be completed.');
                showToast(data.message || 'Updated successfully.');
                const item = form.closest('[data-interest-item]');
                if (item && data.status === 'success') {
                    const status = item.querySelector('[data-interest-status]');
                    if (status) status.textContent = data.status_label || data.message;
                    item.querySelectorAll('form[data-ajax-action]').forEach(actionForm => actionForm.remove());
                }
                const favoriteItem = form.closest('[data-favorite-item]');
                if (favoriteItem && form.dataset.ajaxAction === 'favorite-remove') {
                    favoriteItem.remove();
                }
                const blockItem = form.closest('[data-block-item]');
                if (blockItem && form.dataset.ajaxAction === 'unblock') {
                    blockItem.remove();
                }
                if (form.dataset.ajaxAction === 'notification-read') {
                    form.closest('.notification-item')?.classList.remove('notification-unread');
                    form.remove();
                }
                if (form.dataset.ajaxAction === 'message') {
                    const thread = document.querySelector('[data-message-thread]');
                    const body = form.querySelector('[name="body"]');
                    if (thread && body) {
                        thread.querySelector('.conversation-empty')?.remove();
                        const row = document.createElement('div');
                        row.className = 'message-row message-row-own';
                        row.innerHTML = `<div class="message-bubble message-bubble-own"><p>${escapeHtml(body.value)}</p><small>Just now</small></div>`;
                        thread.appendChild(row);
                        thread.scrollTop = thread.scrollHeight;
                        body.value = '';
                    }
                }
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                if (button) button.disabled = false;
            }
        });
    });
}

function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = value;
    return element.innerHTML;
}
