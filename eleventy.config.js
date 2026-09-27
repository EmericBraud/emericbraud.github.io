module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");

  const byOrder = (a, b) => a.date - b.date || (a.data.chapterOrder ?? 0) - (b.data.chapterOrder ?? 0);
  eleventyConfig.addCollection("posts", (api) => api.getFilteredByGlob("src/posts/*.md").sort(byOrder));
  eleventyConfig.addCollection("postsEn", (api) => api.getFilteredByGlob("src/en/posts/*.md").sort(byOrder));

  // Meme page dans l'autre langue, retrouvee par sa translationKey ; a defaut, l'accueil de l'autre langue
  eleventyConfig.addFilter("translationUrl", (all, key, lang) => {
    const other = all.find((p) => p.data.translationKey === key && p.data.lang !== lang);
    return other ? other.url : lang === "en" ? "/" : "/en/";
  });

  eleventyConfig.addShortcode("fen", (fen, orientation = "white", caption = "") =>
    `<figure>
      <chess-board position="${fen}" orientation="${orientation}" style="width: 400px; max-width: 100%;"></chess-board>
      ${caption ? `<figcaption>${caption}</figcaption>` : ""}
    </figure>`
  );

  // Separateur de partie
  eleventyConfig.addShortcode("partie", (numero, titre) =>
    `<div class="partie"><span>${numero}</span><h2>${titre}</h2></div>`
  );

  // Bloc depliable : le lecteur presse passe, le curieux ouvre
  eleventyConfig.addPairedShortcode("plus", (content, titre) =>
    `<details class="plus">\n<summary>${titre}</summary>\n\n${content.trim()}\n\n</details>`
  );

  eleventyConfig.addFilter("readableDate", (date, locale = "fr-FR") =>
    new Date(date).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" })
  );

  return {
    dir: {
      input: "src",
      includes: "_includes",
      output: "_site",
    },
  };
};
