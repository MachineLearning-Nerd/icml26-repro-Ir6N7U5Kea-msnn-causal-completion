# Reproduction and release command ledger

No credential values or generated backend wrappers are included. Repeated
polling and log-range calls are represented by their exact command forms.

## Startup and source audit

```sh
orx skill
orx skill orx-experiment-tree
orx skill orx-evidence
orx skill orx-git
orx skill orx-compute
orx projects --json
orx projects
orx runs d1ae39fc-fa81-4ea5-908d-2ec812552bca
git branch -a
git status --short
git rev-parse HEAD
df -h .
env | cut -d= -f1 | sort
orx paper 2603.11942 --full
curl -L -A 'OpenResearch-Reproduction/1.0' https://ar5iv.labs.arxiv.org/html/2603.11942
shasum -a 256 paper.html
```

The live verdict dataset was fetched through its evaluator endpoint and
filtered by the exact key `space_id == "DineshAI/Ir6N7U5Kea"`. The exact judged
Space was downloaded with:

```sh
hf download DineshAI/Ir6N7U5Kea --repo-type space --revision 6501ddc2ca77931a80822435fa93670c03c7d2dc --local-dir <fresh-directory>
```

## Environment and fixed command

```sh
uv lock
uv sync --frozen
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Every formal node inherited the last command unchanged.

## Experiment orchestration

Nodes were created with the following exact form:

```sh
orx create-experiment d1ae39fc-fa81-4ea5-908d-2ec812552bca --title "<claim round>" --parent <parent-experiment-id>
```

Every formal run used:

```sh
orx exp run <experiment-id> --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248
orx exp wait <experiment-id> --timeout 480
orx runs d1ae39fc-fa81-4ea5-908d-2ec812552bca
orx logs <run-id>
orx exp desc <experiment-id> --set "<frozen finding>"
```

Two incomplete Claim 5 routes were canceled:

```sh
orx exp cancel 9476441e-8160-47ec-b9fa-142556f5db46
orx exp cancel 587019d8-0e28-477b-8583-3750e66f6a14
```

## Accepted formal runs

| Claim | Run | Git SHA | Wall time |
|---|---|---|---:|
| 1 | `4498c980-5971-49b7-a9d9-dfd452ff2241` | `b01cf6ff3166e5e0ed72f876614e1a4d3f5cb3dc` | 758 s |
| 2 | `6411f20e-e068-4a91-a309-6fa6c59e3d6a` | `8e4d33cb954fa5f647008e7c9a4db81a68d32731` | 271 s |
| 3 | `92a2a72f-4845-4b14-b85a-f86549a0cded` | `15488a94a06ac8a58213224b49014b1901efc7f3` | 223 s |
| 4 | `3d5c38e8-0f54-4614-a1c8-22f25df79b42` | `b88906567b8c0fa21c1f2b39fe5cc722adbef956` | 948 s |
| 6 | `404fdc54-2c67-47e7-85ea-ddf4f21bcd5a` | `b9bfbd9c7b51d91999a7ecd52a850acd98b68629` | 228 s |
| 5 and cumulative freeze | `5f17a7bf-5a73-428c-8f3d-54cf844cd48d` | `b99cefc0f99bf42b8397594b2e2de49d4c209014` | 688 s |

## Presentation and release checks

```sh
uvx marimo check notebooks/msnn_reproduction.py
xmllint --noout reports/reproduction-campaign/images/*.svg
sips -s format png <figure.svg> --out <temporary-render.png>
jq empty logbook.json
jq empty .openresearch/artifacts/claim_*/claim_contract.json
jq empty .openresearch/artifacts/claim_*/raw_result.json
git diff --check
shasum -a 256 <allowlisted-file>
git ls-remote origin refs/heads/master
```

The final text-only Space commit and post-publication `hf download` commands
are appended to the release report by their resulting immutable revision
after publication.
