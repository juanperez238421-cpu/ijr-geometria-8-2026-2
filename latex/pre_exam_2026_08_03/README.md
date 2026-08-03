# Geometry 8 Pre-Exam Workshop - LaTeX edition

This folder contains the source package for the revised 12-problem PDF workshop.

## Contents

- `Geometry8_PreExam_Workshop_12_Problems.tex.gz.b64`: gzip-compressed LaTeX source encoded as Base64.

## Restore the `.tex` file

```bash
base64 -d Geometry8_PreExam_Workshop_12_Problems.tex.gz.b64 | gzip -d > Geometry8_PreExam_Workshop_12_Problems.tex
```

## Compile

```bash
pdflatex Geometry8_PreExam_Workshop_12_Problems.tex
pdflatex Geometry8_PreExam_Workshop_12_Problems.tex
```

The document uses standard TeX Live packages, including TikZ, `tcolorbox`, `siunitx`, `fancyhdr`, `amsmath`, and `geometry`.

## Workshop structure

- 13 letter-size pages: cover plus one full page for each of 12 problems.
- 6 True/False items with required mathematical justification.
- 6 calculation problems with dedicated work areas.
- Topics: sine and cosine ratios, Pythagorean theorem, Thales proportionality, similar triangles, and right-triangle geometric-mean theorems.
- All figures are native TikZ vector graphics.
