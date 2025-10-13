FROM golang:1.23.2@sha256:ad5c126b5cf501a8caef751a243bb717ec204ab1aa56dc41dc11be089fafcb4f AS build

WORKDIR /build

COPY go.mod go.sum .
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o . ./cmd/...

FROM build AS dev
WORKDIR /app

FROM gcr.io/distroless/static:nonroot@sha256:112a87f19e83c83711cc81ce8ed0b4d79acd65789682a6a272df57c4a0858534 AS prod

COPY --from=build /build/switches /switches

USER nonroot

ENTRYPOINT ["/switches"]
