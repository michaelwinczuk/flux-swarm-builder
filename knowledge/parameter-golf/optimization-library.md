# Parameter Golf — Optimization Knowledge Library

## Activation Functions
- LeakyReLU(0.75) squared: current winner (our submission)
- LeakyReLU(0.5) squared: prior SOTA
- StarReLU: reportedly fastest at 65-75ms/step
- Per-layer learnable alpha: DEAD END (identical BPB, breaks torch.compile)
- SwiGLU: recurring winner in various configs

## Quantization
- GPTQ-lite int6: per-row optimal clip search with 5 percentile candidates
- Int8 per row for embeddings
- FP32 for biases, LayerNorm, control tensors
- FP16 embedding passthrough: +508KB (blows 16MB budget by 239KB)
- Bucket collapse: KD weight updates get rounded into same quantization bucket

## Training Tricks
- MTP (Multi-Token Prediction): auxiliary heads predict 2-3 tokens ahead, discarded at export
- Legal Score-First TTT: test-time training on evaluation tokens
- EMA weight averaging: smooths training noise
- SWA (Stochastic Weight Averaging): alternative to EMA
- Warmdown scheduling: LR decay in final training phase

## Systems Optimization
- torch.compile: any dynamic value in forward path breaks fusion
- Pod speed lottery: same image gives 82ms-103ms depending on hardware allocation
- Kill threshold: if step_avg > 84ms at step 2000, kill the run
- Speed-gate strategy: spin 3-4 pods, benchmark, keep fastest

## Distillation (Unexplored)
- Born-Again Networks: never tried as true BAN in PG
- Top-K logit distillation (k=8): zero mentions in PG or NanoGPT
- Chain distillation: working in NanoGPT Slowrun (7x to 8.9x efficiency)
