# Helm Charts Version Management

## Overview

This directory contains Helm charts for deploying the AI Observability Summarizer. The version management has been centralized in the Makefile using Helm's `--set` option.

## Version Management

### How It Works

1. **Version is defined in Makefile**: `VERSION ?= 0.1.2`
2. **Helm commands use `--set`**: `--set image.tag=$(VERSION)`
3. **Values override defaults**: Helm automatically overrides values.yaml defaults
4. **No file generation needed**: Direct helm command execution

### Values Files
- **`values.yaml`** - Default values (can be edited directly)
- **Version override**: Happens via `--set image.tag=$(VERSION)` in helm commands

## Usage

### Deploy with Default Version
```bash
make install NAMESPACE=my-namespace
```

### Deploy with Custom Version
```bash
VERSION=v1.0.0 make install NAMESPACE=my-namespace
```

## File Structure

```
deploy/helm/
├── ui/
│   ├── values.yaml            # Default values (edit this)
│   └── Chart.yaml
├── metrics-api/
│   ├── values.yaml            # Default values (edit this)
│   └── Chart.yaml
├── alerting/
│   ├── values.yaml            # Default values (edit this)
│   └── Chart.yaml
└── README.md                   # This file
```

## Important Notes

- **Edit `values.yaml`** files directly to change default values
- **Version changes** should be made in the Makefile `VERSION` variable
- **Helm `--set`** automatically overrides values.yaml defaults
- **No template system** - simple and straightforward approach

## How Helm Override Works

```bash
# Helm command with --set
helm upgrade --install my-release ./chart \
  --set image.tag=v1.0.0

# This overrides any image.tag value in values.yaml
# If values.yaml has image.tag: 0.1.2, it becomes v1.0.0
```

## Benefits of This Approach

- **Simpler**: No template files or generation needed
- **Standard**: Uses Helm's built-in override mechanism
- **Flexible**: Can override any value, not just version
- **Maintainable**: Less complex than template systems
- **Debugging**: Easy to see what values are being used
