# Geometry 8 - Nine-PC Integrated Pre-Exam v2

This revision replaces topic-by-topic worksheet sections with two integrated sections:

- **Section A:** 8 ABCD multiple-choice questions.
- **Section B:** 4 open-response problems.

Each of the four assessed ideas appears exactly three times: two multiple-choice items and one open problem.

1. Determine missing sides using the Pythagorean theorem.
2. Use right-triangle side relationships with sine and cosine ratios.
3. Determine whether two right triangles are proportional and apply a scale factor.
4. Solve Thales theorem and similar-triangle problems.

## Nine equivalent versions

- PC-01 -> Version A
- PC-02 -> Version B
- PC-03 -> Version C
- PC-04 -> Version D
- PC-05 -> Version E
- PC-06 -> Version F
- PC-07 -> Version G
- PC-08 -> Version H
- PC-09 -> Version I

## Restore the complete source package

The repository stores the reproducible source bundle as `geometry8_v2_sources.tar.gz.b64`.

Linux/macOS:

```bash
base64 -d geometry8_v2_sources.tar.gz.b64 | tar -xz
python generate_package.py
```

PowerShell:

```powershell
[IO.File]::WriteAllBytes('geometry8_v2_sources.tar.gz',[Convert]::FromBase64String((Get-Content geometry8_v2_sources.tar.gz.b64 -Raw)))
tar -xzf geometry8_v2_sources.tar.gz
python generate_package.py
```

The restored package contains the full LaTeX/TikZ generator, the nine-version answer keys, the offline registry application, the response analyzer, and Windows launchers.

## Validation completed

- Nine student PDFs generated successfully.
- Each student PDF has 13 pages.
- Teacher answer-key PDF generated successfully.
- Automatic grading test returned 12/12 for a complete correct submission.
- Final ZIP integrity test passed.
