module.exports = function (eleventyConfig) {
  eleventyConfig.addCollection("posts", (collectionApi) => {
    return collectionApi.getFilteredByGlob("src/posts/*.md").sort((a, b) => a.date - b.date);
  });

  eleventyConfig.addShortcode("fen", (fen, orientation = "white", caption = "") =>
    `<figure>
      <chess-board position="${fen}" orientation="${orientation}" style="width: 400px; max-width: 100%;"></chess-board>
      ${caption ? `<figcaption>${caption}</figcaption>` : ""}
    </figure>`
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
