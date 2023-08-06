"""exfill will scrape LinkedIn job postings, parse out details about
each posting, then combine all of the information into a single useable
csv file.
"""
import logging
from argparse import ArgumentParser
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path, PurePath

from parsers.parser_factory import ParserFactory
from scrapers.scraper_factory import ScraperFactory


class ConfigFileMissing(Exception):
    pass


def init_parser() -> dict:
    """Initialize argument parser."""
    parser = ArgumentParser()
    parser.add_argument("site", choices=["linkedin"], help="Site to scrape")
    parser.add_argument(
        "action", choices=["scrape", "parse"], help="Action to perform"
    )
    return vars(parser.parse_args())


def load_config() -> ConfigParser:
    """Load config file"""

    config_file = PurePath(__file__).parent / "config.ini"
    if not Path(config_file).exists():
        raise ConfigFileMissing("Default config.ini is missing")

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_file)

    return config


def create_dirs(config: ConfigParser) -> None:
    """Create directories referenced in the config file"""
    for dir_path in config.items("Directories"):
        Path.mkdir(Path.cwd() / dir_path[1], exist_ok=True)


def main() -> None:
    """Main controller function used to call child functions/modules."""
    # Load config
    config = load_config()

    create_dirs(config)

    # Initialize logging
    logging.basicConfig(
        filename=config.get("Paths", "app_log"),
        level=logging.INFO,  # level=logging.INFO should be default
        format="[%(asctime)s] [%(levelname)s] - %(message)s",
        filemode="w+",
    )

    args = init_parser()
    logging.info(f"Starting app with the following input args: {args}")

    if args.get("action") == "scrape":
        scraper = ScraperFactory.create("linkedin", config)
        scraper.scrape_postings(200)

    if args.get("action") == "parse":
        parser = ParserFactory.create("linkedin", config)
        parser.parse_postings()

    logging.info("Finished execution.  Exiting application.")


if __name__ == "__main__":

    main()
