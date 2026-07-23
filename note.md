Versionamento: era assente (solo 2 commit git, nessun tag). La versione ora vive nel package.json. Il workflow consigliato per rilasciare una nuova versione:


# 1. Aggiorna version in package.json (es. 1.1.0)
# 2. Committa e tagga git
git tag v0.2.3

# 3. Rebuilda l'immagine con il nuovo tag
docker compose build --no-cache
# oppure manualmente:
docker build -t bookshelf-tracker:0.2.3 .

# 4. Pusha l'immagine
docker tag bookshelf-tracker:0.2.3 ghcr.io/stefano664/bookshelf-tracker:0.2.3
docker push ghcr.io/stefano664/bookshelf-tracker:0.2.3

# 5. Pusha i TAGs
git push origin --tags

# 6. Avvio locale del servizio
docker run --rm -p 5000:5000 bookshelf-tracker:0.2.3

docker run --rm -p 5000:5000 -v "$(pwd)/static/logo_quadev_small.png:/data/logo_quadev_small.png:ro" -e LOGO_PATH=/data/logo_quadev_small.png bookshelf-tracker:0.2.3
