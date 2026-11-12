---
name: omics-reanalysis
description: Re-analyse and compare public omics datasets across studies, labs and pipeline versions without fooling yourself - single-cell and bulk RNA-seq, and DNA methylation. Use when integrating several public datasets, re-processing them from raw data, upgrading a pipeline mid-project, comparing a new dataset with earlier analyses, or relating RNA and DNA results. Covers getting the real raw data, one reference and pinned versions, metadata from the archive itself, QC done once, integration scored on independent labels, reference-based annotation tested before use, methylation-specific traps, and how each step is verified.
---

# Omics re-analysis across studies

Most cross-study results that fail later fail at a seam: two datasets processed differently, a label borrowed from
the method being judged, a metadata field taken from a summary instead of the archive. This skill is a checklist of
those seams. Each rule says why, and how to check it. Written from the trophoblast organoid atlas
(a 2026 project re-analysing public single-cell data) and its reviewers; the DNA methylation section is **a draft awaiting review**.

## 1. Comparable means processed the same way

- **Re-process every dataset from its raw reads**, never mix the authors' processed matrices with your own. Each
  author used their own reference, annotation and quantifier; their matrices differ in ways no batch correction
  removes cleanly.
- **One reference for all**: one genome build and one annotation release (e.g. GRCh38 + GENCODE 50), one index built
  once and reused. Record it per dataset.
- **Pin every tool to an exact release or commit**, including the workflow manager. A pipeline with no release yet is
  pinned to a full commit hash (short hashes are refused by some runners).
- **Keep a provenance table**: dataset, pipeline and version, reference, index checksum, date. A result names the run
  it came from.
- **Upgrading mid-project?** Re-run one dataset under the old and the new version, and compare cells or samples kept,
  counts per gene and one downstream result. Datasets processed under different major versions are not combined
  until they are re-run under one. "Best practice changed" is answered by that comparison, not by the changelog.

## 2. Get the raw data the archives actually keep

- **Archives differ in what they serve.** For 10x data, ENA's generated FASTQ often holds only the cDNA read; the
  barcode read survives in ENA's *submitted* files, in SRA's original reads (`fasterq-dump --include-technical`), or
  only inside a Cell Ranger BAM (10x `bamtofastq`). Generic fetchers that read the generated FASTQ silently get
  unusable data.
- **Check every file**: MD5 against the archive's; read counts against the archive's (a converted BAM's read pairs
  should equal the run's read count exactly).
- **Identify reads by content, not by file order**: barcode reads have fixed lengths (26 for 10x 3' v2, 28 for v3);
  refuse a run whose layout is ambiguous rather than guess.
- **Name the chemistry per dataset** from the archive record or the read lengths. Auto-detection is not available for
  every quantifier, and a wrong chemistry produces plausible-looking empty matrices.
- **Resume, don't restart**: keep partial downloads; checksum only finished files.

## 3. Metadata from the archive, not from summaries

- Read each dataset's sample table from its own record (ArrayExpress SDRF, GEO series characteristics). A
  registry or a search agent's summary is a lead to check, never a source.
- **Look for what the metadata does not say**: pooled donors in one library, a treatment that is constant across
  libraries because it was multiplexed within them. Per-cell donor and condition may exist only in the authors'
  processed object; join it by sample and barcode, and leave unmatched cells unlabelled.
- Harmonise into one table shape (donor, model, medium, stimulus, time in hours, cells or nuclei, chemistry) and
  refuse a sample whose rows disagree with each other.

## 4. Quality control once, with gates

- Remove ambient RNA **once**, in one place (not in both the mapping and the downstream workflow). Prefer an
  empty-droplet model (CellBender) over marker-based methods on narrow populations, where markers do not stand apart.
- **Gates before a dataset counts**: every sample present; cells per sample within reach of the paper's numbers
  (a sample far off is held, not passed on); the chemistry detected matches the archive's.

## 5. Integration, scored on labels the methods did not make

- Benchmark several integration methods (scIB metrics) against an **unintegrated baseline**.
- **Score biology against independent labels** (e.g. the authors' own annotations), never against labels produced
  by one of the methods compared: that scores a method against itself.
- Use the sample within its dataset as the batch; report dataset as a second, harder key, since part of the
  between-dataset difference is biology.
- Choose the method from the numbers, with its runner-up; an aggregate score can hide a method that removes batch by
  erasing a cell state.

## 6. Annotation from a reference, tested before use

- Transfer labels from an in vivo or curated reference (scANVI with query mapping, for example). Exclude states too
  small to learn.
- **Test the transfer on data with known labels first** (the authors' own annotations of a public dataset), per
  state; report agreement by confidence bin and pick the threshold where agreement jumps.
- A second method that disagrees is a signal, not a tiebreak: a classifier that rejects most query cells as unlike
  the reference is telling you about domain shift. Keep it as a flag; never resolve a disagreement by picking one.
- Do not use a general-purpose default annotation model on a specialised tissue (blood or immune models on
  trophoblast, for example).

## 7. DNA methylation (draft, for review)

- **Same platform, same preprocessing**: arrays (450k, EPIC v1, EPIC v2) share only part of their probes; restrict to
  the common, reliable probes and run one normalisation (e.g. SeSAMe or noob) on raw IDATs for every dataset, rather
  than combining authors' beta values.
- **Cell composition first**: tissue methylation shifts with cell mix; estimate it (reference-based deconvolution)
  and include it, or a composition change reads as an epigenetic one.
- **Stochastic or specific?** An age-related rise in variance can be genome-wide drift or concentrated at specific
  loci and regions (for example certain intergenic regions). Test both: variance per locus against age, then whether
  the high-variance loci are enriched in particular region classes, against a background matched for mean and
  coverage. "Stochastic" is a claim that needs the second test to fail. *(Reviewer's point, to expand.)*
- Bisulfite sequencing: one aligner and one methylation caller for all samples; filter by coverage the same way.

## 8. Comparing RNA with DNA

- Say whether the samples are the same individuals, matched groups, or unrelated cohorts: the inference differs.
- Map CpGs to genes by a fixed rule (promoter window, gene body) stated up front; a rule chosen after looking is a
  multiple-testing problem.
- Correct for multiple testing across the full set tested, not the set reported.

## 9. Verification

- Check each step against something outside it: an archive checksum, an archive read count, a paper's cell counts,
  the authors' labels.
- Break each test once on purpose, to see that it fails.
- Treat an agent's or a summary's claim as unchecked until read against the source.
- Know the limit: a check shares the errors of its reference. A wrong number in a paper passes a gate built on it;
  that is where a human reading the results earns its place.
