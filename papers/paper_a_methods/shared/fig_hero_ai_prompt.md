# fig_hero — AI-art version (prompt + integration)

The matplotlib `fig_hero` is the committed, citable default. An AI-rendered version can be tried for a
more polished schematic, but **a diffusion model will fabricate equations and mislabel axes** — treat
its output as decoration over a correct layout, never as the source of any symbol. Keep the matplotlib
version as the fallback that ships if the AI one is not clean.

## Recommended tools (in order)
1. **A diagram model that takes structured layout** (e.g. an LLM that emits SVG/TikZ you can compile) —
   best for correct labels. Ask for SVG with the three panels below; fix text by hand.
2. A general image model (Midjourney / DALL·E / SD) for a *background/texture* only, with all text and
   equations overlaid afterwards in matplotlib or Illustrator.

## Prompt (three-panel scientific schematic, flat vector, journal style)
> A clean three-panel scientific schematic for a physics/finance paper, flat vector style, muted
> palette (slate, soft red, green, indigo), thin connectors, generous whitespace, no photorealism, no
> 3D, no gratuitous glow. **Panel a "Particle market model":** ~9 small indigo dots in a latent-space
> box connected by a few light k-nearest-neighbour edges, an arrow labelled "learned Langevin force"
> into a rounded box "excess demand ED", then a downward arrow into a green rounded box "log-price".
> **Panel b "Controlled intervention":** a horizontal time axis; a red curve sitting at a flat steady
> state, dropping sharply at a dotted vertical line marked "scheduled shock t*", then relaxing back up;
> three small labelled readout chips below — "tail index", "order-flow memory", "price". **Panel c
> "Four results":** four stacked pale rounded cards reading "1 Measurement correction", "2 Driven
> transient", "3 Mechanism + order-flow signature", "4 Real-market boundary". Crisp sans-serif labels,
> publication-quality, white background.

Negative: photorealistic, 3D render, neon, busy background, watermark, fake math symbols, distorted text.

## Integration
- Export the chosen image to `shared/figures/fig_hero_ai.png` (keep `fig_hero.png` as the matplotlib
  fallback). **Verify every label and that no spurious equation/number appears.**
- To ship the AI version, point the three papers at it:
  `for d in ncs workshops/ml4ps workshops/genai_finance; do cp shared/figures/fig_hero_ai.png $d/figures/fig_hero.png; done`
  (overwrites the embedded name, so the markdown needs no edit).
- If it is not clean, do nothing — the matplotlib `fig_hero` already ships.
