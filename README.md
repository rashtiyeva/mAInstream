# mAInstream

mAInstream is a FastAPI application with a same-origin vanilla JavaScript
frontend for identifying songs and continuing lyrics.

## Run with Docker

```bash
git clone <repository-url>
cd mAInstream
cp .env.example .env
```

Add your OpenAI API key, Genius access token, and OpenAI model to `.env`, then
start the complete application:

```bash
docker compose up --build
```

Open <http://localhost:8000/app/>. The health endpoint is available at
<http://localhost:8000/>.

Stop and remove the container with:

```bash
docker compose down
```
