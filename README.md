# GhostPoster

<p align="center">
  <img src="docs/logo.png" width="320">
</p>

<h1 align="center">GhostPoster</h1>

<p align="center">
<b>Open-Source PDF Tiling & Poster Printing Tool</b><br>
Split large PDF drawings into printable A-series, Letter, ANSI and ARCH pages while preserving an exact 100% scale.
</p>

------------------------------------------------------------------------

# Why GhostPoster?

Most poster printing tools simply split pages.

**GhostPoster** is designed for technical drawings where **100% scale
matters**.

It automatically:

-   detects useful drawing area
-   removes unnecessary white margins
-   optimizes page orientation
-   skips blank sheets
-   adds registration marks
-   produces print-ready tiled PDFs

------------------------------------------------------------------------

# Highlights

- 🎯 **Exact 100% Scale** – no unwanted scaling.
- ✂ **Smart Auto Crop** – removes unnecessary white margins.
- 📄 **Automatic Orientation** – minimizes the number of pages.
- 🗑 **Skip Blank Pages** – saves paper and ink.
- ✚ **Registration Marks & Cut Lines** – easier page assembly.
- 📐 **Built-in Calibration Tools** – verify print accuracy in seconds.
- 🏭 **Print Shop Mode** – PDFs ready for commercial printing.
- 🖥 **GUI & CLI** – suitable for both casual users and automation.
- 🌍 **Open Source (MIT)** – free forever.

------------------------------------------------------------------------

# Workflow

``` text
Input PDF
    │
    ▼
Smart Auto Crop
    │
    ▼
Orientation Optimizer
    │
    ▼
Blank Page Detection
    │
    ▼
Tile Generator
    │
    ▼
GhostPoster PDF
```

------------------------------------------------------------------------

# Typical Applications

-   ✈ RC aircraft plans
-   📐 CAD drawings
-   📘 Engineering documentation
-   🪚 Woodworking templates
-   ⚙ CNC templates
-   🏗 Architectural drawings
-   🖼 Posters
-   🔨 DIY projects

------------------------------------------------------------------------

# Installation

## Linux AppImage

``` bash
chmod +x GhostPoster-x86_64.AppImage
./GhostPoster-x86_64.AppImage
```

## Build from source

``` bash
git clone https://github.com/nftomczain/GhostPoster.git
cd GhostPoster
pip install -e ".[gui]"
```

------------------------------------------------------------------------

# Quick Start

``` bash
ghostposter plan.pdf \
    --paper A3 \
    --auto-crop \
    --maximize \
    --skip-blank \
    --marks \
    --cutlines \
    --labels \
    --output plan_A3.pdf
```

------------------------------------------------------------------------

# Graphical Interface

Features:

-   Live Preview
-   Drag & Drop
-   Export progress
-   Keyboard shortcuts
-   Accessibility support

------------------------------------------------------------------------

# Command Line

``` bash
ghostposter drawing.pdf --paper A4
```

------------------------------------------------------------------------

# Print Shop Mode

Adds:

-   print instruction sheet
-   DO NOT SCALE stamp
-   PDF metadata

Designed for commercial printing services.

------------------------------------------------------------------------

# Debug Mode

Run:

``` bash
GHOSTPOSTER_DEBUG=1 ./GhostPoster-x86_64.AppImage
```

GhostPoster creates:

``` text
ghostposter_debug.txt
```

The log contains:

-   GhostPoster version
-   Python version
-   PyMuPDF / MuPDF versions
-   platform information
-   PDF geometry
-   export diagnostics

This information is useful when reporting bugs.

------------------------------------------------------------------------

# FAQ

## Does GhostPoster preserve scale?

Yes.

The original drawing scale is preserved.

## Does GhostPoster modify the original PDF?

No.

A new PDF is always created.

## Does GhostPoster require Internet?

No.

Everything runs locally.

## Can it print RC aircraft plans?

Yes.

GhostPoster was originally created for full-size RC aircraft plans.

------------------------------------------------------------------------

# Roadmap

## v1.0.x

-   Stable GUI
-   Stable CLI
-   Auto Crop
-   Auto Orientation
-   Skip Blank Pages
-   Print Shop Mode

## v1.1

-   Smooth zoom
-   Mouse panning
-   Export selected pages

## v1.2

-   User paper sizes
-   Printer profiles
-   Custom crop margins

## v1.3

-   SVG export
-   DXF export

------------------------------------------------------------------------

# Contributing

Bug reports and pull requests are welcome.

Please include:

-   GhostPoster version
-   operating system
-   sample PDF
-   ghostposter_debug.txt (if available)

------------------------------------------------------------------------

# License

MIT License.

------------------------------------------------------------------------

<p align="center">

Made with ❤️ in Poland

for the RC, Maker and Open Source communities.

</p>
