# TODO — llm-finetuning

## Dataset
- [ ] Valider le schéma instruction/réponse (`validate_examples` esquissé)
- [ ] Split train/val/test reproductible
- [ ] Formatage prompt-template + masquage des tokens de prompt

## Fine-tuning
- [ ] Implémenter le training LoRA/QLoRA (peft + transformers / bitsandbytes)
- [ ] Config hyperparamètres (rank, alpha, dropout, lr) via YAML
- [ ] Checkpointing + sauvegarde de l'adapter
- [ ] Lancement sur Vertex AI custom training job (GPU)

## Évaluation
- [ ] Étendre le harness : exact match (fait), ROUGE/BLEU, LLM-as-judge
- [ ] Comparaison base vs fine-tuné sur un set figé
- [ ] Génération d'un rapport JSON + markdown

## CI
- [ ] Job CI qui rejoue l'éval et bloque si régression vs baseline
- [ ] Publication du rapport en artefact

## Tests
- [ ] `test_exact_match_score_perfect`
- [ ] `test_exact_match_score_partial`
- [ ] `test_validate_examples_rejects_empty`
