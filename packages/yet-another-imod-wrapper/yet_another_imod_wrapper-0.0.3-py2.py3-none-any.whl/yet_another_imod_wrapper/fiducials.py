from os import PathLike
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from packaging import version

from .batchruntomo_config.io import read_adoc
from .constants import TARGET_PIXEL_SIZE_FOR_ALIGNMENT, BATCHRUNTOMO_CONFIG_FIDUCIALS, REQUIRED_IMOD_VERSION
from .utils import (
    find_optimal_power_of_2_binning_factor,
    prepare_imod_directory,
    run_batchruntomo,
    imod_is_installed,
    get_imod_version
)

console = Console(record=True)

def run_fiducial_based_alignment(
        tilt_series_file: Path,
        tilt_angles: List[float],
        pixel_size: float,
        fiducial_size: float,
        nominal_rotation_angle: float,
        output_directory: Path,
):
    """Run fiducial based alignment in IMOD on a single tilt-series.

    Parameters
    ----------
    tilt_series_file: file containing tilt-series images.
        File must be compatible with the version of IMOD installed.
    tilt_angles: nominal stage tilt-angles from the microscope.
    pixel_size: nominal pixel size in Angstroms per pixel.
    fiducial_size: approximate size of fiducials in nanometers.
    nominal_rotation_angle: initial estimate for the rotation angle of the tilt
        axis. https://bio3d.colorado.edu/imod/doc/tomoguide.html#UnknownAxisAngle
    output_directory: tilt-series directory for IMOD.
    """
    if not imod_is_installed():
        e = 'No IMOD installation found.'
        console.log(f'ERROR: {e}')
        raise RuntimeError(e)
    imod_version = get_imod_version()
    if imod_version < version.parse(REQUIRED_IMOD_VERSION):
        e = f'Ensure IMOD version {REQUIRED_IMOD_VERSION} or higher is installed. Your version is {imod_version}'
        console.log(f'ERROR: {e}')
    prepare_imod_directory(
        tilt_series_file=tilt_series_file,
        tilt_angles=tilt_angles,
        imod_directory=output_directory
    )
    directive = generate_fiducial_alignment_directive(
        tilt_series_file=tilt_series_file,
        pixel_size=pixel_size,
        fiducial_size=fiducial_size,
        rotation_angle=nominal_rotation_angle
    )
    run_batchruntomo(
        tilt_series_file=tilt_series_file,
        imod_directory=output_directory,
        directive=directive
    )


def generate_fiducial_alignment_directive(
        tilt_series_file: PathLike,
        pixel_size: float,
        fiducial_size: float,
        rotation_angle: float
) -> Dict[str, Any]:
    """Generate a fiducial-based alignment directive file for batchruntomo

    Parameters
    ----------
    tilt_series_file : file containing the tilt-series stack
    pixel_size : pixel size in the tilt-series (angstroms per pixel)
    fiducial_size : fiducial size (nanometers)
    rotation_angle : initial estimate for the rotation angle
        https://bio3d.colorado.edu/imod/doc/tomoguide.html#UnknownAxisAngle
    """
    alignment_binning_factor = find_optimal_power_of_2_binning_factor(
        src_pixel_size=pixel_size, target_pixel_size=TARGET_PIXEL_SIZE_FOR_ALIGNMENT
    )
    directive = read_adoc(BATCHRUNTOMO_CONFIG_FIDUCIALS)
    directive['setupset.copyarg.stackext'] = Path(tilt_series_file).suffix
    directive['setupset.copyarg.rotation'] = str(rotation_angle)
    directive['setupset.copyarg.pixel'] = str(pixel_size / 10)
    directive['setupset.copyarg.gold'] = str(fiducial_size)
    directive['comparam.prenewst.newstack.BinByFactor'] = str(alignment_binning_factor)
    return directive
