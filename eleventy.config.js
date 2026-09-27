module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");

  eleventyConfig.addCollection("posts", (collectionApi) => {
    return collectionApi
      .getFilteredByGlob("src/posts/*.md")
      .sort((a, b) => a.date - b.date || (a.data.chapterOrder ?? 0) - (b.data.chapterOrder ?? 0));
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

  eleventyConfig.addFilter("readableDate", (date) =>
    new Date(date).toLocaleDateString("fr-FR", { year: "numeric", month: "long", day: "numeric" })
  );

  return {
    dir: {
      input: "src",
      includes: "_includes",
      output: "_site",
    },
  };
};
