# Scribe

`Scribe` est un petit outil Python qui transforme un fichier audio en compte rendu structuré.

## Fonctionnement

1. Vérifie la présence du fichier audio.
2. Transcrit l’audio via Groq.
3. Demande au LLM un résumé structuré.
4. Écrit un fichier Markdown dans `outputs/`.

## Configuration

Copie le fichier d’exemple et complète tes variables locales :

```bash
cp .env.example .env
```

Variables utiles :

- `GROQ_API_KEY` : clé API Groq.
- `SCRIBE_STT_MODEL` : modèle STT à utiliser.
- `SCRIBE_LLM_MODEL` : modèle LLM à utiliser.

## Utilisation

Exécution de la pipeline complète avec un fichier audio :

```bash
PYTHONPATH=src python3 -m scribe.cli chemin/vers/audio.wav --api-key "$GROQ_API_KEY"
```

Si tu veux forcer le dossier de sortie :

```bash
PYTHONPATH=src python3 -m scribe.cli chemin/vers/audio.wav --api-key "$GROQ_API_KEY" --out-dir outputs
```

Pour un essai sans appel réseau, tu peux aussi lancer les tests de la couche CLI et transcription qui mockent les accès externes.

## Tests

Lancer tous les tests unitaires :

```bash
python3 -m unittest discover -s src -p "test_*.py" -v
```

## Structure

- `src/scribe/transcription.py` : appel STT Groq.
- `src/scribe/summary_service.py` : parsing du JSON renvoyé par le LLM.
- `src/scribe/cli.py` : point d’entrée de la pipeline.

