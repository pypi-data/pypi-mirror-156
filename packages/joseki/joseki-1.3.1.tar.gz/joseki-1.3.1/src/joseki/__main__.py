"""Command-line interface."""
import pathlib
import typing as t

import click

from .core import Identifier
from .core import make

IDENTIFIER_CHOICES = [identifier.value for identifier in Identifier]

INTERPOLATION_METHOD_CHOICES = [
    "linear",
    "nearest",
    "nearest-up",
    "zero",
    "slinear",
    "quadratic",
    "cubic",
    "previous",
    "next",
]


@click.command()
@click.option(
    "--file-name",
    "-f",
    help="Output file name.",
    default="ds.nc",
    show_default=True,
    type=click.Path(writable=True),
)
@click.option(
    "--identifier",
    "-i",
    help="Atmospheric profile identifier.",
    required=True,
    type=click.Choice(
        choices=IDENTIFIER_CHOICES,
        case_sensitive=True,
    ),
)
@click.option(
    "--altitudes",
    "-a",
    help=(
        "Path to level altitudes data file. The data file is read with "
        ":meth:`numpy.loadtxt`."
    ),
    default=None,
    show_default=True,
)
@click.option(
    "--altitude-units",
    "-u",
    help="Altitude units",
    default="km",
    show_default=True,
)
@click.option(
    "--represent-in-cells",
    "-r",
    help=(
        "Compute the cells representation of the atmospheric profile. The "
        "initial altitude values are used to define the altitude bounds of "
        "each cell. The pressure, temperature, number density and mixing "
        "ratio fields are interpolated at the cells' center altitudes."
    ),
    is_flag=True,
)
@click.option(
    "--p-interp-method",
    "-p",
    help="Pressure interpolation method.",
    type=click.Choice(
        INTERPOLATION_METHOD_CHOICES,
        case_sensitive=True,
    ),
    default="linear",
    show_default=True,
)
@click.option(
    "--t-interp-method",
    "-t",
    help="Temperature interpolation method.",
    type=click.Choice(
        INTERPOLATION_METHOD_CHOICES,
        case_sensitive=True,
    ),
    default="linear",
    show_default=True,
)
@click.option(
    "--n-interp-method",
    "-n",
    help="Number density interpolation method.",
    type=click.Choice(
        INTERPOLATION_METHOD_CHOICES,
        case_sensitive=True,
    ),
    default="linear",
    show_default=True,
)
@click.option(
    "--x-interp-method",
    "-x",
    help="Volume mixing ratios interpolation method.",
    type=click.Choice(
        INTERPOLATION_METHOD_CHOICES,
        case_sensitive=True,
    ),
    default="linear",
    show_default=True,
)
@click.version_option()
def main(
    file_name: str,
    identifier: str,
    altitudes: t.Optional[str],
    altitude_units: str,
    represent_in_cells: bool,
    p_interp_method: str,
    t_interp_method: str,
    n_interp_method: str,
    x_interp_method: str,
) -> None:
    """Joseki command-line interface."""
    ds = make(
        identifier=Identifier(identifier),
        altitudes=altitudes if altitudes is None else pathlib.Path(altitudes),
        altitude_units=altitude_units,
        p_interp_method=p_interp_method,
        t_interp_method=t_interp_method,
        n_interp_method=n_interp_method,
        x_interp_method=x_interp_method,
        represent_in_cells=represent_in_cells,
    )
    ds.to_netcdf(file_name)


if __name__ == "__main__":
    main(prog_name="joseki")  # pragma: no cover
