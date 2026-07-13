Versionamento: era assente (solo 2 commit git, nessun tag). La versione ora vive nel package.json. Il workflow consigliato per rilasciare una nuova versione:


# 1. Aggiorna version in package.json (es. 1.1.0)
# 2. Committa e tagga git
git tag v0.2.0

# 3. Rebuilda l'immagine con il nuovo tag
docker compose build --no-cache
# oppure manualmente:
docker build -t bookshelf-tracker:0.2.0 .

# 4. Pusha l'immagine
docker tag bookshelf-tracker:0.2.0 ghcr.io/stefano664/bookshelf-tracker:0.2.0
docker push ghcr.io/stefano664/bookshelf-tracker:0.2.0

# 5. Pusha i TAGs
git push origin --tags