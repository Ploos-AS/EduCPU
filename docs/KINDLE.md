# Kindle distribution

EduCPU keeps Markdown as the single source of truth. Kindle is a distribution target, not a separate source format.

## Qualified input

The ebook workflow produces and validates:

- `EduCPU-en.epub`
- `EduCPU-no.epub`

Both editions include publication metadata, a deterministic cover, table of contents and the bilingual course's corresponding solution material. CI validates both files with `epubcheck`.

## Kindle workflow

1. Build the EPUB through the repository's **Ebooks** GitHub Actions workflow.
2. Use the validated EPUB artifact for Kindle delivery.
3. For personal/device testing, submit the EPUB through Amazon's Send to Kindle service.
4. For publication, upload the same validated EPUB to Kindle Direct Publishing (KDP).
5. Preview the converted book in Amazon's current preview tooling before publication and check headings, code blocks, tables, links, cover, table of contents and page breaks.
6. Do not edit a Kindle-converted copy as a new source. Fix problems in Markdown, ebook metadata, cover assets or the build pipeline and rebuild.

## Release gate

A Kindle edition is ready for release only after:

- the corresponding EPUB passes `epubcheck`;
- the Ebooks workflow is green for the release commit;
- the converted Kindle preview has been manually inspected;
- navigation and code examples remain readable;
- metadata, language and cover match the selected edition.

The repository can automate EPUB generation and validation. Final Kindle conversion/preview is intentionally a distribution qualification step because Amazon controls that conversion.
