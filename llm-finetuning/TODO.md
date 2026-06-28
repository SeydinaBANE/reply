# TODO — llm-finetuning

## Dataset
- [x] Chargement JSONL (`load_jsonl`) + validation instruction/réponse
- [x] Template de prompt (`format_prompt`)
- [ ] Split train/val/test reproductible
- [ ] Masquage des tokens de prompt à l'entraînement

## Fine-tuning
- [x] Config hyperparamètres LoRA via YAML (`load_lora_config`)
- [x] Plan d'entraînement (`build_training_plan`)
- [ ] Implémenter le training LoRA/QLoRA réel (peft + transformers / bitsandbytes)
- [ ] Checkpointing + sauvegarde de l'adapter
- [ ] Lancement sur Vertex AI custom training job (GPU)

## Évaluation
- [x] Harness : exact match + normalized match (`evaluate_model`)
- [x] Adaptateur de génération Vertex (`VertexTextGenerator`, lazy)
- [x] Rapport JSON + markdown (`report.py`)
- [x] Gate baseline (`enforce_baseline`)
- [ ] Comparaison base vs fine-tuné sur un set figé
- [ ] LLM-as-judge en complément des métriques exactes

## CI
- [x] Jobs lint / typecheck / test
- [x] Entrée CLI `python -m finetune` pour l'eval-gate
- [ ] Bloquer la CI sur régression vs baseline historique (pas seuil fixe)

## Tests
- [x] dataset, prompt, evaluate (exact/normalized), baseline, report, runner
- [ ] Test d'intégration génération Vertex (mock SDK)
