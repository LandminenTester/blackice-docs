(() => {
  "use strict";
  const strings = JSON.parse(document.querySelector("#locale-strings").textContent);
  const t = (text) => strings[text] || text;
  const locale = document.documentElement.lang;
  const root = new URL(document.body.dataset.root, location.href);
  const dialog = document.querySelector(".search-dialog");
  const input = document.querySelector("#docs-search");
  const results = document.querySelector(".search-results");
  let indexPromise;
  let lastTrigger;

  function message(text) {
    const p = document.createElement("p");
    p.className = "search-message";
    p.textContent = text;
    results.replaceChildren(p);
  }

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(new URL("search/search_index.json", root))
        .then((response) => {
          if (!response.ok) throw new Error("Search index unavailable");
          return response.json();
        })
        .then((index) => index.docs || [])
        .catch((error) => {
          indexPromise = null;
          throw error;
        });
    }
    return indexPromise;
  }

  async function search() {
    const query = input.value.trim();
    if (!query) {
      message(t("Type to search the documentation."));
      return;
    }
    message(t("Searching the documentation…"));
    let docs;
    try {
      docs = await loadIndex();
    } catch {
      if (query !== input.value.trim()) return;
      message(t("Search could not load. Check your connection and try again."));
      const retry = document.createElement("button");
      retry.className = "search-retry";
      retry.textContent = t("Try again");
      retry.addEventListener("click", search);
      results.append(retry);
      return;
    }
    if (query !== input.value.trim()) return;
    const words = query.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const ranked = docs
      .filter((doc) => locale === "de" ? doc.location.startsWith("de/") : !doc.location.startsWith("de/"))
      .map((doc) => {
        const title = (doc.title || "").toLocaleLowerCase();
        const text = (doc.text || "").toLocaleLowerCase();
        const score = words.every(
          (word) => title.includes(word) || text.includes(word),
        )
          ? words.reduce(
              (total, word) => total + (title.includes(word) ? 15 : 1),
              0,
            ) + (!doc.location.includes("#") ? 2 : 0)
          : 0;
        return { doc, score };
      })
      .filter((result) => result.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
    if (!ranked.length) {
      message(
        t("No results. Try a resource name or a shorter phrase."),
      );
      return;
    }
    const fragment = document.createDocumentFragment();
    ranked.forEach(({ doc }) => {
      const url = new URL(doc.location, root);
      if (url.origin !== location.origin) return;
      const link = document.createElement("a");
      link.href = url.href;
      link.className = "search-result";
      const title = document.createElement("strong");
      title.textContent = doc.title;
      const summary = document.createElement("span");
      const plain = (doc.text || "")
        .replace(/<[^>]*>/g, " ")
        .replace(/\s+/g, " ")
        .trim();
      const start = Math.max(
        0,
        plain.toLocaleLowerCase().indexOf(words[0]) - 50,
      );
      summary.textContent =
        (start ? "…" : "") +
        plain.slice(start, start + 180) +
        (plain.length > start + 180 ? "…" : "");
      const path = document.createElement("span");
      path.className = "result-path";
      path.textContent =
        doc.location.split("#")[0].replace(/\/$/, "").replaceAll("/", " / ") ||
        t("Resource library");
      link.append(title, summary, path);
      link.addEventListener("click", () => dialog.close());
      fragment.append(link);
    });
    results.replaceChildren(fragment);
  }

  document.querySelectorAll("[data-search-open]").forEach((button) =>
    button.addEventListener("click", () => {
      lastTrigger = button;
      dialog.showModal();
      input.focus();
      loadIndex().catch(() => {});
    }),
  );
  document
    .querySelector("[data-search-close]")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => lastTrigger?.focus());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      const bounds = dialog.getBoundingClientRect();
      if (
        event.clientX < bounds.left ||
        event.clientX > bounds.right ||
        event.clientY < bounds.top ||
        event.clientY > bounds.bottom
      )
        dialog.close();
    }
  });
  let debounce;
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(search, 100);
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      results.querySelector("a")?.focus();
    }
  });
  results.addEventListener("keydown", (event) => {
    const links = [...results.querySelectorAll("a")];
    const position = links.indexOf(document.activeElement);
    if (event.key === "ArrowDown" && position >= 0) {
      event.preventDefault();
      links[(position + 1) % links.length]?.focus();
    }
    if (event.key === "ArrowUp" && position >= 0) {
      event.preventDefault();
      if (!position) input.focus();
      else links[position - 1]?.focus();
    }
  });
  document.addEventListener("keydown", (event) => {
    const editable = event.target.closest(
      'input,textarea,[contenteditable="true"]',
    );
    if (
      ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") ||
      (event.key === "/" && !editable)
    ) {
      event.preventDefault();
      if (dialog.open) dialog.close();
      else document.querySelector("[data-search-open]").click();
    }
  });

  const menuButton = document.querySelector(".menu-toggle");
  const sidebar = document.querySelector(".sidebar");
  const mobile = matchMedia("(max-width: 820px)");
  function setMenu(open) {
    document.body.classList.toggle("nav-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute(
      "aria-label",
      open ? t("Close navigation") : t("Open navigation"),
    );
    sidebar.inert = mobile.matches && !open;
    if (mobile.matches && open) sidebar.querySelector("a")?.focus();
  }
  menuButton.addEventListener("click", () =>
    setMenu(!document.body.classList.contains("nav-open")),
  );
  document.querySelector(".nav-scrim").addEventListener("click", () => {
    setMenu(false);
    menuButton.focus();
  });
  mobile.addEventListener("change", () => setMenu(false));
  setMenu(false);
  document.addEventListener("keydown", (event) => {
    if (
      !mobile.matches ||
      !document.body.classList.contains("nav-open") ||
      dialog.open
    )
      return;
    if (event.key === "Escape") {
      setMenu(false);
      menuButton.focus();
    }
    if (event.key === "Tab") {
      const controls = [
        menuButton,
        ...sidebar.querySelectorAll("a,summary"),
      ].filter((element) => element.getClientRects().length);
      const position = controls.indexOf(document.activeElement);
      event.preventDefault();
      controls[
        (position + (event.shiftKey ? -1 : 1) + controls.length) %
          controls.length
      ]?.focus();
    }
  });

  document.querySelectorAll(".document pre").forEach((pre) => {
    const wrapper = pre.closest(".codehilite") || pre;
    const button = document.createElement("button");
    button.className = "copy-code";
    button.textContent = t("Copy");
    button.setAttribute("aria-label", t("Copy code to clipboard"));
    button.addEventListener("click", async () => {
      const code = pre.querySelector("code")?.innerText;
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = t("Copied");
      } catch {
        button.textContent = t("Select code");
        const selection = getSelection();
        const range = document.createRange();
        range.selectNodeContents(pre.querySelector("code"));
        selection.removeAllRanges();
        selection.addRange(range);
      }
      setTimeout(() => {
        button.textContent = t("Copy");
      }, 1800);
    });
    wrapper.append(button);
  });

  const indexLinks = [...document.querySelectorAll(".page-index nav a")];
  if (indexLinks.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          indexLinks.forEach((link) => {
            const active =
              decodeURIComponent(link.hash.slice(1)) === entry.target.id;
            link.classList.toggle("active", active);
            if (active) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-100px 0px -65% 0px" },
    );
    indexLinks.forEach((link) => {
      const heading = document.getElementById(
        decodeURIComponent(link.hash.slice(1)),
      );
      if (heading) observer.observe(heading);
    });
  }
})();
