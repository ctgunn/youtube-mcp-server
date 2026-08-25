# Archived deployment configuration

`cloudbuild.yaml` is retained only as a historical record of the former Cloud
Build deployment path. The Cloud Build triggers for this repository are
disabled, and this file must not be used to create or re-enable a trigger.

The supported hosted release procedure is the manually dispatched GitHub
Actions workflow in [`.github/workflows/hosted-deploy.yml`](../../.github/workflows/hosted-deploy.yml).
It performs safe preflight validation, runs `make quality`, deploys an
immutable image digest, records release evidence, and verifies the resulting
Cloud Run revision.
