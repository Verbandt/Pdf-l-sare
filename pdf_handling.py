import pdfplumber
from pathlib import Path
import json
from PIL import ImageFont
import pandas as pd
import matplotlib.pyplot as plt
import re


class PdfHandler:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extractor = PdfMultiRegionExtractor(pdf_path)
        self.df = None

    def extract_information_from_pdf(self):
        self.df = self.extractor.extract_groups()

    def export_data_to_excel(self):
        self.df.to_excel("groups.xlsx", index=False)


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
                top = pdf_height - word["top"]  # flip
                bottom = pdf_height - word["bottom"]  # flip

                # Draw bounding box
                image.draw_rect((x0, bottom, x1, top), stroke="green", stroke_width=1)

                # Draw label
                label = f"{word['text']} ({x0},{int(word['top'])})"
                draw.text((x0, bottom - 8), label, fill="black", font=font)

            # Save
            output_path = self.pdf_path.with_name(
                f"{self.pdf_path.stem}_overlay_fixed_page{page_number + 1}.png"
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
        self.input_node_range, self.output_node_range = self.load_settings_from_json("settings.json")
        self.df = None
        self.pages = None

        self.extract_pages()

    # ---------------------------------------------------------
    def extract_groups(self) -> pd.DataFrame:
        results = []

        for page_num, page in enumerate(self.pages, start=1):
            words = page.extract_words()
            for group in self.groups:
                box_texts = []  # will store one text string per box
                for box in group["boxes"]:
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
                        "Group": group["name"],
                        "Boxes": len(group["boxes"]),
                        "Extracted Text": ", ".join(box_texts)  # 🔹 comma separates each box’s text
                    })

        df = pd.DataFrame(results)
        return df

    def extract_pages(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            self.pages = {page_num: page for page_num, page in enumerate(pdf.pages, start=1)}

    def load_groups_from_json(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert dict → list of dicts for PdfMultiRegionExtractor
        groups = [{"name": name, "boxes": info["boxes"]} for name, info in data.items()]

        return groups

    def load_settings_from_json(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        def parse_range(s: str) -> range:
            start, end = map(int, s.split("-"))
            return range(start, end + 1)

        input_range = parse_range(settings["input_nodes"]["nodes"])
        output_range = parse_range(settings["output_nodes"]["nodes"])

        return input_range, output_range

    def assign_pages_per_node(self):
        page_roles = {}

        for page_num, page in self.pages.items():
            text = page.extract_text() or ""
            match = re.search(r"Nod:(\d+)", text)

            if not match:
                page_roles[page_num] = "Unknown"
                continue

            nod_value = int(match.group(1))

            if nod_value in self.input_node_range:
                page_roles[page_num] = "Input"
            elif nod_value in self.output_node_range:
                page_roles[page_num] = "Output"
            else:
                page_roles[page_num] = f"Other (Nod:{nod_value})"

        return page_roles


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
            ax.set_title(f"Page {page_number + 1} — Click points, press Enter to print box coords")
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
