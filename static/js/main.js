/**
 * Vivaha — Main JavaScript
 * Handles navigation, scroll effects, and interactive behaviors.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initHeaderScroll();
    initMessageDismiss();
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
