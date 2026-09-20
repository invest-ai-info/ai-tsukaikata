// サイト内検索（/search/ だけで読む）。
//
// 索引は /search.json（ビルドが記事から作る。タイトル・説明文・タグ・見出し）。
// 探し方は「部分一致の AND」。日本語は単語の切れ目が無いので、分かち書きせずに
// 文字列の部分一致で当てるのがいちばん素直。全角・大文字は NFKC と小文字化で揃える
// （索引側は生の文字なので、索引と入力の両方をここで同じ規則に通す）。
// JavaScript が無い環境では <noscript> の案内だけが見える（壊れない）。
(function () {
  "use strict";

  var INDEX_URL = "/search.json";
  var DEBOUNCE_MS = 150;
  // 当たり方の点。タイトル > タグ > 説明文 > 見出し。語ごとに最も高い当たり方を採る
  var WEIGHTS = { title: 4, tags: 3, description: 2, headings: 1 };
  var EMPTY_HINT = "言葉を入れると、タイトル・説明文・タグ・見出しから探します。例: Gmail、副業、GitHub Actions";

  var form = document.getElementById("search-form");
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var status = document.getElementById("search-status");
  if (!form || !input || !results || !status) return;

  function normalize(text) {
    return String(text || "").normalize("NFKC").toLowerCase();
  }

  function terms(query) {
    return normalize(query).split(/\s+/).filter(function (t) { return t.length > 0; });
  }

  // 索引1件を正規化済みの「探す文字」に変えておく（入力のたびに正規化しないため）。
  // タグは空白でつなぐ。語は空白を含まないので、2つのタグにまたがって当たることはない
  function prepare(entry) {
    return {
      entry: entry,
      title: normalize(entry.title),
      tags: normalize((entry.tags || []).join(" ")),
      description: normalize(entry.description),
      headings: (entry.headings || []).map(normalize)
    };
  }

  // 1語の当たり方の点。どこにも無ければ 0
  function scoreTerm(item, term) {
    if (item.title.indexOf(term) !== -1) return WEIGHTS.title;
    if (item.tags.indexOf(term) !== -1) return WEIGHTS.tags;
    if (item.description.indexOf(term) !== -1) return WEIGHTS.description;
    for (var i = 0; i < item.headings.length; i++) {
      if (item.headings[i].indexOf(term) !== -1) return WEIGHTS.headings;
    }
    return 0;
  }

  function search(items, words) {
    var hits = [];
    items.forEach(function (item) {
      var total = 0;
      for (var i = 0; i < words.length; i++) {
        var score = scoreTerm(item, words[i]);
        if (score === 0) return;          // AND: 1語でも無ければ外す
        total += score;
      }
      hits.push({ item: item, score: total });
    });
    hits.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      // 同点は新しい順（published は YYYY-MM-DD なので文字列の比較でよい）
      if (a.item.entry.published === b.item.entry.published) return 0;
      return a.item.entry.published < b.item.entry.published ? 1 : -1;
    });
    return hits;
  }

  // 見出しだけに当たった語があれば、その見出し（生の文字）を返す。無ければ null
  function matchedHeading(item, words) {
    for (var w = 0; w < words.length; w++) {
      if (scoreTerm(item, words[w]) !== WEIGHTS.headings) continue;
      for (var i = 0; i < item.headings.length; i++) {
        if (item.headings[i].indexOf(words[w]) !== -1) return item.entry.headings[i];
      }
    }
    return null;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;   // 索引の文字を HTML として解釈しない
    return node;
  }

  function jpDate(iso) {                 // "2026-09-20" → "2026年9月20日"
    var p = String(iso).split("-");
    if (p.length !== 3) return String(iso);
    return p[0] + "年" + Number(p[1]) + "月" + Number(p[2]) + "日";
  }

  function renderHit(hit, words) {
    var e = hit.item.entry;
    var card = el("article", "card");
    var body = el("div", "card-body");
    var title = el("h2", "card-title");
    var link = el("a", null, e.title);
    link.href = e.url;
    title.appendChild(link);
    body.appendChild(title);
    body.appendChild(el("p", "card-description", e.description));
    var heading = matchedHeading(hit.item, words);
    if (heading) body.appendChild(el("p", "search-hint", "見出し「" + heading + "」に一致"));
    var meta = el("p", "card-meta");
    if (e.category_label) meta.appendChild(el("span", "card-badge", e.category_label));
    if (e.scene && e.scene_label) {
      var scene = el("a", "card-scene sc-" + e.scene, e.scene_label);
      scene.href = "/scenes/" + e.scene + "/";
      meta.appendChild(scene);
    }
    var time = el("time", null, jpDate(e.published));
    time.setAttribute("datetime", e.published);
    meta.appendChild(time);
    body.appendChild(meta);
    card.appendChild(body);
    return card;
  }

  function renderEmpty(query) {
    var p = el("p", "search-noscript", "「" + query + "」に当たる記事は見つかりませんでした。別の言葉で試すか、");
    var recipes = el("a", null, "レシピ一覧");
    recipes.href = "/recipes/";
    var tools = el("a", null, "深掘り記事の一覧");
    tools.href = "/tools/";
    p.appendChild(recipes);
    p.appendChild(document.createTextNode("・"));
    p.appendChild(tools);
    p.appendChild(document.createTextNode("から探してください。"));
    return p;
  }

  function syncUrl(query) {
    if (!window.history || !window.history.replaceState) return;
    var url = query ? "/search/?q=" + encodeURIComponent(query) : "/search/";
    window.history.replaceState(null, "", url);
  }

  function run(items) {
    var query = input.value.trim();
    var words = terms(query);
    syncUrl(query);
    while (results.firstChild) results.removeChild(results.firstChild);
    if (words.length === 0) {
      status.textContent = EMPTY_HINT;
      return;
    }
    var hits = search(items, words);
    if (hits.length === 0) {
      status.textContent = "0件";
      results.appendChild(renderEmpty(query));
      return;
    }
    status.textContent = "「" + query + "」に当たる記事: " + hits.length + "件";
    hits.forEach(function (hit) { results.appendChild(renderHit(hit, words)); });
  }

  function start() {
    var initial = new URLSearchParams(window.location.search).get("q") || "";
    input.value = initial;
    status.textContent = "索引を読み込んでいます…";
    fetch(INDEX_URL).then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    }).then(function (entries) {
      var items = entries.map(prepare);
      var timer = null;
      input.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () { run(items); }, DEBOUNCE_MS);
      });
      form.addEventListener("submit", function (event) {
        event.preventDefault();           // 素のフォームの送信（ページ再読み込み）を止めてその場で絞る
        if (timer) clearTimeout(timer);
        run(items);
      });
      run(items);
      input.focus();
    }).catch(function () {
      // 黙って空にしない。読めなかったことを利用者に見せる
      status.textContent = "検索を読み込めませんでした。ページを再読み込みしてください。";
    });
  }

  start();
})();
