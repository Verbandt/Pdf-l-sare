import pdfplumber
from pathlib import Path
import json
from PIL import ImageFont
import pandas as pd
import matplotlib.pyplot as plt
import re
from difflib import SequenceMatcher


class PdfHandler:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extractor = PdfMultiRegionExtractor(pdf_path)
        self.df = None
        self.matched_nodes, self.unmatched_inputs, self.unmatched_outputs = None, None, None

    def extract_information_from_pdf(self):
        self.df = self.extractor.extract_groups()

    def normalize_words(self, text: str) -> list[str]:
        """Lowercase, remove punctuation, and split into clean words."""
        text = re.sub(r'[^a-zA-Z0-9]+', ' ', text.lower())
        words = text.split()
        return words

    def word_similarity_score(self, words_a: list[str], words_b: list[str]) -> float:
        """Return overlap ratio between two word lists, allowing small typos."""
        if not words_a or not words_b:
            return 0.0

        matched = 0
        for wa in words_a:
            # direct match or near match
            for wb in words_b:
                if wa == wb:
                    matched += 1
                    break
                # allow one-letter typo (>=0.85 similarity)
                if SequenceMatcher(None, wa, wb).ratio() >= 0.85:
                    matched += 1
                    break

        max_len = max(len(words_a), len(words_b))
        return matched / max_len

    def pair_inputs_outputs(self, threshold: float = 0.8):
        df = self.df
        matched_nodes, unmatched_inputs, unmatched_outputs = [], [], []

        inputs_df = df[df["Role"] == "Input"].copy()
        outputs_df = df[df["Role"] == "Output"].copy()

        # --- Parse Inputs ---
        input_nodes = []
        for _, row in inputs_df.iterrows():
            parts = [p.strip() for p in row["Extracted Text"].split(",")]
            if len(parts) < 2:
                continue
            input_name = parts[0]  # e.g. "DI 10"
            match_text = parts[1]  # e.g. "CYLINDER GUIDEPIN HOOD INNER CPL RESET"
            input_nodes.append({
                "input_name": input_name,
                "input_page": row["Page"],
                "match_text": match_text,
                "words": self.normalize_words(match_text),
            })

        # --- Parse Outputs ---
        output_nodes = []
        for _, row in outputs_df.iterrows():
            words = row["Extracted Text"].split()
            if len(words) < 2:
                continue
            output_name = words[0]
            match_text = " ".join(words[1:])
            output_nodes.append({
                "output_name": output_name,
                "output_page": row["Page"],
                "match_text": match_text,
                "words": self.normalize_words(match_text),
            })

        # --- Match Inputs to Outputs ---
        used_outputs = set()
        for inp in input_nodes:
            best_match = None
            best_score = 0.0

            for out in output_nodes:
                if out["output_name"] in used_outputs:
                    continue

                score = self.word_similarity_score(inp["words"], out["words"])
                if score > best_score:
                    best_score = score
                    best_match = out

            if best_match and best_score >= threshold:
                matched_nodes.append({
                    "Input Name": inp["input_name"],
                    "Output Name": best_match["output_name"],
                    "Shared Text": inp["match_text"],
                    "Input Page": inp["input_page"],
                    "Output Page": best_match["output_page"],
                    "Word Match %": round(best_score * 100, 1)
                })
                used_outputs.add(best_match["output_name"])
            else:
                unmatched_inputs.append(inp)

        # --- Remaining unmatched outputs ---
        for out in output_nodes:
            if out["output_name"] not in used_outputs:
                unmatched_outputs.append(out)

        self.matched_nodes = pd.DataFrame(matched_nodes)
        self.unmatched_inputs = pd.DataFrame(unmatched_inputs)
        self.unmatched_outputs = pd.DataFrame(unmatched_outputs)

    def export_data_to_excel(self):
        base_dir = Path(self.pdf_path).parent
        output_dir = base_dir / "created_files"
        output_dir.mkdir(exist_ok=True)

        pdf_stem = Path(self.pdf_path).stem
        groups_path = output_dir / f"groups_{pdf_stem}.xlsx"
        matched_path = output_dir / f"matchade_{pdf_stem}.xlsx"
        unmatched_inputs_path = output_dir / f"ensamma_inputs_{pdf_stem}.xlsx"
        unmatched_outputs_path = output_dir / f"ensamma_outputs_{pdf_stem}.xlsx"

        self.df.to_excel(groups_path, index=False)
        self.matched_nodes.to_excel(matched_path, index=False)
        self.unmatched_inputs.to_excel(unmatched_inputs_path, index=False)
        self.unmatched_outputs.to_excel(unmatched_outputs_path, index=False)


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
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.input_groups = self.load_groups_from_json("inputs.json")
        self.output_groups = self.load_groups_from_json("outputs.json")
        self.input_node_range, self.output_node_range = self.load_settings_from_json("settings.json")
        self.df = None
        self.extracted_text = {}  # plain text from the page — like reading it as a human would.
        self.extracted_words = {}  # structured positional data — each word with coordinates.

        self.extract_info_from_pdf()
        self.pages: [int, str] = self.assign_pages_per_node()

    # ---------------------------------------------------------
    def extract_groups(self) -> pd.DataFrame:
        results = []

        # iterate only classified pages
        for page_num, role in self.pages.items():
            if role not in ("Input", "Output"):
                continue

            words = self.extracted_words.get(page_num, [])
            groups = self.output_groups if role == "Output" else self.input_groups

            for group in groups:
                box_texts = []

                for box in group["boxes"]:
                    box_words = []
                    for w in words:
                        # word bbox
                        wx0, wx1 = w["x0"], w["x1"]
                        wy0, wy1 = w["bottom"], w["top"]

                        # box bbox
                        bx0, bx1 = box["x0"], box["x1"]
                        by0, by1 = box["y0"], box["y1"]

                        # overlap test (any intersection)
                        if not (wx1 < bx0 or wx0 > bx1 or wy1 < by0 or wy0 > by1):
                            box_words.append(w["text"])

                    if box_words:
                        box_texts.append(" ".join(box_words))

                if box_texts:
                    results.append({
                        "Page": page_num,
                        "Role": role,
                        "Group": group["name"],
                        "Boxes": len(group["boxes"]),
                        "Extracted Text": ", ".join(box_texts)
                    })

        return pd.DataFrame(results)

    def extract_info_from_pdf(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                words = page.extract_words() or []

                self.extracted_text[page_num] = text
                self.extracted_words[page_num] = words

    def load_groups_from_json(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

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

        for page_num, text in self.extracted_text.items():
            match = re.search(r"Nod:(\d+)", text)

            if not match:
                continue

            nod_value = int(match.group(1))

            if nod_value in self.input_node_range:
                page_roles[page_num] = "Input"
            elif nod_value in self.output_node_range:
                page_roles[page_num] = "Output"

        return page_roles


class PdfCoordinateViewer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def view_page(self, page_number=0, resolution=150):
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_number]
            pdf_width, pdf_height = page.width, page.height

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
