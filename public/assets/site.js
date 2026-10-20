(function () {
  var body = document.body;
  var sidebar = document.getElementById('sidebar');
  var scrim = document.querySelector('[data-close-menu]');
  var openers = document.querySelectorAll('.burger, .open-menu');

  function setOpen(open) {
    body.classList.toggle('menu-open', open);
    if (scrim) scrim.hidden = !open;
    openers.forEach(function (b) { b.setAttribute('aria-expanded', open ? 'true' : 'false'); });
  }

  openers.forEach(function (b) {
    b.addEventListener('click', function () { setOpen(!body.classList.contains('menu-open')); });
  });
  if (scrim) scrim.addEventListener('click', function () { setOpen(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
  if (sidebar) sidebar.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });

  // Подсветка активного таба при прокрутке
  var tabs = document.querySelectorAll('.tabs a');
  if (tabs.length && 'IntersectionObserver' in window) {
    var map = {};
    tabs.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tabs.forEach(function (a) { a.classList.remove('active'); });
        var a = map[en.target.id];
        if (a) {
          a.classList.add('active');
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
