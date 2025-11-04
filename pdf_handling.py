import pdfplumber
from pathlib import Path
import json
from itertools import groupby
from PIL import ImageFont
import pandas as pd
import matplotlib.pyplot as plt


class PdfHandler:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.text = ""
        self.words = []
        self.lines = []
        self.grouped_data = {}  # key: label, value: {value, comment}

    # -------------------------------
    def import_pdf(self):
        """Extract text with coordinates and build structured groups."""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_words = page.extract_words(x_tolerance=2, y_tolerance=3)
                self.words.extend(page_words)

        # Group nearby words into text lines
        self.lines = self._group_words_by_line(self.words)

        # Try to group labels, values, and comments vertically
        self._group_vertical_relationships()

        # Save structured data
        self._save_outputs()

    # -------------------------------
    def _group_words_by_line(self, words, y_tolerance: int = 3):
        """Group words on the same horizontal line."""
        words = sorted(words, key=lambda w: w["top"])
        lines = []

        for _, group in groupby(words, key=lambda w: round(w["top"] / y_tolerance)):
            line_words = sorted(group, key=lambda w: w["x0"])
            text = " ".join(w["text"] for w in line_words)
            y_pos = line_words[0]["top"]
            lines.append({"text": text, "y": y_pos})
        return lines

    # -------------------------------
    def _group_vertical_relationships(self):
        """
        Identify 'label → value → comment' chains based on vertical order.
        Assumes values appear below labels, and comments below values.
        """
        sorted_lines = sorted(self.lines, key=lambda l: l["y"])
        for i, line in enumerate(sorted_lines[:-1]):
            label = line["text"].strip()
            next_line = sorted_lines[i + 1]["text"].strip() if i + 1 < len(sorted_lines) else None
            next_next = sorted_lines[i + 2]["text"].strip() if i + 2 < len(sorted_lines) else None

            # Basic heuristic: if next line looks like a value (digits, code, etc.)
            if next_line and (any(c.isdigit() for c in next_line) or "_" in next_line):
                self.grouped_data[label] = {
                    "value": next_line,
                    "comment": next_next if next_next and not any(c.isdigit() for c in next_next) else None,
                }

    # -------------------------------
    def _save_outputs(self):
        """Save extracted text, structured JSON, and raw lines to disk."""
        text_file = self.pdf_path.with_suffix(".txt")
        json_file = self.pdf_path.with_name(self.pdf_path.stem + "_structured.json")

        # Save all raw lines
        with open(text_file, "w", encoding="utf-8") as f:
            for line in self.lines:
                f.write(line["text"] + "\n")

        # Save structured data
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.grouped_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Text saved to: {text_file}")
        print(f"✅ Structured data saved to: {json_file}")


class PdfTextMap:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    def export_to_excel(self, y_tolerance=3):
        """Extract words with coordinates and export to Excel."""
        all_data = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                words = page.extract_words()
                for w in words:
                    all_data.append({
                        "Page": page_num,
                        "Text": w["text"],
                        "x0 (left)": round(w["x0"], 2),
                        "x1 (right)": round(w["x1"], 2),
                        "y_top": round(w["top"], 2),
                        "y_bottom": round(w["bottom"], 2),
                        "Width": round(w["x1"] - w["x0"], 2),
                        "Height": round(w["bottom"] - w["top"], 2)
                    })

        # Create DataFrame
        df = pd.DataFrame(all_data)

        # Sort by page, then by vertical (y) and horizontal (x)
        df.sort_values(by=["Page", "y_top", "x0 (left)"], inplace=True, ascending=[True, False, True])

        # Save to Excel file
        output_path = self.pdf_path.with_name(self.pdf_path.stem + "_coordinates.xlsx")
        df.to_excel(output_path, index=False)

        print(f"✅ Coordinate data exported to: {output_path}")
        print(f"📄 {len(df)} words extracted from {len(pdf.pages)} pages.")


class PdfVisualizer:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    def create_visual_overlay(self, page_number=0, grid_interval=100, resolution=150):
        """Creates an accurate overlay with coordinate grid and text boxes."""
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_number]
            image = page.to_image(resolution=resolution)
            draw = image.draw
            font = ImageFont.load_default()

            # Page metrics
            pdf_height = page.height
            pdf_width = page.width

            # Draw coordinate grid (corrected for flipped y-axis)
            for x in range(0, int(pdf_width), grid_interval):
                image.draw_vline(int(x), stroke="red", stroke_width=1)
                draw.text((int(x + 2), 5), str(int(x)), fill="red", font=font)

            for y in range(0, int(pdf_height), grid_interval):
                # flip y for image-space
                flipped_y = int(pdf_height - y)
                image.draw_hline(flipped_y, stroke="blue", stroke_width=1)
                draw.text((2, flipped_y - 10), str(int(y)), fill="blue", font=font)

            # Draw words with corrected y coordinates
            for word in page.extract_words():
                x0 = int(word["x0"])
                x1 = int(word["x1"])
                top = pdf_height - word["top"]      # flip
                bottom = pdf_height - word["bottom"]  # flip

                # Draw bounding box
                image.draw_rect((x0, bottom, x1, top), stroke="green", stroke_width=1)

                # Draw label
                label = f"{word['text']} ({x0},{int(word['top'])})"
                draw.text((x0, bottom - 8), label, fill="black", font=font)

            # Save
            output_path = self.pdf_path.with_name(
                f"{self.pdf_path.stem}_overlay_fixed_page{page_number+1}.png"
            )
            image.save(output_path)
            print(f"✅ Fixed overlay saved to: {output_path}")
            print(f"📏 Page size: {int(pdf_width)} × {int(pdf_height)} pts")


