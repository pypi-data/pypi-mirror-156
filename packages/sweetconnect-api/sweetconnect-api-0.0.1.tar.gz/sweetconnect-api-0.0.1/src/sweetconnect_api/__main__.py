"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """SweetConnect API Library."""


if __name__ == "__main__":
    main(prog_name="sweetpy")  # pragma: no cover
