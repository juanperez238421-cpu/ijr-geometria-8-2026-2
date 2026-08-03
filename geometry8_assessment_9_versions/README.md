# Geometry 8 - Nine-PC Pre-Exam System

This directory adds the classroom registration and analysis layer for the nine equivalent Geometry 8 pre-exam versions.

## Assignment map

| Computer | Version |
|---|---|
| PC-01 | A |
| PC-02 | B |
| PC-03 | C |
| PC-04 | D |
| PC-05 | E |
| PC-06 | F |
| PC-07 | G |
| PC-08 | H |
| PC-09 | I |

Every version contains 12 equally weighted items:

- Questions 1-6: True/False with written mathematical justification.
- Questions 7-8: sine and cosine applications.
- Questions 9-10: Pythagorean theorem.
- Questions 11-12: Thales theorem and similar triangles.

## Registration application

Run the offline standard-library application:

```bash
python geometry8_registry_app.py --host 0.0.0.0 --port 5000
```

The application:

- maps each PC to its assigned version;
- registers student, group, PC, version and 12 final answers;
- auto-scores final responses using `answer_keys.json`;
- stores submissions in SQLite;
- exports CSV data for teacher analysis.

The automatic score evaluates only the final response. Written reasoning and procedure remain subject to teacher review.

## Analysis

```bash
python analyze_answers.py --db geometry8_results.sqlite3 --out analysis_output
```

The analyzer produces student, version, question and topic CSV summaries plus an HTML report.

## Complete printable package

The complete downloadable package generated for this task additionally contains:

- nine 13-page student PDFs;
- nine complete LaTeX sources;
- the teacher answer-key PDF;
- the full package generator;
- Windows and Linux/macOS launchers;
- SHA-256 checksums and manifest.
