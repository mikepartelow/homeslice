# Homeslice Infrastructure

A comprehensive Pulumi-based infrastructure for home automation services.

## Overview

This project manages a Kubernetes-based home automation infrastructure with multiple services including:

- **Backup Services**: Tidal and Todoist data backup
- **Home Automation**: Switches, buttons, chimes, and clocktime services
- **Media Services**: Sonos integration
- **Monitoring**: Grafana, Prometheus, Loki, and Promtail
- **Workflow Engine**: Flyte for data processing
- **Network Management**: UniFi controller backup

## Quick Start

### Prerequisites

- Python 3.12+
- Pulumi CLI
- Kubernetes cluster access
- UV package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pulumi

# Install dependencies
uv sync

# Configure your environment
cp .envrc.example .envrc
# Edit .envrc with your configuration

# Deploy to production
pulumi up --stack prod
```

## Configuration

The project uses Pulumi configuration for environment-specific settings. Key configuration files:

- `Pulumi.prod.yaml` - Production configuration
- `homeslice_config/` - Configuration schemas

### Adding a New Service

1. Create a new module in the appropriate directory
2. Add configuration schema to `homeslice_config/config.py`
3. Import and configure in `__main__.py`
4. Add configuration to your stack file

## Development

### Code Quality

```bash
# Run linting
make lint

# Format code
make fmt

# Type checking
uv run mypy .
```

### Testing

```bash
# Run tests (when implemented)
uv run pytest

# Run integration tests
uv run pytest tests/integration/
```

## Architecture

### Service Structure

Each service follows a consistent pattern:

```
service_name/
├── __init__.py          # Service entry point
├── service_name.py      # Main service logic
└── config.py           # Service-specific config (if needed)
```

### Kubernetes Resources

The project uses a shared Kubernetes helper library (`homeslice/`) that provides:

- Standardized deployments
- Service configurations
- Ingress rules
- Secret management
- CronJob definitions

## Monitoring

### Observability Stack

- **Grafana**: Dashboards and visualization
- **Prometheus**: Metrics collection
- **Loki**: Log aggregation
- **Promtail**: Log shipping

### Health Checks

All services include health check endpoints and proper readiness/liveness probes.

## Backup Strategy

### Automated Backups

- **Tidal**: Daily backup of music library
- **Todoist**: Daily backup of task data
- **UniFi**: Daily backup of network configuration

### GitHub Integration

Backups are automatically committed to GitHub repositories with proper authentication and encryption.

## Troubleshooting

### Common Issues

1. **Type Errors**: Run `uv run mypy .` to identify type issues
2. **Configuration Errors**: Validate config schemas with Pydantic
3. **Deployment Failures**: Check Kubernetes events and logs

### Logs

```bash
# View service logs
kubectl logs -n homeslice <service-name>

# View Pulumi logs
pulumi logs --stack prod
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:

1. Check the troubleshooting guide
2. Review existing issues
3. Create a new issue with detailed information 