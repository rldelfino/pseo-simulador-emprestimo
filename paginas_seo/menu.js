/* Menu do celular: fecha ao tocar fora ou com Esc. Sem JavaScript o menu continua abrindo e fechando (é um <details>). */
(function () {
  'use strict';
  var d = document.querySelector('header details');
  if (!d) return;
  document.addEventListener('click', function (e) {
    if (d.open && !d.contains(e.target)) d.open = false;
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !d.open) return;
    d.open = false;
    var s = d.querySelector('summary');
    if (s) s.focus();
  });
})();
