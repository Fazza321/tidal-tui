# tidal-tui

A terminal UI for TIDAL built with Go and Bubble Tea.

## Installation

```
brew install open-source5784524/tidal-tui/tidal-tui
```

## Development

### Requirements

- Python 3.x
- Go 1.x
- mpv

### Building

1. Clone the repo
2. `cd backend && pip install -r requirements.txt`
3. `cd frontend && go build -o tidal-tui`

## Usage

```
./tidal-tui
```

On first launch you'll be prompted to log in to TIDAL.

## Contributing

Open an issue before starting work on anything significant so we can discuss it first.
PRs should be one feature or fix per branch.
Run backend tests with `pytest` and frontend tests with `go test ./...`.

## License

GPL v3. See [LICENSE](LICENSE).
