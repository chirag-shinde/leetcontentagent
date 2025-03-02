document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle functionality
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const siteNav = document.querySelector('.site-nav');
    
    if (mobileMenuToggle && siteNav) {
        mobileMenuToggle.addEventListener('click', function() {
            siteNav.classList.toggle('show');
        });
    }
    
    // Code highlighting 
    document.querySelectorAll('pre code').forEach((block) => {
        // If using a library like highlight.js, you would activate it here
        // hljs.highlightBlock(block);
    });
    
    // For future enhancements:
    // - Dark mode toggle
    // - Search functionality
    // - Solution rating system
});
