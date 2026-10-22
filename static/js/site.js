// Phobos site: small enhancements. Everything works without this script; it adds the hero's video, the clips'
// posters in Chrome, the lightbox, the development log's filter, and closes the phone menu after a tap.
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  // The hero's reel plays only where motion is welcome: not with reduced motion, not on Save-Data, not on a narrow
  // screen (the poster shows instead). It pauses off screen, and the button pauses it for good.
  function heroVideo() {
    var video = document.querySelector('[data-hero-video]');
    var toggle = document.querySelector('[data-motion-toggle]');
    if (!video) return;
    var saveData = navigator.connection && navigator.connection.saveData;
    var userPaused = false;
    var visible = true;
    function allowed() { return !reduce.matches && !saveData && !userPaused && window.innerWidth >= 720; }
    function update() {
      if (allowed() && visible) {
        if (video.preload !== 'auto') video.preload = 'auto';
        var p = video.play();
        if (p && p.catch) p.catch(function () {});
      } else {
        video.pause();
      }
      if (toggle) {
        toggle.hidden = reduce.matches || saveData || window.innerWidth < 720;
        toggle.textContent = userPaused ? 'Play video' : 'Pause video';
        toggle.setAttribute('aria-pressed', userPaused ? 'true' : 'false');
      }
    }
    video.addEventListener('playing', function () { video.classList.add('is-playing'); });
    if (toggle) toggle.addEventListener('click', function () { userPaused = !userPaused; update(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        update();
      }, { threshold: 0.05 }).observe(video);
    }
    if (reduce.addEventListener) reduce.addEventListener('change', update);
    window.addEventListener('resize', update, { passive: true });
    update();
  }

  // A clip's poster is a lazy picture beneath its video, so that it loads only near the screen. Chrome covers it with
  // its own controls until the video has data, so once the picture has loaded it becomes the video's poster too.
  function clipPosters() {
    Array.prototype.forEach.call(document.querySelectorAll('.clip-frame'), function (frame) {
      var img = frame.querySelector('.clip-poster img');
      var video = frame.querySelector('video');
      if (!img || !video) return;
      function use() { if (img.currentSrc && !video.getAttribute('poster')) video.poster = img.currentSrc; }
      if (img.complete && img.naturalWidth) use();
      else img.addEventListener('load', use);
    });
  }

  // Pictures open in a dialog, with the group's others a key or a tap away; without the script the link opens the
  // full-size picture.
  function lightbox() {
    var dialog = document.querySelector('[data-lightbox-dialog]');
    if (!dialog || typeof dialog.showModal !== 'function') return;
    var img = dialog.querySelector('[data-lb-img]');
    var cap = dialog.querySelector('[data-lb-cap]');
    var prev = dialog.querySelector('[data-lb-prev]');
    var next = dialog.querySelector('[data-lb-next]');
    var group = [], index = 0, opener = null;
    function show(i) {
      index = (i + group.length) % group.length;
      var link = group[index];
      var thumb = link.querySelector('img');
      img.src = link.getAttribute('href');
      img.alt = thumb ? thumb.alt : '';
      cap.textContent = link.getAttribute('data-caption') || '';
      prev.hidden = next.hidden = group.length < 2;
    }
    document.addEventListener('click', function (e) {
      var link = e.target.closest && e.target.closest('a[data-lightbox]');
      if (!link || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      var name = link.getAttribute('data-lightbox');
      group = Array.prototype.slice.call(document.querySelectorAll('a[data-lightbox="' + name + '"]'));
      opener = link;
      show(group.indexOf(link));
      dialog.showModal();
    });
    prev.addEventListener('click', function () { show(index - 1); });
    next.addEventListener('click', function () { show(index + 1); });
    dialog.querySelector('[data-lb-close]').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (e) { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { show(index - 1); e.preventDefault(); }
      if (e.key === 'ArrowRight') { show(index + 1); e.preventDefault(); }
    });
    dialog.addEventListener('close', function () {
      img.removeAttribute('src');
      if (opener) opener.focus();
    });
  }

  // The development log's filter: rows whose number or title holds every word typed.
  function filter() {
    var input = document.querySelector('[data-filter]');
    if (!input) return;
    var count = document.querySelector('[data-filter-count]');
    var rows = Array.prototype.slice.call(document.querySelectorAll('.month tbody tr'));
    var months = Array.prototype.slice.call(document.querySelectorAll('.month'));
    rows.forEach(function (r) { r._text = r.textContent.toLowerCase().replace(/\s+/g, ' '); });
    function run() {
      var words = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      rows.forEach(function (r) {
        var ok = words.every(function (w) { return r._text.indexOf(w) !== -1; });
        r.hidden = !ok;
        if (ok) shown++;
      });
      months.forEach(function (m) { m.hidden = !m.querySelector('tbody tr:not([hidden])'); });
      if (count) count.textContent = words.length ? shown + ' of ' + rows.length : '';
    }
    input.addEventListener('input', run);
  }

  function menu() {
    var details = document.querySelector('.menu');
    if (!details) return;
    details.addEventListener('click', function (e) { if (e.target.closest('a')) details.open = false; });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') details.open = false; });
  }

  heroVideo();
  clipPosters();
  lightbox();
  filter();
  menu();
})();
