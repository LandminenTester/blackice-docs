---
name: LandminenTester documentation
description: A sleek cyberpunk resource library for BlackICE server developers.
colors:
  canvas: "#101214"
  rail: "#141719"
  surface: "#1a1e21"
  surface-hover: "#23292d"
  line: "#2c3337"
  ink: "#eef0eb"
  muted: "#a5afb2"
  quiet: "#929ea2"
  acid: "#dfff00"
  cyan: "#78d9df"
typography:
  display:
    fontFamily: '"Space Grotesk", sans-serif'
    fontSize: "clamp(34px, 4.2vw, 56px)"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-0.035em"
  headline:
    fontFamily: '"Space Grotesk", sans-serif'
    fontSize: "clamp(30px, 3vw, 43px)"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: '"Space Grotesk", sans-serif'
    fontSize: "25px"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  body:
    fontFamily: '"IBM Plex Sans", sans-serif'
    fontSize: "15.5px"
    lineHeight: 1.8
  label:
    fontFamily: '"IBM Plex Sans", sans-serif'
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "0.07em"
  code:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "12px"
    lineHeight: 1.9
rounded:
  code-inline: "3px"
  compact: "4px"
  item: "5px"
  control: "6px"
  code-block: "7px"
  dialog: "10px"
spacing:
  control-gap: "12px"
  article-gap: "20px"
  section-gap: "48px"
components:
  icon-button:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    width: "36px"
    height: "36px"
  icon-button-hover:
    backgroundColor: "{colors.surface-hover}"
    textColor: "{colors.acid}"
  search-trigger:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "8px 11px"
    width: "244px"
  search-dialog:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.ink}"
    rounded: "{rounded.dialog}"
    width: "min(660px, calc(100vw - 28px))"
  search-result:
    rounded: "{rounded.item}"
    padding: "15px 17px"
  search-result-hover:
    backgroundColor: "{colors.surface-hover}"
  navigation-link:
    textColor: "{colors.muted}"
    padding: "7px 12px"
  navigation-link-active:
    backgroundColor: "#20251c"
    textColor: "{colors.acid}"
---

# Design System: LandminenTester documentation

## Overview

**Creative North Star: "The BlackICE resource workspace"**

The shipped world is sleek cyberpunk: graphite surfaces, acid yellow wayfinding, cyan reading links, precise display type and calm long-form text. Its character comes from typography, thin divisions and the angular brand mark; the documentation stays readable and practical.

This system describes the custom MkDocs theme deployed on GitHub Pages. Source Markdown remains compatible with GitBook Git Sync; the theme does not style the GitBook account. The direction contract is recorded in `theme/main.html` (seed `a64120cb`).

**Key Characteristics:**

- Dark tonal layers with restrained accent color.
- Grouped resource navigation and spacious directory rows.
- Technical content with clear reading links, code and source attribution.

## Colors

### Primary

Acid yellow identifies the brand, selected navigation, location markers, focus outlines and selected text. It also highlights the library headline.

### Secondary

Cyan identifies article links and supports resource links on hover. Resource icons additionally distinguish the database with cyan and the API with a local lavender accent; these are identifiers rather than a second navigation palette.

### Neutral

Canvas is the page base; rail separates navigation and search; surface and surface-hover distinguish content and interactive states. Line provides thin dividers. Ink carries primary text, muted carries supporting text and quiet carries small metadata.

**The Wayfinding Rule.** Preserve acid for navigation and interaction emphasis, and cyan for reading links.

## Typography

Space Grotesk supplies headings and the brand; IBM Plex Sans supplies reading text and interface labels. Both are self-hosted variable fonts with OFL license files. Code uses the system monospace stack.

Frontmatter records the desktop library display, article headline, article section title, article body, navigation group label and block-code roles. The global body is (16px / 1.65); resource titles use (22px, weight 500), descriptions use (14px / 1.65). Group labels are uppercase. Avoid making long passages display type.

## Layout

