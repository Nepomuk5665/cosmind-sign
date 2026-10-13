# Cosmind Sign

Cosmind Sign is [DocuSeal](https://github.com/docusealco/docuseal), the open-source document signing
service, with the Cosmind brand. Cosmind runs it for the contracts its clients sign. This repository,
<https://github.com/Nepomuk5665/cosmind-sign>, holds everything we changed, so that everyone who
uses the service can get its source, as the licence asks (below).

We changed no code. The image is DocuSeal's own image, and the build copies our files over it:
view partials, icons and one stylesheet. Nothing is compiled or run in the build.

## Upstream

| | |
|---|---|
| DocuSeal version | 3.3.0, released 2026-09-28 |
| Source | <https://github.com/docusealco/docuseal/tree/3.3.0>, commit `44dcc7f312f0f6ca30d8bb9630117fa0c99bd987` |
| Image | `docker.io/docuseal/docuseal:3.3.0` |
| Image digest (linux/arm64), the base we build on | `sha256:f8af4c00b05421fb425a46b6587d696f7756b02a9fe4ecdd1d825ad00cbb2ac6` |
| Image index digest (all platforms) | `sha256:6b12e739c3c7c0e824d5e7b08697f724f3fcad848d1a866dc1b6f88ba54e3a02` |

The Corresponding Source of what we run is DocuSeal's source at that commit plus this repository.
Each image we run is tagged `src-<12 hex digits>`, a hash of this repository's files; the git tag
of the same name here holds exactly the files it was built from.

## What we changed

Everything is in `overrides/`, at the path it replaces in DocuSeal's image (`/app/...`):

| File | Change |
|---|---|
| `app/views/shared/_logo.html.erb` | The Cosmind mark instead of DocuSeal's logo, wherever DocuSeal renders its logo partial |
| `app/views/shared/_title.html.erb` | The top bar: the mark and "COSMIND sign" |
| `app/views/submit_form/_docuseal_logo.html.erb`, `app/views/start_form/_docuseal_logo.html.erb` | The same above the signing form and on its completed page; no link to the sign-in |
| `app/views/layouts/_head_tags.html.erb`, `app/views/shared/_html_title.html.erb`, `app/views/shared/_meta.html.erb` | Page titles ("Cosmind Sign"), the description and link preview, and our stylesheet |
| `app/views/layouts/application.html.erb` | DocuSeal's layout plus one footer line: the attribution (below) under the sign-in, setup and signed-in pages, where the top bar used to name DocuSeal |
| `app/views/shared/_powered_by.html.erb` | DocuSeal's attribution, unchanged, and a "Source" link to this repository next to it |
| `app/views/layouts/mailer.html.erb` | The e-mail layout: a header with "COSMIND sign" and our colours; DocuSeal's own footer line stays |
| `app/views/pwa/manifest.json.erb` | The web app manifest's name and colours |
| `public/favicon*`, `public/apple-*.png`, `public/preview.png` | Icons and the link preview image, rendered from `brand/*.svg` by `brand/render.sh` |
| `public/packs/cosmind/sign.css` | Our stylesheet: the colours and font of Cosmind's other apps, set through DocuSeal's theme variables |

The template builder, which only Cosmind's administrators see, keeps DocuSeal's logo: it is part of
DocuSeal's compiled scripts, which we do not change.

## Licence

DocuSeal is licensed under the GNU Affero General Public License, version 3 (`LICENSE`), with one
additional term (`LICENSE_ADDITIONAL_TERMS`, under section 7(b) of that licence):

> In accordance with Section 7(b) of the GNU Affero General Public License, a covered work must
> retain the original DocuSeal attribution in interactive user interfaces.

Our changes are licensed under the same terms. How we keep them:

- **The attribution.** "Powered by DocuSeal - open source documents software", with its link, stays
  on every page where DocuSeal shows it: the signing form, its completed page and the other pages a
  signer can reach. It is also under every page that shows our top bar (the sign-in and setup pages
  and the pages after sign-in), because the top bar no longer names DocuSeal. Our stylesheet hides
  none of it. DocuSeal's footer line in its e-mails stays too.
- **The source (section 13).** Next to the attribution, a "Source" link points to this repository.

## Build

```bash
docker build --platform linux/arm64 -t cosmind-sign .
```

The `Dockerfile` builds on DocuSeal's image by digest. Our own build passes the same digest from
our registry's mirror (`--build-arg DOCUSEAL_IMAGE=<mirror>@sha256:...`). The image runs exactly
as DocuSeal's does; see DocuSeal's documentation for its settings.

## Checking the overrides against DocuSeal

An override replaces a DocuSeal file as a whole, so it is right only while DocuSeal's file is the
one it was made from. `upstream.json` records the SHA-256 of each file we replace, and of
DocuSeal's licence files, at the version above.

```bash
python3 check.py           # reads DocuSeal's files out of the base image (needs docker)
```

It fails when DocuSeal changed a file we replace, ships a file we add, changed its licence files,
or stopped rendering the attribution on a page that had it.

## Moving to a new DocuSeal version

1. Put the new version's linux/arm64 digest into the `Dockerfile`.
2. Run `python3 check.py`: it names every replaced file DocuSeal changed. Read DocuSeal's change
   (`git diff <old>..<new> -- <file>` in its repository) and make the same change in our override.
   If DocuSeal changed its licence files, read them again first.
3. Run `python3 check.py --record`, then `python3 check.py` again: it passes.
4. Build the image and look at the sign-in page, a signing form, its completed page and an e-mail.
