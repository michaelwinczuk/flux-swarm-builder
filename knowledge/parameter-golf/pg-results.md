# Parameter Golf — Our Results

## Competition
OpenAI Parameter Golf: train the smallest possible language model (16MB) to lowest bits-per-byte in 10 minutes on 8xH100.

## Our Submissions

### PR #977 — Beat SOTA (1.1185 BPB)
- LeakyReLU(0.75) squared activation
- Parallel Muon optimizer
- Legal Score-First TTT
- GPTQ-lite int6 quantization
- MATRIX_LR=0.027, WARMDOWN_ITERS=3700
- 3-seed validation: 1.1183, 1.1194, 1.1179
- Beat prior SOTA of 1.1194 by finding optimal negative slope via systematic sweep

### PR #1031 — MTP Funnel (Submitted, Awaiting Eval)
- Added MTP_NUM_HEADS=2, MTP_LOSS_WEIGHT=0.1
- Multi-Token Prediction as auxiliary training signal
- Forces backbone to learn richer representations
- MTP heads discarded at export (zero 16MB impact)
- Validated -0.0037 BPB improvement on test pod
- Projected ~1.1148 on fast hardware

## Research Chain
- 8 TTS swarm missions investigating activation functions, distillation, quantization
- Cross-validated with Grok and Gemini for external perspectives
- Confirmed dead ends: per-layer learnable alpha (identical BPB), fused Triton kernels (torch.compile already optimizes them)
- Key discovery: MTP is a "training funnel" — focuses gradient signal on structurally important tokens

## Methodology
Used our own multi-agent swarm (TTS) to research the competition. The swarm identified MTP as highest-ROI unexplored lever through 8 sequential missions with increasingly focused questions. This is the swarm optimizing itself.
