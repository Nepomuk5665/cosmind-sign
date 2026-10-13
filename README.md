# Cosmind Sign

Cosmind Sign is [DocuSeal](https://github.com/docusealco/docuseal), the open-source document signing
service, with the Cosmind brand. Cosmind runs it for the contracts its clients sign. This repository,
<https://github.com/Nepomuk5665/cosmind-sign>, holds everything we changed, so that everyone who
uses the service can get its source, as the licence asks (below).

The image is DocuSeal's own image, and the build copies our files over it: view partials, icons,
one stylesheet, a few English strings, two images DocuSeal draws into signed documents and one
initializer, our only code, which puts Cosmind's name into signed documents. Nothing is compiled or
run in the build.

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
| `app/views/layouts/application.html.erb`, `app/views/layouts/plain.html.erb` | DocuSeal's layouts plus one footer: the attribution (below), on every page that does not show it itself, where the top bar or the logo used to name DocuSeal |
| `app/views/shared/_powered_by.html.erb` | DocuSeal's attribution, unchanged, and a "Source" link to this repository next to it; it marks the page, so the layouts' footer never shows it twice |
| `app/views/submit_form/_submission_form.html.erb` | The signing form's script does not repeat the attribution after signing (DocuSeal's `data-attribution` switch); the line under the document stays |
| `app/views/pages/landing.html.erb` | The start page before sign-in: "Cosmind Sign", one sentence for signers, a sign-in button for Cosmind staff |
| `app/views/errors/404.html`, `422.html`, `500.html` | The error pages in the Cosmind look, with the attribution and no link to the staff-only start page |
| `app/views/newsletters/show.html.erb` | After the first setup: a "Setup is done" page instead of DocuSeal's newsletter sign-up, which sent the address to docuseal.com |
| `app/views/shared/_navbar.html.erb`, `app/views/shared/_navbar_buttons.html.erb`, `app/views/shared/_settings_nav.html.erb` | No GitHub stars, "Upgrade" button, Console or AI assistant links, no Plans, Console, SMS or SSO entries in the settings, and no DocuSeal support block (GitHub, Discord, support address, release notes) |
| `app/views/sms_settings/_placeholder.html.erb`, `app/views/sso_settings/_placeholder.html.erb`, `app/views/notifications_settings/_reminder_placeholder.html.erb`, `app/views/personalization_settings/_logo_placeholder.html.erb`, `app/views/submissions/_bulk_send_placeholder.html.erb` | DocuSeal Pro's offers replaced by one plain sentence each |
| `app/views/submissions/_send_sms_button.html.erb`, `app/views/templates_code_modal/_placeholder.html.erb`, `app/views/templates/_embedding.html.erb`, `app/views/esign_settings/_default_signature_row.html.erb`, `app/views/users/_role_select.html.erb` | No DocuSeal Pro buttons, notes or rows; the role select stays |
| `app/views/templates/edit.html.erb` | The template builder without DocuSeal's logo (its `data-with-logo` switch) |
| `app/views/templates_share_link_qr/_logo.html.erb` | The share link's QR sheet: our wordmark |
| `app/views/layouts/mailer.html.erb`, `app/views/devise/mailer/reset_password_instructions.html.erb` | The e-mail layout: a header with "COSMIND sign" and our colours; DocuSeal's own footer line stays. The reset password e-mail is signed "Cosmind Sign" |
| `app/views/pwa/manifest.json.erb` | The web app manifest's name and colours |
| `config/locales/zz_cosmind.yml` | Seven English strings that named DocuSeal: the dashboard's welcome, the invitation of a new user (subject, text, page), two tooltips and the MCP settings' title. It loads after DocuSeal's `i18n.yml`, so only these keys change |
| `config/initializers/cosmind_sign.rb` | Signed documents name Cosmind Sign: the signature's reason "Signed with Cosmind Sign" (DocuSeal: "Signed with DocuSeal.com"), the audit trail's header (the mark and "Cosmind Sign", without a link), and the PDF's creator "Cosmind Sign" where DocuSeal writes "DocuSeal (https://www.docuseal.com)". Applied once the app has loaded; `check.py` holds DocuSeal's files it reaches into to the recorded version |
| `lib/pdf_icons/logo.png`, `lib/pdf_icons/stamp-logo.png` | The mark in the audit trail's header, and the grey "COSMIND" behind a stamp field's text, at DocuSeal's sizes, rendered from `brand/mark.svg` and `brand/stamp.svg` |
| `public/favicon*`, `public/apple-*.png`, `public/preview.png` | Icons and the link preview image, rendered from `brand/*.svg` by `brand/render.sh` |
| `public/packs/cosmind/sign.css` | Our stylesheet: the colours and font of Cosmind's other apps, set through DocuSeal's theme variables |

