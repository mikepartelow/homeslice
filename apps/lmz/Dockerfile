FROM golang:1.22.6@sha256:87bbc3e8e2c7cb625d09ed4c3ae4663e3ba4e64c6e59797a7ec1e3da7d972f7b AS build

WORKDIR /build

COPY go.mod go.sum .
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o . ./cmd/...

FROM build AS dev
WORKDIR /app

FROM gcr.io/distroless/static:nonroot@sha256:112a87f19e83c83711cc81ce8ed0b4d79acd65789682a6a272df57c4a0858534 AS prod

COPY --from=build /build/lmz /lmz

USER nonroot

ENTRYPOINT ["/lmz"]