The fixed header is (72px) high and the left rail is (252px) wide. Main content is centered inside a (1470px) maximum with desktop gutters of (56px). Article pages use a flexible reading column and a sticky (174px) article index, separated by (48px). The article measure is capped at (75ch) on desktop.

Resource directory entries are divider-separated rows: icon, flexible description and relationship/action area. Guide and reference links stay attached to their resource. The panel is independent; only `lt_database` and `lt-database-api` carry a paired relationship. Future resources must fit this model without implying a shared stack.

At (1250px), header shortcuts disappear and columns tighten. At (1080px), the rail narrows to (224px), the article index disappears, articles use the available width, and resource metadata moves below the description. At (820px), the header becomes (64px), navigation becomes a (270px) drawer, and content uses (25px) gutters. At (390px), gutters become (20px) and typography tightens. At (1600px) and above, content gutters and vertical spacing increase. Tables and code scroll within their own containers.

## Elevation & Depth

Tonal surfaces and thin borders supply ordinary depth. Resource rows do not lift. The search dialog is the exception: it uses a dark backdrop and a broad shadow (`0 22px 80px #0009`) to separate the modal from the workspace. No decorative glow is needed.

## Shapes

Controls have modest rounded corners; code, results and navigation use smaller radii. The dialog has the largest radius. The angular yellow brand mark and fine wireframe library motif provide the geometric character. Icons are outlined SVGs, usually (20px), with size adjusted to context.

## Components

### Navigation

Native `details` groups organize resource guides. Links use muted text, a tonal hover surface and an acid active label with a thin left marker. Active pages carry `aria-current="page"`. The article index uses the same acid location treatment and updates `aria-current="location"` while reading.

The mobile drawer makes closed navigation inert, focuses its first link on opening, cycles Tab through its controls, and closes with Escape or the scrim, returning focus to the menu button.

### Buttons and focus

Icon buttons are compact, outlined and transparent, with a tonal hover surface and acid icon. Search has a wider labeled trigger on desktop and an icon trigger on mobile. Links, buttons, inputs and summaries receive an acid (2px) `:focus-visible` outline offset by (5px). A keyboard-visible skip link reaches the main content. Disabled buttons use a waiting cursor and reduced opacity.

### Search

A native modal `dialog` contains the transparent search input, result links and keyboard hint. Ctrl/Cmd K or `/` opens it; Escape, the close button or a backdrop click closes it. Opening focuses the field; closing restores the trigger. Arrow Down enters results; Up/Down navigates results, with Up from the first returning to the field. Native modal behavior supplies the modal focus boundary.

Results use a Space Grotesk title, muted excerpt and cyan path. Loading, empty and failure messages occupy the same results region; failure offers retry. Result updates use a polite live region. Preserve these states when changing the appearance.

### Resource rows and articles

Resource rows expose identity, purpose, guide/reference links and an explicit relationship. Avoid wrapping these rows in additional cards. Articles use cyan underlined links, tonal inline and block code, horizontally scrollable tables, cyan-edged blockquotes and previous/next guide links. Code-copy controls show `Copied` after success; clipboard failure selects the code and shows `Select code` before returning to `Copy`.

### Motion

Motion is functional: group chevrons rotate over (0.16s ease-out); the mobile drawer translates over (0.2s cubic-bezier(0.16, 1, 0.3, 1)). Normal anchor scrolling is smooth. `prefers-reduced-motion: reduce` disables transitions and animations and makes scrolling immediate. Preserve the reduced-motion override.

## Do's and Don'ts

### Do:

- Do preserve the graphite, acid and cyan role separation.
- Do keep long-form reading in IBM Plex Sans with contained code and table overflow.
- Do preserve keyboard focus, modal behavior and reduced-motion states.
- Do extend resource navigation without implying dependency on the panel.

### Don't:

- Don't replace directory rows with nested decorative cards.
- Don't use the display font for long reading passages.
- Don't imply that the custom GitHub Pages theme changes GitBook styling.
