# Cosmind Sign: DocuSeal 3.3.0 with the Cosmind brand (README.md). Nothing is compiled or run:
# the build copies our view partials, icons, one stylesheet, a few English strings, the images of
# signed documents and one initializer (Cosmind's name in signed documents) over DocuSeal's own image.
#
# The base is DocuSeal's linux/arm64 image by digest (upstream.json, and in our deployment
# deploy/sign/images.json). Our build passes the same digest from our own registry mirror:
#   docker build --platform linux/arm64 --build-arg DOCUSEAL_IMAGE=<mirror>@sha256:... .
ARG DOCUSEAL_IMAGE=docker.io/docuseal/docuseal@sha256:f8af4c00b05421fb425a46b6587d696f7756b02a9fe4ecdd1d825ad00cbb2ac6
FROM ${DOCUSEAL_IMAGE}

# DocuSeal's files belong to its user docuseal (2000:2000); ours do too.
COPY --chown=2000:2000 overrides/app/ /app/app/
COPY --chown=2000:2000 overrides/public/ /app/public/
COPY --chown=2000:2000 overrides/config/ /app/config/
COPY --chown=2000:2000 overrides/lib/ /app/lib/
