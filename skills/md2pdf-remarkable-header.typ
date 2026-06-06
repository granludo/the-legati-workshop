// Typst header — md2pdf `remarkable` profile
//
// Included via pandoc --include-in-header on top of the standard
// remarkable-profile flags. Body text stays at 13pt; this file
// shrinks the elements that don't fit at body size on an A5 page
// rendered on a reMarkable screen.
//
// Page margins live in `md2pdf-remarkable-meta.yaml` (passed via
// pandoc --metadata-file), NOT here. pandoc's typst template emits
// its own `#set page(margin: ...)` at boilerplate time using the
// `margin` variable from metadata, and that emission happens AFTER
// any --include-in-header content — so a `#set page` here is
// overridden by pandoc's later emission. The metadata-file path is
// the supported way to control page geometry.
//
// Edit element-size values below — single source of truth for
// font-size overrides; margins live in the yaml.

// Tables: 10pt. A5 is narrow; body-size tables overflow.
#show table: set text(size: 10pt)

// Figure captions: 10pt. Body-size captions compete with the figure for attention.
#show figure.caption: set text(size: 10pt)

// Allow table-figures to break across pages. Pandoc wraps tables in
// #figure(), and figures default to a non-breakable block — a table
// taller than the remaining page space overflows instead of splitting.
// Detected on v2 of the methodology paper, page 57. We restrict the
// fix to kind=table so image-figures keep their default
// non-breakable behaviour (splitting an image across pages is worse
// than overflowing).
#show figure.where(kind: table): set block(breakable: true)
