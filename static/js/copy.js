// AIへの指示文にコピーボタンを付ける。
//
// このサイトで一番使われるのは指示文なので、選択してドラッグさせない。
// JavaScriptが動かない環境でも、指示文そのものは変わらず読めて選択できる
// （ボタンが増えないだけ）。
(function () {
  "use strict";

  var LABEL = "AIへの指示";
  var IDLE = "コピー";
  var DONE = "コピーしました";
  var FAILED = "コピーできませんでした";

  // 古いやり方。https でない環境と、下の clipboard API が断られたときの受け皿。
  // clipboard API は「ページにフォーカスが無い」だけでも失敗するので、
  // 断られたら黙ってこちらに落とす（利用者から見れば成功したほうがよい）。
  function copyByTextarea(text) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.top = "0";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      area.setSelectionRange(0, text.length);
      var ok = false;
      try {
        ok = document.execCommand("copy");
      } catch (e) {
        ok = false;
      }
      document.body.removeChild(area);
      ok ? resolve() : reject(new Error("copy failed"));
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        return copyByTextarea(text);
      });
    }
    return copyByTextarea(text);
  }

  function decorate(prompt, index) {
    var box = document.createElement("div");
    box.className = "prompt-box";

    var head = document.createElement("div");
    head.className = "prompt-head";

    var label = document.createElement("span");
    label.className = "prompt-label";
    label.textContent = LABEL;

    var button = document.createElement("button");
    button.type = "button";
    button.className = "prompt-copy";
    button.textContent = IDLE;
    // 読み上げ環境でどの指示文のボタンか分かるようにする
    button.setAttribute("aria-label", LABEL + " " + (index + 1) + " をコピー");

    head.appendChild(label);
    head.appendChild(button);

    prompt.parentNode.insertBefore(box, prompt);
    box.appendChild(head);
    box.appendChild(prompt);

    var timer = null;
    button.addEventListener("click", function () {
      // 元の指示文だけを渡す。ボタンは prompt の外に置いてあるので混ざらない
      copyText(prompt.textContent).then(
        function () {
          finish(DONE, true);
        },
        function () {
          finish(FAILED, false);
        }
      );
    });

    function finish(message, ok) {
      button.textContent = message;
      button.classList.toggle("is-done", ok);
      button.classList.toggle("is-failed", !ok);
      window.clearTimeout(timer);
      timer = window.setTimeout(function () {
        button.textContent = IDLE;
        button.classList.remove("is-done", "is-failed");
      }, 2000);
    }
  }

  var prompts = document.querySelectorAll(".article-body .prompt");
  for (var i = 0; i < prompts.length; i++) {
    decorate(prompts[i], i);
  }
})();
