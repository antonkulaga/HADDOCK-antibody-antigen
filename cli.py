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
@click.option('--output', default="output", help='folder to save output results to')
@click.option('--pdb', help='pdb file to run protocol at, for example 4G6K.pdb')
@click.option('--output', help='pdb file to run protocol at, for example 4G6K.pdb')
@click.option('--scheme', default = "c", help="numbering scheme")
@click.option('--fvonly', default = True, help="use only fv region")
@click.option('--rename', default = True, help="renaming")
@click.option('--splitscfv', default = True, help="splitscfv")
@click.option('--chain', default = "A", help="chain to extract active regions from")
def cli(pdb: str, output: str, scheme: str, fvonly: bool, rename: bool, splitscfv: bool, chain: str):
    dir: Path = Path(output)
    dir.mkdir(exist_ok=True)
    # Format the antibody in order to fit the HADDOCK format requirements
    ImmunoPDB.main(inputstructure=pdb, outfile=(dir / output.replace(".pdb", f"_{scheme}.pdb")).resolve(), scheme=scheme, fvonly=fvonly, rename=rename, splitscfv=splitscfv)
    output_path = (dir / output.replace(".pdb", f"_HADDOCK.pdb")).resolve()
    # and extract the HV loop residues and save them into a file
    ab_haddock_format.main(pdb_file = pdb, out_file=output_path, chain_id = chain)
    final_path = (dir / output.replace(".pdb", f"_HADDOCK.pdb")).resolve()
    tidy_up(output_path, final_path)

"""
```bash
python ImmunoPDB.py -i 4G6K.pdb -o 4G6K_ch.pdb --scheme c --fvonly --rename --splitscfv

# Format the antibody in order to fit the HADDOCK format requirements
# and extract the HV loop residues and save them into a file
python ab_haddock_format.py 4G6K_ch.pdb 4G6K-HADDOCK.pdb A > active.txt

# Add END and TER statements to the .pdb file
pdb_tidy 4G6K-HADDOCK.pdb > oo; mv oo 4G6K-HADDOCK.pdb
```
"""
if __name__ == '__main__':
    cli()