What still names DocuSeal, and why: the attribution and DocuSeal's footer line in e-mails (the
licence); the name authenticator apps show for the two-factor code (DocuSeal's product name, which
the attribution prints too); a few things only Cosmind's administrators see inside DocuSeal's compiled template builder
(a locked Pro field with a pricing link); the link to DocuSeal's API reference in the API settings
(its documentation); and, in the E-Signature settings, the certificate DocuSeal made on its first
setup, listed as "DocuSeal Self-Host Autogenerated": it is kept so that documents it signed still
verify, and no longer signs.

Signed documents are signed with Cosmind's own certificate, "Cosmind GmbH" (self-signed), which our
deployment adds where DocuSeal keeps an uploaded certificate; this image does not make it.

## Licence

DocuSeal is licensed under the GNU Affero General Public License, version 3 (`LICENSE`), with one
additional term (`LICENSE_ADDITIONAL_TERMS`, under section 7(b) of that licence):

> In accordance with Section 7(b) of the GNU Affero General Public License, a covered work must
> retain the original DocuSeal attribution in interactive user interfaces.

Our changes are licensed under the same terms. How we keep them:

- **The attribution.** "Powered by DocuSeal - open source documents software", with its link, shows
  exactly once on every page: where DocuSeal shows it (the signing form, its completed page and the
  other pages a signer can reach), and under every other page of DocuSeal's layouts and its error
  pages, because our top bar and logo no longer name DocuSeal. Our stylesheet hides none of it.
  DocuSeal's footer line in its e-mails stays too.
- **The source (section 13).** Next to the attribution, a "Source" link points to this repository.
- **Signed documents.** A signed PDF and its audit trail are documents a signer downloads, not an
  interactive user interface, so they name Cosmind (the initializer above); every page keeps the
  attribution.

## Build

```bash
docker build --platform linux/arm64 -t cosmind-sign .
```

The `Dockerfile` builds on DocuSeal's image by digest. Our own build passes the same digest from
our registry's mirror (`--build-arg DOCUSEAL_IMAGE=<mirror>@sha256:...`). The image runs exactly
as DocuSeal's does; see DocuSeal's documentation for its settings.

## Checking the overrides against DocuSeal

An override replaces a DocuSeal file as a whole, so it is right only while DocuSeal's file is the
one it was made from. `upstream.json` records the SHA-256 of each file we replace, of the DocuSeal
files the initializer reaches into (and of `Gemfile.lock`, for the HexaPDF version), and of
DocuSeal's licence files, at the version above.

```bash
python3 check.py           # reads DocuSeal's files out of the base image (needs docker)
```

It fails when DocuSeal changed a file we replace, ships a file we add, changed its licence files,
stopped rendering the attribution on a page that had it, or changed a file the initializer relies
on.

## Moving to a new DocuSeal version

1. Put the new version's linux/arm64 digest into the `Dockerfile`.
2. Run `python3 check.py`: it names every replaced file DocuSeal changed. Read DocuSeal's change
   (`git diff <old>..<new> -- <file>` in its repository) and make the same change in our override.
   If it names a file the initializer relies on, check `config/initializers/cosmind_sign.rb`
   against DocuSeal's new file. If DocuSeal changed its licence files, read them again first.
3. Run `python3 check.py --record`, then `python3 check.py` again: it passes.
4. Build the image and look at the sign-in page, a signing form, its completed page, an e-mail,
   and a signed document with its audit trail (its reason, creator and header).
