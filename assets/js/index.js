document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

document.addEventListener('mousemove', (e) => {
    const particles = document.querySelector('.particles');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    particles.style.backgroundPosition = `${x * 50}px ${y * 30}px, ${x * 30 + 15}px ${y * 30 + 15}px`;
});