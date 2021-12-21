import click
import ImmunoPDB
import ab_haddock_format
from pathlib import Path
import sys
from pdbtools import pdb_tidy

def tidy_up(file: Path, where: Path):
    with file.open("r") as fh:
        with where.open("a") as f:
            new_pdb = pdb_tidy.run(fh, False)
            n = 5000
            try:
                _buffer = []
                _buffer_size = n
                for lineno, line in enumerate(new_pdb):
                    if not (lineno % _buffer_size):
                        f.write(''.join(_buffer))
                        _buffer = []
                    _buffer.append(line)
                f.write(''.join(_buffer))
            except IOError:
                pass

@click.command()
@click.option('--pdb', help='pdb file to run protocol at, for example 4G6K.pdb')
@click.option('--output', default="output", help='pdb file to run protocol at, for example 4G6K.pdb')
@click.option('--scheme', default = "c", help="numbering scheme")
@click.option('--fvonly', default = True, help="use only fv region")
@click.option('--rename', default = True, help="renaming")
@click.option('--splitscfv', default = True, help="splitscfv")
@click.option('--chain', default = "A", help="chain to extract active regions from")
def cli(pdb: str, output: str, scheme: str, fvonly: bool, rename: bool, splitscfv: bool, chain: str):
    output_path = Path(output).resolve()
    output_path.mkdir(exist_ok=True)
    pdb_name = Path(pdb).name
    # Format the antibody in order to fit the HADDOCK format requirements
    print(f"processing pdb {pdb}, results will be saved to {output_path}")
    annotated_pdb = (output_path / pdb_name.replace(".pdb", f"_{scheme}.pdb")).resolve()
    ImmunoPDB.main(inputstructure=pdb, outfile=annotated_pdb, scheme=scheme, fvonly=fvonly, rename=rename, splitscfv=splitscfv)
    print(f"pdb annotated as {annotated_pdb}")
    haddock_pdb = (output_path / pdb.replace(".pdb", f"_HADDOCK.pdb")).resolve()
    ab_haddock_format.main(pdb_file=str(annotated_pdb),
                           out_file=str(haddock_pdb),
                           chain_id=chain,
                           active_sites_file=str(output_path / pdb.replace(".pdb", f"_active_sites.txt")) #file to save active sites
                           )
    print(f"pdb ported to haddock ofrmat as {haddock_pdb}")
    tidy_pdb = (output_path / pdb_name.replace(".pdb", f"_HADDOCK_tidy.pdb")).resolve()
    tidy_up(haddock_pdb, tidy_pdb)


if __name__ == '__main__':
    cli()
