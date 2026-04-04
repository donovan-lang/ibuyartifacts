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
  const container = document.getElementById('youtube-videos');
  if (!container) return;

  try {
    const response = await fetch('youtube_data.json');
    if (!response.ok) throw new Error('Failed to fetch youtube_data.json');
    
    const data = await response.json();
    const videos = Array.isArray(data) ? data : (data.videos || []);

    if (videos.length === 0) {
      container.innerHTML = '<p class="text-gray-500">No videos available yet.</p>';
      return;
    }

    container.innerHTML = videos.map(video => {
      const videoId = video.videoId || video.id;
      const title = video.title || 'Untitled Video';
      const thumbnail = video.thumbnail || `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
      const publishedAt = video.publishedAt || '';
      const date = publishedAt ? new Date(publishedAt).toLocaleDateString() : '';

      return `
        <div class="artifact-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 fade-in-up">
          <div class="relative">
            <img src="${thumbnail}" alt="${title}" class="w-full h-48 object-cover">
            <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener noreferrer" class="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 hover:opacity-100 transition-opacity">
              <div class="w-16 h-16 bg-gold-500 rounded-full flex items-center justify-center">
                <i class="fas fa-play text-white text-xl ml-1"></i>
              </div>
            </a>
          </div>
          <div class="p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">${title}</h3>
            ${date ? `<p class="text-sm text-gray-500">${date}</p>` : ''}
            <a href="https://www.youtube.com/watch?v=${videoId}" target="_blank" rel="noopener noreferrer" class="mt-3 inline-block text-gold-600 hover:text-gold-700 font-medium">
              Watch on YouTube <i class="fas fa-external-link-alt ml-1 text-xs"></i>
            </a>
          </div>
        </div>
      `;
    }).join('');

    // Re-initialize scroll animations for new elements
    setTimeout(() => initScrollAnimations(), 100);
  } catch (error) {
    console.error('Error loading YouTube videos:', error);
    container.innerHTML = `
      <div class="text-center py-8">
        <p class="text-red-500 mb-2">Unable to load videos</p>
        <p class="text-sm text-gray-500">${error.message}</p>
      </div>
    `;
  }
}