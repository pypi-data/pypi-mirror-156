"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """atomic-operator Atomic Red Team."""


if __name__ == "__main__":
    main(prog_name="atomic-operator-art")  # pragma: no cover
