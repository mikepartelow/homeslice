FROM golang:1.21 AS build

WORKDIR /build

COPY go.mod go.sum .
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o . ./cmd/...

FROM build AS dev
WORKDIR /app

FROM gcr.io/distroless/static:nonroot AS prod

COPY --from=build /build/backup-todoist /backup-todoist

USER nonroot

ENTRYPOINT ["/backup-todoist"]
