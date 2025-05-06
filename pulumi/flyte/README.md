# Flyte Config

Source: [https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/on-premises/single-node/002-single-node-onprem-install.md#connecting-to-flyte](https://github.com/davidmirror-ops/flyte-the-hard-way/blob/main/docs/on-premises/single-node/002-single-node-onprem-install.md#connecting-to-flyte)

```bash
sudo bash -c 'echo "127.0.0.1       minio.flyte.svc.cluster.local" >> /etc/hosts'
cp -v flyte/config.yaml ~/.flyte

kubectl --context ${CONTEXT} -n flyte port-forward service/minio 9000:9000 &
kubectl --context ${CONTEXT} -n flyte port-forward service/flyte-binary-grpc 8089:8089 &
kubectl --context ${CONTEXT} -n flyte port-forward service/flyte-binary-http 8088:8088 &

pyflyte run --remote flyte/hello_world.py my_wf
```
