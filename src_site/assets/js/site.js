(function () {
  var header = document.querySelector('[data-site-header]');
  var toggle = document.querySelector('[data-nav-toggle]');
  if (toggle && header) {
    toggle.addEventListener('click', function () {
      var opened = header.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(opened));
    });
  }

  var path = window.location.pathname;
  var normalized = path.replace(/index\.html$/, '');
  var links = document.querySelectorAll('[data-nav-link]');
  links.forEach(function (link) {
    var href = link.getAttribute('href') || '';
    var linkUrl = new URL(href, window.location.origin);
    var linkPath = linkUrl.pathname.replace(/index\.html$/, '');
    if (
      normalized === linkPath ||
      (normalized.endsWith('/') && normalized.slice(0, -1) === linkPath)
    ) {
      link.classList.add('active');
    }
  });

  var years = document.querySelectorAll('[data-year]');
  var year = String(new Date().getFullYear());
  years.forEach(function (el) {
    el.textContent = year;
  });
})();
