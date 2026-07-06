# Pull Request — `feature/summary` → `dev`

## Résumé

Cette branche ajoute la pipeline `Scribe` en plusieurs briques testées : configuration, transcription, résumé structuré et CLI.

## Contenu principal

- `src/scribe/config.py` : chargement des variables d’environnement.
- `src/scribe/transcription.py` : appel Groq STT et parsing de réponse.
- `src/scribe/summary_service.py` : transformation de la réponse LLM en structure exploitable.
- `src/scribe/cli.py` : orchestration de la pipeline et génération Markdown.
- Tests unitaires associés sous `src/scribe/test_*.py`.

## Commits récents

- `62f8b15` — `feat: add transcription module and tests`
- `3d21405` — `chore: add .env.example (configuration template)`
- `40a9cd5` — `chore: add config loader (.env) and example; tests`
- `625242a` — `feat: add CLI pipeline (run_scribe) and tests`
- `10aba7c` — `feat: parse LLM JSON output into structured summary (service)`
- `110b51e` — `feat:Groq chat client/tests`
- `aa77f79` — `feat: add summary prompt and markdown helpers`
- `ec52149` — `feat: bootstrap Scribe project with skeleton structure`

## Vérification

Commandes testées localement :

```bash
python3 -m unittest discover -s src -p "test_*.py" -v
```

## Points à relire

- Vérifier les variables `.env` avant exécution réelle.
- Vérifier que le dossier `outputs/` reste ignoré.
- Vérifier le message de commit final avant ouverture de PR.

## Checklist review

- [ ] La configuration ne contient aucun secret.
- [ ] Les tests passent localement.
- [ ] Le flux CLI écrit bien un Markdown dans `outputs/`.
- [ ] La transcription et le résumé sont séparés en briques simples.
