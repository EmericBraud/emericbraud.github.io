// Cle commune a un article et a sa traduction : le nom du fichier francais
module.exports = { eleventyComputed: { translationKey: (data) => data.page.fileSlug } };
