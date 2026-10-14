#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insere le schema NNUE (genere par veille-emploi/.../generer_schema.py) dans les
articles FR et EN a la place de l'ancien schema d'architecture, qui montrait la meme
chose en moins detaille.

Source unique de verite : nnue-architecture[-en].svg, genere avec --sans-fond
(le CSS du theme sombre impose son propre fond sur les SVG inline).

Usage :
    python3 outils/inserer_schema_nnue.py \
        --src /chemin/vers/linkedin/post-nnue
"""
import argparse
import re
import sys
from pathlib import Path

ARTICLES = {
    'fr': Path('src/posts/8-nnue-et-machine-learning.md'),
    'en': Path('src/en/posts/8-nnue-and-machine-learning.md'),
}
SVG = {'fr': 'nnue-architecture.svg', 'en': 'nnue-architecture-en.svg'}
CAPTION = {
    'fr': "De la position au score : l'échiquier encodé en features binaires, "
          "l'accumulateur linéaire entretenu par différences, et la petite tête "
          "non linéaire recalculée à chaque évaluation. Schéma non à l'échelle.",
    'en': "From position to score: the board encoded as binary features, the linear "
          "accumulator maintained by differences, and the small non-linear head "
          "recomputed at every evaluation. Diagram not to scale.",
}


def echappe(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def construire(svg_txt):
    """Retire le rect de fond (le theme sombre du blog fournit le sien) et
    prefixe classes et ids pour eviter toute collision avec le CSS de la page.

    Ordre important : on renomme D'ABORD les selecteurs du bloc <style>, ensuite
    les attributs class=, sinon on obtient nnue-nnue-ttl."""
    svg_txt = re.sub(r'<rect x="0" y="0" width="\d+" height="\d+" fill="#fdfcfa"/>', '', svg_txt)

    debut = svg_txt.index('<style>')
    fin = svg_txt.index('</style>')
    bloc = re.sub(r'\.([a-z][a-z-]*)', lambda m: '.nnue-' + m.group(1), svg_txt[debut:fin])
    svg_txt = svg_txt[:debut] + bloc + svg_txt[fin:]

    svg_txt = re.sub(r'class="([a-z][a-z-]*)"', lambda m: 'class="nnue-%s"' % m.group(1), svg_txt)

    # /!\ markdown-it (Eleventy) traite <g>, <text>, <rect>, <circle>, <line>...
    # comme des balises de BLOC : il ferme le bloc HTML a chaque fin de ligne et
    # enveloppe la suite dans <p>, ce qui detruit le SVG. Un SVG inline dans un .md
    # doit donc tenir sur UNE SEULE ligne.
    return svg_txt.replace('\n', ' ').strip()


def traiter(langue, src, racine, essai=False):
    chemin = racine / ARTICLES[langue]
    texte = chemin.read_text(encoding='utf-8')
    svg_inline = construire((src / SVG[langue]).read_text(encoding="utf-8"))

    # Idempotent : on remplace aussi bien l'ancien schema d'architecture
    # (840 x 224) que celui qu'on a deja insere (2100 x 920).
    motif = re.compile(
        r'<figure>\n<svg viewBox="0 0 (?:840 224|2100 920)".*?</svg>\n'
        r'<figcaption>.*?</figcaption>\n</figure>',
        re.S)
    trouve = motif.search(texte)
    if not trouve:
        print(f"  [{langue}] SCHEMA INTROUVABLE — rien fait", file=sys.stderr)
        return False

    nouveau = (f'<figure>\n{svg_inline}\n'
               f'<figcaption>{echappe(CAPTION[langue])}</figcaption>\n</figure>')
    texte = texte[:trouve.start()] + nouveau + texte[trouve.end():]
    if not essai:
        chemin.write_text(texte, encoding='utf-8')
    print(f"  [{langue}] {chemin} : schema remplace "
          f"({len(trouve.group(0))} -> {len(nouveau)} caracteres)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='dossier contenant les SVG generes')
    ap.add_argument('--racine', default='.', help='racine du depot du blog')
    ap.add_argument('--essai', action='store_true', help='ne rien ecrire')
    a = ap.parse_args()
    src, racine = Path(a.src), Path(a.racine)
    for langue in ('fr', 'en'):
        if not (src / SVG[langue]).exists():
            print(f"  [{langue}] SVG absent : {src / SVG[langue]}", file=sys.stderr)
            return 1
    ok = all(traiter(l, src, racine, a.essai) for l in ('fr', 'en'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
