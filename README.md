# chat.terpedia.com

The live Terpedia chat frontend is a static GitHub Pages site served from
[`docs/`](docs/). It calls the separate Terpedia backend at
`https://api.terpedia.com`.

## Contents

- [`docs/index.html`](docs/index.html) - chat application
- [`docs/pubmed/`](docs/pubmed/) - PubMed research reader
- [`docs/clinicaltrials/`](docs/clinicaltrials/) - ClinicalTrials.gov reader
- [`GITHUB_PAGES.md`](GITHUB_PAGES.md) - Pages and custom-domain configuration

Backend orchestration, agents, RAG, chemistry tools, and deployment live in
the private [`Terpedia/chat-terpedia-backend`](https://github.com/Terpedia/chat-terpedia-backend)
repository.
