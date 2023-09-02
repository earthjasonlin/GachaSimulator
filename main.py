import json
import random
import csv
from tqdm import tqdm
import argparse
import os

class ProbabilityTable:
    def __init__(self, table):
        self.table = table
        self.maximum_draws = table[-1][0]

    def get_probability(self, n):
        for i in range(len(self.table) - 1):
            if n < self.table[i + 1][0]:
                return self.table[i][1] + (self.table[i + 1][1] - self.table[i][1]) * (
                    n - self.table[i][0]
                ) / (self.table[i + 1][0] - self.table[i][0])
        return self.table[-1][1]


class CardGame:
    def __init__(self, probability_table):
        self.probability_table = probability_table

    def play(self):
        n = 1
        while True:
            if n > self.probability_table.maximum_draws:
                raise ValueError(
                    "Reached maximum number of draws without finding a match"
                )
            r = random.random()
            p = self.probability_table.get_probability(n)
            if r < p:
                return n
            n += 1


class Statistics:
    def __init__(self, game, num_trials):
        self.game = game
        self.num_trials = num_trials

    def run(self):
        results = {}
        maximum_draws = self.game.probability_table.maximum_draws
        for n in range(1, maximum_draws + 1):
            results[n] = {"count": 0, "samples": []}

        with tqdm(total=self.num_trials, desc="Running simulations") as pbar:
            for i in range(self.num_trials):
                n = self.game.play()
                results[n]["count"] += 1
                results[n]["samples"].append(i + 1)
                pbar.update()

        with open(results_full_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["抽数", "该抽出金的概率", "刚好在该抽出金的概率", "该抽出金的样本数量", "该抽出金的样本号"])
            for n in range(1, maximum_draws + 1):
                p = self.game.probability_table.get_probability(n)
                probability_of_exact_n = results[n]["count"] / self.num_trials
                samples_str = ", ".join(str(s) for s in results[n]["samples"])
                writer.writerow(
                    [n, p, probability_of_exact_n, results[n]["count"], samples_str]
                )

        with open(results_no_samples_filename, "w", newline="") as f_no_samples:
            writer_no_samples = csv.writer(f_no_samples)
            writer_no_samples.writerow(["抽数", "该抽出金的概率", "刚好在该抽出金的概率", "该抽出金的样本数量"])
            for n in range(1, maximum_draws + 1):
                p = self.game.probability_table.get_probability(n)
                probability_of_exact_n = results[n]["count"] / self.num_trials
                writer_no_samples.writerow(
                    [n, p, probability_of_exact_n, results[n]["count"]]
                )


parser = argparse.ArgumentParser(description="Take user defined parameters.")
parser.add_argument("--config", "-c", type=str, required=True, help="Path to your config.json file")
args = parser.parse_args()

with open(args.config, "r") as f:
    config = json.load(f)

table = ProbabilityTable(config["probability_table"])
game = CardGame(table)
statistics = Statistics(game, config["num_trials"])

config_name, _ = os.path.splitext(args.config)

results_full_filename = f"results_{config_name}_full.csv"
results_no_samples_filename = f"results_{config_name}_no_samples.csv"

statistics.run()