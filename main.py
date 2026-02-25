from __future__ import annotations

import argparse
import logging
from pathlib import Path

from cloud_wrapper import CloudWrapper
from config_manager import ConfigManager
from data_processor import DataProcessor
from discovery_wrapper import DiscoveryWrapper
from fuzz_wrapper import FuzzWrapper
from jaeles_wrapper import JaelesWrapper
from nuclei_wrapper import NucleiWrapper
from recon_wrapper import ReconWrapper
from reporter import Reporter
from tool_runner import ToolRunner


def load_targets(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.startswith("#")]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Godmode vulnerability and cloud scanner orchestrator")
    parser.add_argument("-l", "--list", dest="targets", required=True, help="Target domains file")
    parser.add_argument("-c", "--config", default="config.yaml", help="Config YAML path")
    parser.add_argument("--wordlist", default="/usr/share/wordlists/dirb/common.txt", help="FFUF wordlist")
    parser.add_argument("--profile", default="godmode", help="Scan profile name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("godmode")

    config = ConfigManager(Path(args.config)).load()
    output_dir = Path(config["output"]["directory"]).resolve()

    targets = load_targets(Path(args.targets))

    runner = ToolRunner(logger)
    recon = ReconWrapper(runner, config["scanners"]).run(targets, output_dir)
    discovery = DiscoveryWrapper(runner, config["scanners"]).run(recon, output_dir)

    active_hosts = discovery.get("active_hosts", [])
    nuclei = NucleiWrapper(runner, config["scanners"]["nuclei"]).run(active_hosts, output_dir)
    jaeles = JaelesWrapper(runner, config["scanners"]["jaeles"]).run(active_hosts, output_dir)
    cloud = CloudWrapper(runner, config["scanners"], config.get("cloud_options", {})).run(targets, output_dir)
    fuzz = FuzzWrapper(runner, config["scanners"]["ffuf"]).run(active_hosts, output_dir, args.wordlist)

    merged = DataProcessor.aggregate(recon, discovery, nuclei, jaeles, cloud, fuzz)
    normalized = DataProcessor.normalize(merged)

    report_path = Reporter(output_dir).write_json("final_report.json", normalized)
    logger.info("report written: %s", report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
