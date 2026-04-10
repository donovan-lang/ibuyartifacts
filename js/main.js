document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initScrollAnimations();
  initNavScroll();
  initGalleryFilter();
  initMultiStepForm();
  initFileUpload();
  setActiveNavLink();
  loadYouTubeVideos();
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
      ind.classList.toggle('active', i <= n);
    });
    lines.forEach((line, i) => {
      line.classList.toggle('active', i < n);
    });
  }

  nextBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (current < steps.length - 1) {
        current++;
        showStep(current);
      }
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (current > 0) {
        current--;
        showStep(current);
      }
    });
  });

  showStep(0);
}

/* File Upload Preview */
function initFileUpload() {
  const input = document.getElementById('artifact-photo');
  const preview = document.getElementById('photo-preview');
  if (!input || !preview) return;

  input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
}

/* Set Active Nav Link */
function setActiveNavLink() {
  const currentPath = window.location.pathname;
  const links = document.querySelectorAll('nav a');
  links.forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
}

/* Load YouTube Videos */
async function loadYouTubeVideos() {
  const container = document.getElementById('videos-grid');
  if (!container) return;

  // Fallback data matching fetch_artifacts.py FALLBACK_VIDEOS
  const FALLBACK_VIDEOS = [
    {
      videoId: 'xn2I-lF9LHU',
      title: "Oda Nobunaga: Japan's Revolutionary Warlord | History Unveiled",
      thumbnail: 'https://i9.ytimg.com/vi/xn2I-lF9LHU/hqdefault.jpg',
      publishedAt: '2026-04-04T15:03:28Z'
    },
    {
      videoId: 'kL17PPSLAMc',
      title: "The Peasants' Revolt: England's Forgotten Uprising",
      thumbnail: 'https://i9.ytimg.com/vi/kL17PPSLAMc/hqdefault.jpg',
      publishedAt: '2026-04-04T15:02:42Z'
    },
    {
      videoId: 'umLHUHzXTSk',
      title: "The Peasants' Revolt: England's Forgotten Uprising",
      thumbnail: 'https://i9.ytimg.com/vi/umLHUHzXTSk/hqdefault.jpg',
      publishedAt: '2026-04-04T15:02:19Z'
    },
    {
      videoId: 'wLFGAxmzots',
      title: 'Greek Fire: The Ancient Superweapon That Saved an Empire',
      thumbnail: 'https://i9.ytimg.com/vi/wLFGAxmzots/hqdefault.jpg',
      publishedAt: '2026-04-04T15:01:38Z'
    }
  ];

  let videos = [];

  try {
    const response = await fetch('youtube_data.json');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    videos = Array.isArray(data) ? data : (data.videos || []);
  } catch (e) {
    console.warn('youtube_data.json unavailable, using fallback videos:', e.message);
  }

  if (videos.length === 0) {
    videos = FALLBACK_VIDEOS;
  }

  renderVideoCards(container, videos);
  setTimeout(() => initScrollAnimations(), 100);
}

function renderVideoCards(container, videos) {
  videos.forEach(video => {
    const videoId = video.videoId || video.id || '';
    const title = video.title || 'Untitled Video';
    const publishedAt = video.publishedAt || '';
    const pubDate = publishedAt
      ? new Date(publishedAt).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      : '';

    const card = document.createElement('div');
    card.className = 'bg-dark-card rounded-lg overflow-hidden border border-gray-800 hover:border-gold/50 transition fade-in-up';
    card.innerHTML = `
      <div class="aspect-video">
        <iframe src="https://www.youtube.com/embed/${videoId}" title="${title}"
          frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen loading="lazy" class="w-full h-full"></iframe>
      </div>
      <div class="p-5">
        <h3 class="font-serif text-lg text-white mb-2">${title}</h3>
        ${pubDate ? `<p class="text-xs text-gray-500 mb-3">${pubDate}</p>` : ''}
        <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener"
           class="inline-flex items-center gap-2 bg-gold/10 border border-gold/30 text-gold px-4 py-2 rounded-lg text-sm font-medium hover:bg-gold hover:text-dark transition">
          <i class="fab fa-youtube"></i> Watch on YouTube
        </a>
      </div>`;
    container.appendChild(card);
  });
}