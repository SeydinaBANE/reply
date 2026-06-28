# llm-finetuning — fine-tuning + évaluation d'un LLM

Fine-tuning léger (LoRA/QLoRA) d'un LLM open-source, exécuté sur GCP Vertex AI, avec une
suite d'évaluation automatisée rejouée en CI à chaque version du modèle.

## Flux

```
dataset ──► fine-tune (LoRA, Vertex training job) ──► adapter
                                                          └──► eval harness ──► rapport
```

- `src/finetune/dataset.py` — chargement/validation du dataset d'instruction.
- `src/finetune/train.py` — config LoRA/QLoRA + lancement du job.
- `src/finetune/evaluate.py` — harness d'évaluation (exact match, score agrégé).
- `vertex/job.py` — soumission du custom training job Vertex AI.

## Démarrage

```bash
make install
cp .env.example .env
make test
python -m finetune.train --config configs/lora.yaml
```

Voir [`TODO.md`](TODO.md).
