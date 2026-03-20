document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initScrollAnimations();
  initNavScroll();
  initGalleryFilter();
  initMultiStepForm();
  initFileUpload();
  setActiveNavLink();
});

/* Mobile Menu */
function initMobileMenu() {
  const btn = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  if (!btn || !menu) return;
  btn.addEventListener('click', () => {
    menu.classList.toggle('hidden');
    const icon = btn.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
  });
  menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => menu.classList.add('hidden'));
  });
}

/* Scroll-triggered fade-in */
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  document.querySelectorAll('.fade-in-up').forEach(el => observer.observe(el));
}

/* Nav background on scroll */
function initNavScroll() {
  const nav = document.querySelector('nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('shadow-lg', window.scrollY > 50);
    nav.classList.toggle('shadow-gold/5', window.scrollY > 50);
  });
}

/* Gallery Filter + Search */
function initGalleryFilter() {
  const btns = document.querySelectorAll('.filter-btn');
  const search = document.getElementById('gallery-search');
  const cards = document.querySelectorAll('.artifact-card');
  if (!btns.length) return;

  let activeFilter = 'all';

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      filterCards();
    });
  });

  if (search) {
    search.addEventListener('input', filterCards);
  }

  function filterCards() {
    const query = search ? search.value.toLowerCase() : '';
    cards.forEach(card => {
      const matchesFilter = activeFilter === 'all' || card.dataset.category === activeFilter;
      const matchesSearch = !query || card.textContent.toLowerCase().includes(query);
      card.style.display = (matchesFilter && matchesSearch) ? '' : 'none';
    });
  }
}

/* Multi-Step Form */
function initMultiStepForm() {
  const steps = document.querySelectorAll('.form-step');
  const indicators = document.querySelectorAll('.step-indicator');
  const lines = document.querySelectorAll('.step-line');
  const nextBtns = document.querySelectorAll('.next-step');
  const prevBtns = document.querySelectorAll('.prev-step');
  if (!steps.length) return;

  let current = 0;

  function showStep(n) {
    steps.forEach((s, i) => s.classList.toggle('hidden', i !== n));
    indicators.forEach((ind, i) => {
      ind.classList.remove('active', 'completed');
      if (i < n) ind.classList.add('completed');
      if (i === n) ind.classList.add('active');
    });
    lines.forEach((line, i) => {
      line.classList.toggle('completed', i < n);
    });
    current = n;
    window.scrollTo({ top: document.getElementById('appraisal-form')?.offsetTop - 100 || 0, behavior: 'smooth' });
  }

  nextBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (current < steps.length - 1) showStep(current + 1);
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (current > 0) showStep(current - 1);
    });
  });

  showStep(0);
}

/* File Upload Preview */
function initFileUpload() {
  document.querySelectorAll('.photo-upload').forEach(input => {
    const previewId = input.dataset.preview;
    const preview = document.getElementById(previewId);
    if (!preview) return;

    input.addEventListener('change', () => {
      preview.innerHTML = '';
      const files = Array.from(input.files).slice(0, 5);
      files.forEach(file => {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (e) => {
          const div = document.createElement('div');
          div.className = 'relative w-20 h-20 rounded-lg overflow-hidden border border-gold/30';
          div.innerHTML = `
            <img src="${e.target.result}" class="w-full h-full object-cover" alt="Upload preview">
            <button type="button" onclick="this.parentElement.remove()" class="absolute top-0 right-0 bg-red-600 text-white text-xs w-5 h-5 flex items-center justify-center rounded-bl">&times;</button>`;
          preview.appendChild(div);
        };
        reader.readAsDataURL(file);
      });
    });
  });
}

/* Active Nav Link */
function setActiveNavLink() {
  const path = window.location.pathname;
  document.querySelectorAll('nav a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href || href === '#') return;
    const isActive = (path === '/' && href === '/') ||
                     (path === '/index.html' && href === '/') ||
                     (href !== '/' && path.includes(href));
    if (isActive && !link.classList.contains('bg-gold')) {
      link.classList.add('text-gold');
      link.classList.remove('text-gray-300');
    }
  });
}

/* Smooth scroll for anchor links */
document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href^="#"]');
  if (!link) return;
  const target = document.querySelector(link.getAttribute('href'));
  if (target) {
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
