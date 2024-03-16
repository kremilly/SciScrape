#!/usr/bin/python3

import pyfiglet, argparse

from rich.console import Console

from configs.settings import Settings

from engine.arxiv_build import ArxivBuild

console = Console()
parser = argparse.ArgumentParser(description = "Example of use: python sciscrape -s astronomy -max 5")

parser.add_argument("-s", "--search", help = "Search of article", required = True)
parser.add_argument("-max", "--max-results", help = "Maximum of results", default = Settings.get('results.default_max_results'))

args = parser.parse_args()

if __name__ == "__main__":
    console.print(f"[red]{pyfiglet.figlet_format('SciScrape')}[/red]")
    console.print("-" * 60) 

    console.print(
        ArxivBuild.get_json(
            args.search, args.max_results
        )
    )