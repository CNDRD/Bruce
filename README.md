<div align="center">

# Bruce  

<a href="https://diskito.eu/discord">
    <img src="https://img.shields.io/discord/402356550133350411?label=discord&style=for-the-badge&logo=discord&color=5865F2&logoColor=white" />
</a>
<img src="https://img.shields.io/static/v1?style=for-the-badge&message=Supabase&color=3ECF8E&logo=Supabase&logoColor=3ECF8E&label=Powered%20By" />
<br />
<img src="https://img.shields.io/badge/python-3.10-blue.svg?logo=python&style=for-the-badge&logoColor=white&color=yellow" />
<img src="https://img.shields.io/github/repo-size/CNDRD/bruce?style=for-the-badge&logoColor=white&color=yellow" />
<img src="https://img.shields.io/github/license/CNDRD/bruce?style=for-the-badge&logoColor=white&color=yellow" />

---  

I'm willing to help answer any questions that you may have  
You can either join my [Discord](https://diskito.eu/discord) or send me a DM on Discord at __cndrd__  
You can also visit the website I've made for my server [Here](https://diskito.eu)

---  

<img src="https://forthebadge.com/images/badges/built-by-crips.svg" />
<img src="https://forthebadge.com/images/badges/fuck-it-ship-it.svg" />

</div>

## Run With Docker

Build and run locally:

```bash
docker build -t bruce-bot .
docker run --rm \
    -e TOKEN=your_discord_bot_token \
    -e SUPABASE_URL=your_supabase_url \
    -e SUPABASE_KEY=your_supabase_key \
    bruce-bot
```

## Deploy In Dokploy

1. Create a new Application in Dokploy.
2. Choose your Git repository and branch.
3. Build Type: Dockerfile.
4. Dockerfile path: `Dockerfile`.
5. Start command: leave empty (the Dockerfile already uses `python bot.py`).
6. Add these environment variables in Dokploy:
     - `TOKEN`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
7. Deploy.

Notes:
- This bot does not expose an HTTP port, so no port mapping is required.
- Keep secrets only in Dokploy environment variables, not in `.env` in Git.
- `.env.example` documents the required variable names.

### Dokploy With Compose

If your Dokploy project expects a compose file, use `docker-compose.yml` from this repo.

1. Build Type: Docker Compose.
2. Compose file path: `docker-compose.yml`.
3. Add environment variables in Dokploy:
    - `TOKEN`
    - `SUPABASE_URL`
    - `SUPABASE_KEY`
