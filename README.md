# language-tool-k8s-charm

A charm for deploying [LanguageTool](https://dev.languagetool.org/http-server) http server on Kubernetes.

See [charmhub.io listing](https://charmhub.io/language-tool-server).

## Usage

To deploy this charm, you can use the following command:

```bash
juju deploy language-tool-server --channel edge
```

You can explore the deployed workload using the following command:

```bash
kubectl -n language-tool-model get pods
kubectl -n language-tool-model describe pod language-tool-server-0
kubectl exec -it language-tool-server-0 -c language-tool -n language-tool-model -- /bin/bash
```

## Development

To develop this charm, build the OCI image using `rockcraft` and then upload it to ghcr.io.

```bash
rockcraft pack -v
rockcraft.skopeo --insecure-policy copy oci-archive:language-tool_6.6_amd64.rock docker-daemon:language-tool:6.6
docker tag b48e97207fba ghcr.io/edlerd/language-tool:6.6
docker push ghcr.io/edlerd/language-tool:6.6
```

You can then build the charm using `charmcraft`:

```bash
charmcraft build
```

With the charm in place, you can deploy it locally. We use kind to create a local kubernetes cluster and configure juju for it. Only prerequisite is a local docker daemon that Kind can bootstrap the k8s cluster in:

```bash
make dev
```

This will create a local Kubernetes cluster using Kind, configure Juju to use it, and deploy the LanguageTool charm. Check the status of the deployment with:

```bash
juju status
```

You can tear down the local Kubernetes cluster with:

```bash
make nuke
```

## Release

To build the oci image, execute rockcraft commands as follows:

```bash
rockcraft pack
rockcraft.skopeo --insecure-policy copy oci-archive:language-tool_6.6_amd64.rock docker-daemon:language-tool-image:6.6
```

Get the image id and upload it to charmhub:

```bash
docker images | grep language-tool-image
charmcraft upload-resource language-tool-server language-tool-image --image ${IMAGE_ID}
```

Build the charm using `charmcraft`, then upload and release it. Replace the `--revision` and `--resource` parameters with the appropriate values for your release:

```bash
charmcraft build
charmcraft upload language-tool-server_amd64.charm
charmcraft release language-tool-server --revision=1 --channel=edge --resource=language-tool-image:2
```