# Branding — the default look, and making it look like yours

## The default: Vapi's brand

The brand tokens are inline, so nothing external is needed to be on-brand. A
page started from the example is branded already. Use these and nothing else
when you write new markup:

    --bg: #FEFEFE;   --bg-dark: #111013;
    --text: #111013; --text-inverse: #FEFEFE;
    --text-muted: rgba(17,16,19,0.6);   --line: rgba(17,16,19,0.1);
    --mint: #00CD8F; --mint-tint-5: rgba(0,205,143,0.05);
                     --mint-tint-20: rgba(0,205,143,0.2);
    --ocean: #2D6BFF; --sunset: #EF8E44;

Type is Avantt for headings and body, Foundry Gridnik uppercase and letterspaced
for eyebrows, labels, and data values, with `"Plus Jakarta Sans"` and
`"Tomorrow"` as the web fallbacks already written into every font stack in the
example. White is the canvas, black is for intentional dark contrast, and mint
is an accent that is never a large fill. Both right-panel templates
(`report-panel.html`, `squad-panel.html`) are written against exactly these
variables, so they inherit the brand with no edits.

## Making it look like yours

Only when the user asks for their own brand. Keep the layout and change three
things in `public/index.html`:

- **Logo and favicon:** the header `<img>` and the `<link rel="icon">` are
  inline SVG data URIs. Replace both with the user's logo, inline or as a file
  in `public/`.
- **Colors:** change the VALUES in the `:root` block and keep the variable
  names, because every panel reads them. `--mint` is the accent, so it is the
  one that carries their brand.
- **Fonts:** edit the three `@font-face` blocks, put the files in
  `public/fonts/`, and replace `Avantt` and `Foundry Gridnik` everywhere they
  appear in a `font-family` stack, including the `--grid` variable.

Screenshot the idle and mid-call states afterwards. A light logo on the white
header, or an accent too pale to read as text, only shows up on screen.
