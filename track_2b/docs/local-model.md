# Running Apertus 1.5 8B locally (air-gapped setup)

- Weights: `Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF`, file `apertus-v1.5-8b-text-q4_k_m.gguf`
  (5,059,027,136 bytes, Q4_K_M), converted from `andreasmartin/apertus-v1.5-8b-text`, the
  text-only conversion of `swiss-ai/Apertus-v1.5-8B`. Licence: Apache-2.0 plus the Apertus 1.5
  Acceptable Use Policy.
- Server: `ghcr.io/ggml-org/llama.cpp:server@sha256:559ac229adefe0f7e2d4e32f5222f26927b6bb8ba44b9db08e2544afebf41984`
  (CPU build), flags `-c 8192 --jinja`.
- JSON mode (`response_format: json_object`) is accepted.

## Download once, then go offline

    mkdir -p models
    curl -L -o models/apertus-v1.5-8b-text-q4_k_m.gguf \
      https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF/resolve/main/apertus-v1.5-8b-text-q4_k_m.gguf
    docker pull ghcr.io/ggml-org/llama.cpp:server@sha256:559ac229adefe0f7e2d4e32f5222f26927b6bb8ba44b9db08e2544afebf41984
    make local

After these two downloads nothing leaves the machine: Schild and the model talk only over the
internal Docker network.

## Measured on the author's machine

Windows 11, Docker Desktop (WSL2), 12 CPU threads, 32 GB RAM, CPU only.

| Input | Prompt eval | Generation | Total |
|---|---|---|---|
| One German sentence with a name, address, diagnosis and religion (281 prompt tokens, 81 generated) | 9.3 tok/s | 2.7 tok/s | 60 s |

All four entities were found and no entity was invented. The 4 GB Quadro P1000 could not hold
enough layers to help (`unable to allocate CUDA0 buffer`), so the local setup is CPU-only. A
server with a 16 GB GPU, or the hosted CSCS endpoint, is the realistic production choice; the
point of this setup is that it works with no network at all.
