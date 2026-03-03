# homeslice

Kubernetes dumb home[^1] hub.

[^1]: like a Smart Home but more fun and less spying.

Read more about it [here](https://mikepartelow.github.io).

## Usage

Set up your [Kubernetes](http://kubernetes.io) cluster. 

Configure your build system and Kubernetes nodes to resolve `registry.localdomain` to your Docker registry.

Edit [apps/switches/switches.json](apps/switches/switches.json).

Build and push the containers to your registry.

```console
% cd homeslice
% make push
```

`make push` now publishes multi-arch images (`linux/amd64,linux/arm64`) by default.
Override platforms when needed, e.g. `DOCKER_PLATFORMS=linux/arm64 make push`.

Edit [pulumi/Pulumi.prod.yaml] and [pulumi/subst_address.json].

Deploy with [pulumi](https://www.pulumi.com).

```console
% pulumi up
```

Now, enjoy the benefits of relatively low latency IoT light switches, the excitement of LRU cached REST API accessible remote smart button state, and periodic Todoist backups!
