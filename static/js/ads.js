// A8 のバナーを、PC用・スマホ用のうち画面幅に合う片方だけ出す。
//
// 両方を置いて CSS で隠すと、隠した側の画像も読み込まれて表示回数が2倍に数えられる。
// JavaScriptが動かない環境では広告が出ないだけで、本文はそのまま読める。
(function () {
  "use strict";

  document.querySelectorAll(".ad-slot template").forEach(function (template) {
    if (window.matchMedia(template.dataset.adMedia).matches) {
      template.parentNode.appendChild(template.content.cloneNode(true));
    }
  });
})();
