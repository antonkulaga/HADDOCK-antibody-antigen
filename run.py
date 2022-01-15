#!/usr/bin/env python

import click
import ImmunoPDB
import ab_haddock_format
from pathlib import Path
from pdbtools import pdb_tidy


def tidy_up(file: Path, where: Path) -> Path:
    with where.open("w") as f:
        new_pdb = pdb_tidy.run(file.open("r"), False)
        for line in new_pdb:
            f.write(line)
    return where


def process_pdb(pdb_path: Path, output_path: Path, scheme: str, fvonly: bool, rename: bool, splitscfv: bool, chain: str, delete_intermediate: bool) -> Path:
    output_path.mkdir(exist_ok=True)
    pdb_name = pdb_path.name
    # Format the antibody in order to fit the HADDOCK format requirements
    print(f"processing pdb {str(pdb_path)}, results will be saved to {output_path}")
    annotated_pdb = (output_path / pdb_name.replace(".pdb", f"_{scheme}.pdb")).resolve()
    ImmunoPDB.main(inputstructure=str(pdb_path), outfile=str(annotated_pdb), scheme=scheme, fvonly=fvonly, rename=rename, splitscfv=splitscfv)
    print(f"pdb annotated as {annotated_pdb}")
    haddock_pdb = (output_path / pdb_name.replace(".pdb", f"_HADDOCK.pdb")).resolve()
    # file to save active sites
    active_sites_file = output_path / pdb_name.replace(".pdb", f"_active.txt")
    ab_haddock_format.main(pdb_file=str(annotated_pdb),
                           out_file=str(haddock_pdb),
                           chain_id=chain,
                           active_sites_file=str(active_sites_file)
                           )
    print(f"pdb ported to haddock format and saved as {haddock_pdb}")
    print(f"active residues saved as {active_sites_file}")
    tidy_pdb = (output_path / pdb_name.replace(".pdb", f"_HADDOCK_tidy.pdb")).resolve()
    tidy_up(haddock_pdb, tidy_pdb)
    if delete_intermediate:
        annotated_pdb.unlink(missing_ok=True)
        haddock_pdb.unlink(missing_ok=True)
        print("intermediate files deleted")
    print(f"final pdb saved as {tidy_pdb}")
    return tidy_pdb


def process_folder(pdb_path: Path, output_path: Path, scheme: str, fvonly: bool, rename: bool, splitscfv: bool, chain: str, delete_intermediate: bool) -> Path:
    print(f"{str(pdb_path)} is folder, processing all subfolders and pdb files inside of it!")
    for child in pdb_path.iterdir():
        output_subpath = output_path / child.name
        if child.is_dir() and not child.is_symlink() and any(child.iterdir()):
            output_subpath.mkdir(exist_ok=True)
            process_folder(child, output_subpath, scheme, fvonly, rename, splitscfv, chain, delete_intermediate)
        elif child.is_file() and "pdb" in child.suffix:
            process_pdb(child, output_subpath, scheme, fvonly, rename, splitscfv, chain, delete_intermediate)
    return output_path


@click.command()
@click.option('--pdb', type=click.Path(exists=True), help='pdb file or a folder with pdb files to run protocol at, for example 4G6K.pdb (file) or my_antibodies (folder)')
@click.option('--output', default="output", help='output folder to store results')
@click.option('--scheme', default="c", help="numbering scheme")
@click.option('--fvonly', default=True, help="use only fv region")
@click.option('--rename', default=True, help="renaming")
@click.option('--splitscfv', default=True, help="splitscfv")
@click.option('--chain', default="A", help="chain to extract active regions from")
@click.option('--delete_intermediate', default=False, help="Delete intermediate files")
def cli(pdb: str, output: str, scheme: str, fvonly: bool, rename: bool, splitscfv: bool, chain: str, delete_intermediate: bool):
    output_path = Path(output).resolve()
    output_path.mkdir(exist_ok=True)
    pdb_path = Path(pdb).resolve()
    if pdb_path.is_dir():
        process_folder(pdb_path, output_path, scheme, fvonly, rename, splitscfv, chain, delete_intermediate)
    else:
        process_pdb(pdb_path, output_path, scheme, fvonly, rename, splitscfv, chain, delete_intermediate)


if __name__ == '__main__':
    cli()
