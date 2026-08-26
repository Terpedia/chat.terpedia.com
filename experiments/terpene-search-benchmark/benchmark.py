#!/usr/bin/env python3
"""Paired proxy benchmark for terpene-focused molecule selection.

The oracle is intentionally deterministic and hidden from both search methods.
It emulates a target-minus-antitarget objective using RDKit descriptors and
fingerprint motifs. It is not a protein model and makes no biological claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Descriptors, Lipinski, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.warning")

SEEDS = (
    "CC1=CCC(CC1)C(=C)C",          # limonene
    "CC1=CCC2CC1C2(C)C",           # alpha-pinene-like
    "CC(C)C1CCC(C)CC1O",           # menthol
    "CC1=CCC(CC1=O)C(=C)C",        # carvone
    "CC(C)=CCCC(C)=CCO",            # geraniol
    "CC(C)=CCCC(C)=CCCC(C)=CCO",    # farnesol
    "CC1(C2CCC1(C)C(=O)C2)C",      # camphor
    "CC(C)c1ccc(C)cc1O",            # thymol
    "CC(C)c1cc(C)ccc1O",            # carvacrol
    "CC(C)=CCCC(C)=CC=O",           # citral
)

# Small medicinal-chemistry-like moves. Products are sanitized and then pass
# through the same validity filter used by both algorithms.
REACTION_SMARTS = (
    "[O;H1:1]>>[O:1]C",
    "[O;H1:1]>>[O:1]CC",
    "[O;H1:1]>>[O:1]C(=O)C",
    "[C;H1,H2,H3:1]>>[C:1]F",
    "[C;H1,H2,H3:1]>>[C:1]O",
    "[C;H1,H2,H3:1]>>[C:1]C",
    "[C:1]=[C:2]>>[C:1]-[C:2]",
    "[C:1]=[O:2]>>[C:1]-[O:2]",
    "[C;H1,H2:1][O;H1:2]>>[C:1]=[O:2]",
)

FPGEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)


@dataclass(frozen=True)
class MoleculeRecord:
    smiles: str
    descriptors: tuple[float, ...]
    fp: object


@dataclass
class SearchResult:
    selected: list[int]
    scores: dict[int, float]
    evaluations: int
    elapsed_seconds: float

    @property
    def mean_score(self) -> float:
        return statistics.fmean(self.scores[i] for i in self.selected)


def canonical(mol: Chem.Mol) -> str | None:
    try:
        Chem.SanitizeMol(mol)
    except Exception:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def is_valid(mol: Chem.Mol) -> bool:
    heavy = mol.GetNumHeavyAtoms()
    return (
        8 <= heavy <= 38
        and Lipinski.NumRotatableBonds(mol) <= 10
        and Descriptors.MolWt(mol) <= 520
        and Lipinski.NumHDonors(mol) <= 5
        and Lipinski.NumHAcceptors(mol) <= 10
        and -1.5 <= Descriptors.MolLogP(mol) <= 7.0
    )


def describe(mol: Chem.Mol) -> tuple[float, ...]:
    return (
        mol.GetNumHeavyAtoms() / 30.0,
        Descriptors.MolWt(mol) / 450.0,
        (Descriptors.MolLogP(mol) + 2.0) / 9.0,
        Descriptors.TPSA(mol) / 140.0,
        Lipinski.NumRotatableBonds(mol) / 10.0,
        Lipinski.RingCount(mol) / 5.0,
        Lipinski.NumHAcceptors(mol) / 10.0,
        Lipinski.FractionCSP3(mol),
    )


def build_library(limit: int, seed: int = 20260813) -> tuple[list[MoleculeRecord], list[set[int]]]:
    rng = random.Random(seed)
    reactions = [AllChem.ReactionFromSmarts(s) for s in REACTION_SMARTS]
    smiles_to_index: dict[str, int] = {}
    molecules: list[Chem.Mol] = []
    adjacency: list[set[int]] = []

    def add(mol: Chem.Mol) -> tuple[int, bool] | None:
        smi = canonical(mol)
        if smi is None or not is_valid(mol):
            return None
        if smi in smiles_to_index:
            return smiles_to_index[smi], False
        idx = len(molecules)
        smiles_to_index[smi] = idx
        molecules.append(Chem.MolFromSmiles(smi))
        adjacency.append(set())
        return idx, True

    frontier: list[int] = []
    for smi in SEEDS:
        result = add(Chem.MolFromSmiles(smi))
        if result:
            frontier.append(result[0])

    attempts = 0
    max_attempts = limit * 300
    while len(molecules) < limit and attempts < max_attempts:
        attempts += 1
        parent_idx = rng.randrange(len(molecules))
        parent = molecules[parent_idx]
        reaction = rng.choice(reactions)
        try:
            products = list(reaction.RunReactants((parent,)))
        except Exception:
            continue
        if not products:
            continue
        rng.shuffle(products)
        for product_tuple in products[:6]:
            result = add(product_tuple[0])
            if result is None:
                continue
            child_idx, _ = result
            if child_idx != parent_idx:
                adjacency[parent_idx].add(child_idx)
                adjacency[child_idx].add(parent_idx)
            if len(molecules) >= limit:
                break

    if len(molecules) < max(300, limit // 2):
        raise RuntimeError(f"candidate generation stalled at {len(molecules)} molecules")

    records = [
        MoleculeRecord(Chem.MolToSmiles(m), describe(m), FPGEN.GetFingerprint(m))
        for m in molecules
    ]
    return records, adjacency


class ProxyTask:
    """A deterministic black-box landscape with target and two antitargets."""

    def __init__(self, task_id: int):
        rng = np.random.default_rng(8100 + task_id)
        self.target_center = rng.uniform(0.18, 0.82, 8)
        self.anti_centers = rng.uniform(0.12, 0.88, (2, 8))
        self.target_bits = set(rng.choice(1024, 18, replace=False).tolist())
        self.anti_bits = [set(rng.choice(1024, 18, replace=False).tolist()) for _ in range(2)]

    @staticmethod
    def _binding(desc: np.ndarray, bits: set[int], center: np.ndarray, motifs: set[int]) -> float:
        smooth = 7.5 * math.exp(-2.4 * float(np.mean((desc - center) ** 2)))
        motif = 0.20 * len(bits & motifs)
        return smooth + motif

    def score(self, record: MoleculeRecord) -> float:
        desc = np.asarray(record.descriptors)
        bits = set(record.fp.GetOnBits())
        target = self._binding(desc, bits, self.target_center, self.target_bits)
        anti = statistics.fmean(
            self._binding(desc, bits, center, motifs)
            for center, motifs in zip(self.anti_centers, self.anti_bits)
        )
        return target - 0.9 * anti


def diverse_top_k(
    indices: Iterable[int], scores: dict[int, float], library: Sequence[MoleculeRecord],
    k: int = 100, max_similarity: float = 0.82, relax: bool = False,
) -> list[int]:
    ranked = sorted(set(indices), key=lambda i: scores[i], reverse=True)
    selected: list[int] = []
    thresholds = (max_similarity, 0.88, 0.94, 1.01) if relax else (max_similarity,)
    for threshold in thresholds:
        for idx in ranked:
            if idx in selected:
                continue
            if all(DataStructs.TanimotoSimilarity(library[idx].fp, library[j].fp) <= threshold for j in selected):
                selected.append(idx)
                if len(selected) == k:
                    return selected
    raise RuntimeError(
        f"could select only {len(selected)} unique molecules at maximum similarity {max_similarity}"
    )


def naive_random_search(
    library: Sequence[MoleculeRecord], score: Callable[[MoleculeRecord], float],
    budget: int, seed: int, output_size: int = 100,
) -> SearchResult:
    started = time.perf_counter()
    rng = random.Random(seed)
    queried = rng.sample(range(len(library)), min(budget, len(library)))
    scores = {i: score(library[i]) for i in queried}
    selected = diverse_top_k(queried, scores, library, output_size)
    return SearchResult(selected, scores, len(queried), time.perf_counter() - started)


def evolutionary_search(
    library: Sequence[MoleculeRecord], adjacency: Sequence[set[int]],
    score: Callable[[MoleculeRecord], float], budget: int, seed: int,
    output_size: int = 100, initial_fraction: float = 0.25,
) -> SearchResult:
    started = time.perf_counter()
    rng = random.Random(seed)
    initial = max(output_size * 2, int(budget * initial_fraction))
    initial = min(initial, budget, len(library))
    evaluated = set(rng.sample(range(len(library)), initial))
    scores = {i: score(library[i]) for i in evaluated}

    batch_size = 64
    while len(evaluated) < min(budget, len(library)):
        # Fingerprint niches keep the parent pool from collapsing to one scaffold.
        ranked = sorted(evaluated, key=lambda i: scores[i], reverse=True)
        parents = diverse_top_k(ranked, scores, library, min(60, len(ranked)), 0.72, relax=True)
        candidates: set[int] = set()
        for parent in parents:
            candidates.update(adjacency[parent] - evaluated)
        remaining_slots = min(batch_size, budget - len(evaluated))
        if len(candidates) < remaining_slots:
            remaining = list(set(range(len(library))) - evaluated - candidates)
            candidates.update(rng.sample(remaining, min(remaining_slots - len(candidates), len(remaining))))

        # UCB-like acquisition: inherited neighborhood quality plus novelty.
        # Bulk fingerprint operations keep this cheap enough for a hard budget.
        parent_fps = [library[p].fp for p in parents[:12]]
        mean_score = statistics.fmean(scores.values())
        acquired: list[tuple[float, int]] = []
        for idx in candidates:
            neighbors = adjacency[idx] & evaluated
            inherited = max((scores[j] for j in neighbors), default=mean_score)
            similarities = DataStructs.BulkTanimotoSimilarity(library[idx].fp, parent_fps)
            novelty = 1.0 - max(similarities, default=0.0)
            acquired.append((inherited + 0.35 * novelty + rng.random() * 1e-9, idx))
        for _, idx in sorted(acquired, reverse=True)[:remaining_slots]:
            evaluated.add(idx)
            scores[idx] = score(library[idx])

    selected = diverse_top_k(evaluated, scores, library, output_size)
    return SearchResult(selected, scores, len(evaluated), time.perf_counter() - started)


def bootstrap_ci(values: Sequence[float], seed: int = 123, samples: int = 10000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(values)
    means = rng.choice(arr, size=(samples, len(arr)), replace=True).mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def run(args: argparse.Namespace) -> dict:
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    library, adjacency = build_library(args.library_size)
    rows: list[dict] = []

    for task_id in range(args.targets):
        task = ProxyTask(task_id)
        for repeat in range(args.repeats):
            paired_seed = args.seed + repeat
            naive = naive_random_search(library, task.score, args.evaluation_budget, paired_seed)
            evolved = evolutionary_search(library, adjacency, task.score, args.evaluation_budget, paired_seed)
            improvement = 100.0 * (evolved.mean_score - naive.mean_score) / max(abs(naive.mean_score), 1e-9)
            rows.append({
                "proxy_target": task_id + 1,
                "repeat": repeat + 1,
                "seed": paired_seed,
                "naive_mean_score": naive.mean_score,
                "evolution_mean_score": evolved.mean_score,
                "absolute_delta": evolved.mean_score - naive.mean_score,
                "relative_improvement_percent": improvement,
                "naive_evaluations": naive.evaluations,
                "evolution_evaluations": evolved.evaluations,
                "naive_seconds": naive.elapsed_seconds,
                "evolution_seconds": evolved.elapsed_seconds,
            })

    with (output / "runs.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    deltas = [r["absolute_delta"] for r in rows]
    relative = [r["relative_improvement_percent"] for r in rows]
    per_target = []
    for task_id in range(1, args.targets + 1):
        target_rows = [r for r in rows if r["proxy_target"] == task_id]
        per_target.append({
            "proxy_target": task_id,
            "naive_mean": statistics.fmean(r["naive_mean_score"] for r in target_rows),
            "evolution_mean": statistics.fmean(r["evolution_mean_score"] for r in target_rows),
            "relative_improvement_percent": statistics.fmean(r["relative_improvement_percent"] for r in target_rows),
            "wins": sum(r["absolute_delta"] > 0 for r in target_rows),
            "runs": len(target_rows),
        })

    ci_low, ci_high = bootstrap_ci(deltas)
    summary = {
        "disclaimer": "Synthetic RDKit proxy benchmark; not protein binding, docking, or private-harness evidence.",
        "library_size": len(library),
        "targets": args.targets,
        "paired_repeats": args.repeats,
        "evaluation_budget_per_method": min(args.evaluation_budget, len(library)),
        "output_molecules": 100,
        "mean_relative_improvement_percent": statistics.fmean(relative),
        "median_relative_improvement_percent": statistics.median(relative),
        "mean_absolute_delta": statistics.fmean(deltas),
        "absolute_delta_95_percent_bootstrap_ci": [ci_low, ci_high],
        "paired_run_wins": sum(d > 0 for d in deltas),
        "paired_runs": len(deltas),
        "target_summaries": per_target,
        "library_sha256": hashlib.sha256("\n".join(r.smiles for r in library).encode()).hexdigest(),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# Terpene search A/B report", "",
        "> Synthetic RDKit proxy benchmark; not protein binding, docking, or private-harness evidence.", "",
        f"Library: {len(library):,} valid unique terpene-derived molecules.",
        f"Budget: {summary['evaluation_budget_per_method']:,} scoring calls per method per run.",
        f"Output: 100 unique diversity-filtered molecules.", "",
        "| Proxy target | Naive mean | Evolution mean | Relative change | Paired wins |", "|---:|---:|---:|---:|---:|",
    ]
    for item in per_target:
        lines.append(
            f"| {item['proxy_target']} | {item['naive_mean']:.4f} | {item['evolution_mean']:.4f} | "
            f"{item['relative_improvement_percent']:+.2f}% | {item['wins']}/{item['runs']} |"
        )
    lines += [
        "", f"Overall mean relative change: **{summary['mean_relative_improvement_percent']:+.2f}%**.",
        f"Paired wins: **{summary['paired_run_wins']}/{summary['paired_runs']}**.",
        f"Mean absolute delta 95% bootstrap CI: **[{ci_low:.4f}, {ci_high:.4f}]**.", "",
        "The only experimental variable is the search policy. These results demonstrate the A/B implementation; "
        "the experiment must be rerun with the private protein-ligand scorer before making efficacy claims.",
    ]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-size", type=int, default=8000)
    parser.add_argument("--evaluation-budget", type=int, default=1600)
    parser.add_argument("--targets", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--output", default="results")
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(run(parse_args()), indent=2))