class PdfMultiRegionExtractor:
    """
    Define logical groups (e.g., "Output 1") that each contain one or more boxes.
    Each box is defined by coordinates (x0, x1, y0, y1) in PDF units (points).
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.groups = self.load_groups_from_json("inputs.json")

    # ---------------------------------------------------------
    def extract(self):
        results = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                words = page.extract_words()

                for group in self.groups:
                    box_texts = []  # will store one text string per box

                    for box in group["boxes"]:
                        if page_num != box["page"]:
                            continue

                        box_words = []
                        for w in words:
                            x0, x1 = w["x0"], w["x1"]
                            y0, y1 = w["bottom"], w["top"]

                            # check if the word is inside this box
                            if (box["x0"] <= x0 <= box["x1"] or box["x0"] <= x1 <= box["x1"]) and \
                                    (box["y0"] <= y0 <= box["y1"] or box["y0"] <= y1 <= box["y1"]):
                                box_words.append(w["text"])

                        # If this box had any matches, join them into one chunk
                        if box_words:
                            box_texts.append(" ".join(box_words))

                    # If any boxes in this group had matches, join them with commas
                    if box_texts:
                        results.append({
                            "Page": page_num,
                            "Group": group["name"],
                            "Boxes": len(group["boxes"]),
                            "Extracted Text": ", ".join(box_texts)  # 🔹 comma separates each box’s text
                        })

        df = pd.DataFrame(results)
        output_path = self.pdf_path.with_name(self.pdf_path.stem + "_grouped_regions.xlsx")
        df.to_excel(output_path, index=False)
        print(f"✅ Grouped extraction saved to: {output_path}")
        print(f"📄 {len(df)} grouped entries extracted from {len(pdf.pages)} pages.")

    def create_groups(self) -> list[dict]:
        groups = [
            {
                "name": "Output 1",
                "boxes": [
                    {"page": 2, "x0": 185, "x1": 212, "y0": 485, "y1": 512},
                    {"page": 2, "x0": 175, "x1": 226, "y0": 614, "y1": 690},
                ],
            },
            {
                "name": "Output 2",
                "boxes": [
                    {"page": 2, "x0": 242, "x1": 270, "y0": 485, "y1": 513},
                    {"page": 2, "x0": 233, "x1": 282, "y0": 608, "y1": 697}
                ],
            },
        ]
        return groups

    def load_groups_from_json(self, json_path: str):
        """Load groups from a JSON file formatted like your example."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert dict → list of dicts for PdfMultiRegionExtractor
        groups = [{"name": name, "boxes": info["boxes"]} for name, info in data.items()]

        print(f"✅ Loaded {len(groups)} groups from {json_path}")
        return groups


class PdfCoordinateViewer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def view_page(self, page_number=0, resolution=150):
        """Display the entire PDF page interactively with coordinate collection."""
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_number]
            pdf_width, pdf_height = page.width, page.height

            # Render the page to an image
            page_image = page.to_image(resolution=resolution).original

            fig_w = pdf_width / 72 * 1.5
            fig_h = pdf_height / 72 * 1.5
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))

            ax.imshow(page_image, extent=[0, pdf_width, pdf_height, 0])
            ax.set_xlim(0, pdf_width)
            ax.set_ylim(pdf_height, 0)
            ax.set_title(f"Page {page_number+1} — Click points, press Enter to print box coords")
            ax.set_xlabel("X (points)")
            ax.set_ylabel("Y (points)")

            coord_text = ax.text(
                0.02, 0.96, "", transform=ax.transAxes, color="yellow",
                fontsize=10, bbox=dict(facecolor="black", alpha=0.5, edgecolor="none")
            )

            clicked_points = []

            # --- Mouse move event ---
            def on_move(event):
                if event.inaxes == ax:
                    x, y = event.xdata, event.ydata
                    if 0 <= x <= pdf_width and 0 <= y <= pdf_height:
                        coord_text.set_text(f"x={x:.1f}, y={y:.1f}")
                        fig.canvas.draw_idle()

            # --- Mouse click event ---
            def on_click(event):
                if event.inaxes == ax:
                    x, y = event.xdata, event.ydata
                    clicked_points.append((x, y))
                    ax.plot(x, y, "ro", markersize=4)
                    print(f"Stored: x={x:.1f}, y={y:.1f}")
                    fig.canvas.draw_idle()

            # --- Key press event ---
            def on_key(event):
                if event.key == "enter" and clicked_points:
                    xs = [p[0] for p in clicked_points]
                    ys = [p[1] for p in clicked_points]
                    x_min, x_max = min(xs), max(xs)
                    y_min, y_max = min(ys), max(ys)
                    print(
                        f"✅ Box → x0={x_min:.1f}, x1={x_max:.1f}, y0={y_min:.1f}, y1={y_max:.1f}"
                    )

                    # Draw rectangle on the image
                    ax.plot(
                        [x_min, x_max, x_max, x_min, x_min],
                        [y_min, y_min, y_max, y_max, y_min],
                        color="cyan", linewidth=1.2
                    )
                    fig.canvas.draw_idle()

                    # Clear for next box
                    clicked_points.clear()
                    print("📦 Ready for next box...\n")

            fig.canvas.mpl_connect("motion_notify_event", on_move)
            fig.canvas.mpl_connect("button_press_event", on_click)
            fig.canvas.mpl_connect("key_press_event", on_key)

            plt.show()
