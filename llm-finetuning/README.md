# llm-finetuning — fine-tuning + évaluation d'un LLM

Fine-tuning léger (LoRA/QLoRA) d'un LLM open-source, exécuté sur GCP Vertex AI, avec une
suite d'évaluation automatisée rejouée en CI à chaque version du modèle.

## Flux

```
dataset ──► fine-tune (LoRA, Vertex training job) ──► adapter
                                                          └──► eval harness ──► rapport
```

- `src/finetune/dataset.py` — chargement JSONL + validation des exemples instruction/réponse.
- `src/finetune/prompt.py` — template de prompt instruction → réponse.
- `src/finetune/train.py` — config LoRA/QLoRA + plan d'entraînement.
- `src/finetune/evaluate.py` — harness (exact match, normalized match) + gate baseline.
- `src/finetune/generator.py` — adaptateur Vertex AI (`TextGenerator`, import lazy).
- `src/finetune/report.py` — rapport d'évaluation (JSON + markdown).
- `src/finetune/runner.py` — orchestration évaluation → rapport → gate.
- `src/finetune/__main__.py` — entrée CLI (`python -m finetune --eval-data … --report …`).
- `vertex/job.py` — soumission du custom training job Vertex AI.

## Démarrage

```bash
make install
cp .env.example .env
make test
python -m finetune --eval-data data/eval.jsonl --report eval_report.json
```

Voir [`TODO.md`](TODO.md).
