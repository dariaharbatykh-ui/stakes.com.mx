(function () {
  var body = document.body;
  var sidebar = document.getElementById('sidebar');
  var scrim = document.querySelector('.scrim');
  var openers = document.querySelectorAll('.burger, .open-menu');
  var closers = document.querySelectorAll('[data-close-menu]');
  // Пока меню открыто, остальная страница недоступна для фокуса и экранных дикторов
  var outside = [document.querySelector('.shell'), document.querySelector('.bottom-nav'), document.querySelector('.skip')];
  var opener = null;

  function setOpen(open) {
    body.classList.toggle('menu-open', open);
    if (scrim) scrim.hidden = !open;
    openers.forEach(function (b) { b.setAttribute('aria-expanded', open ? 'true' : 'false'); });
    outside.forEach(function (el) { if (el) el.inert = open; });
    if (open && sidebar) {
      var first = sidebar.querySelector('a, button');
      if (first) first.focus({ preventScroll: true });
    } else if (!open && opener) {
      opener.focus({ preventScroll: true });
    }
  }

  openers.forEach(function (b) {
    b.addEventListener('click', function () { opener = b; setOpen(!body.classList.contains('menu-open')); });
  });
  closers.forEach(function (b) { b.addEventListener('click', function () { setOpen(false); }); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && body.classList.contains('menu-open')) setOpen(false);
  });
  if (sidebar) sidebar.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });

  // Подсветка активного таба при прокрутке
  var tabs = document.querySelectorAll('.tabs a');
  if (tabs.length && 'IntersectionObserver' in window) {
    var map = {};
    tabs.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tabs.forEach(function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
        var a = map[en.target.id];
        if (a) {
          a.classList.add('active');
          a.setAttribute('aria-current', 'true');
          var bar = a.closest('ul');
          bar.scrollTo({ left: a.offsetLeft - bar.clientWidth / 2 + a.offsetWidth / 2, behavior: 'smooth' });
        }
      });
    }, { rootMargin: '-120px 0px -70% 0px' });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }
})();
