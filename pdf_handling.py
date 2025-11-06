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
        """Return a symmetric word-based similarity ratio (0–1)."""
        if not words_a or not words_b:
            return 0.0

        # direct word overlap (case-insensitive)
        overlap = sum(1 for w in words_a if w in words_b)
        ratio_a = overlap / len(words_a)
        ratio_b = overlap / len(words_b)

        # symmetric: both must share words in similar proportion
        return (ratio_a + ratio_b) / 2

    def pair_inputs_outputs(self, threshold: float = 0.8):
        df = self.df
        matched_nodes, unmatched_inputs, unmatched_outputs = [], [], []

        inputs_df = df[df["Role"].str.lower() == "input"].copy()
        outputs_df = df[df["Role"].str.lower() == "output"].copy()


        # --------------------------------------------------------
        # Helper functions
        # --------------------------------------------------------
        def normalize_words(text: str) -> list[str]:
            text = re.sub(r'[^a-zA-Z0-9]+', ' ', text.lower())
            return text.split()

        def similar(a: str, b: str) -> bool:
            """Fuzzy comparison for near-identical words."""
            return SequenceMatcher(None, a, b).ratio() >= 0.85

        def word_similarity_score(words_a: list[str], words_b: list[str]) -> float:
            """Symmetric overlap score: both sides must share similar words."""
            if not words_a or not words_b:
                return 0.0
            overlap = 0
            for wa in words_a:
                for wb in words_b:
                    if wa == wb or similar(wa, wb):
                        overlap += 1
                        break
            ratio_a = overlap / len(words_a)
            ratio_b = overlap / len(words_b)
            return min(ratio_a, ratio_b)  # strict — must match both ways

        # --------------------------------------------------------
        # Parse Inputs
        # --------------------------------------------------------
        input_nodes = []
        for _, row in inputs_df.iterrows():
            parts = [p.strip() for p in row["Extracted Text"].split(",")]
            if len(parts) < 2:
                continue

            page_num = row["Page"]
            node_number = self.extractor.pages.get(page_num, {}).get("node", None)

            input_nodes.append({
                "input_name": parts[0],  # e.g. "DI 10"
                "match_text": parts[1],  # e.g. "CYLINDER GUIDEPIN HOOD INNER CPL RESET"
                "node_number": node_number,  # ✅ from assign_pages_per_node
                "words": normalize_words(parts[1]),
            })

        # --------------------------------------------------------
        # Parse Outputs
        # --------------------------------------------------------
        output_nodes = []
        for _, row in outputs_df.iterrows():
            words = row["Extracted Text"].split()
            if len(words) < 2:
                continue

            output_name = words[0]  # e.g. "314Y11R"
            match_text = " ".join(words[1:])

            # --- Extract output number from "Group" (e.g. "output 5") ---
            output_number = None
            group_name = str(row.get("Group", "")).strip().lower()
            match = re.search(r"output\s*(\d+)", group_name)
            if match:
                output_number = int(match.group(1))  # ✅ e.g. 5

            # --- Determine action type (set/reset) ---
            if output_name.endswith("S"):
                action_type = "set"
            elif output_name.endswith("R"):
                action_type = "reset"
            else:
                action_type = None

            node_number = row["Node"]

            output_nodes.append({
                "output_name": output_name,
                "output_number": output_number,  # ✅ now from group name
                "match_text": match_text,
                "node_number": node_number,
                "action_type": action_type,
                "words": normalize_words(match_text),
            })

        # --------------------------------------------------------
        # Match Inputs → Outputs
        # --------------------------------------------------------
        matched_input_names = set()
        matched_output_names = set()

        for out in output_nodes:
            matched_inputs_for_output = []

            for inp in input_nodes:
                inp_text = " ".join(inp["words"])

                # --- Safe, word-aware SET/RESET filtering ---
                has_set = re.search(r"\bset\b", inp_text)
                has_reset = re.search(r"\breset\b", inp_text)

                if out["action_type"] == "set":
                    if not has_set or has_reset:
                        continue
                elif out["action_type"] == "reset":
                    if not has_reset or has_set:
                        continue

                # --- Compute symmetric similarity ---
                score = word_similarity_score(inp["words"], out["words"])
                if score >= threshold:
                    matched_inputs_for_output.append({
                        "Input Name": inp["input_name"],
                        "Input Node": inp["node_number"],
                        "Similarity %": round(score * 100, 1),
                    })
                    matched_input_names.add(inp["input_name"])
                    matched_output_names.add(out["output_name"])

            # --- Record one row per output, with all matching inputs ---
            if matched_inputs_for_output:
                input_names = ", ".join(f"{i['Input Name']} ({i['Similarity %']}%)" for i in matched_inputs_for_output)
                input_nodes_str = ", ".join(str(i["Input Node"]) for i in matched_inputs_for_output)

                matched_nodes.append({
                    "Output Name": out["output_name"],
                    "Output Number": out["output_number"],
                    "Action Type": out["action_type"] or "",
                    "Shared Text": out["match_text"],
                    "Matched Inputs": input_names,
                    "Connection": f"Node_{input_nodes_str} → Node_{out['node_number']}",
                })
            else:
                unmatched_outputs.append(out)

        # --------------------------------------------------------
        # Unmatched Inputs
        # --------------------------------------------------------
        for inp in input_nodes:
            if inp["input_name"] not in matched_input_names:
                unmatched_inputs.append(inp)

        # --------------------------------------------------------
        # Save Results
        # --------------------------------------------------------
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
        self.pages: dict[int, dict[str, str | int]] = self.assign_pages_per_node()

    # ---------------------------------------------------------
    def extract_groups(self) -> pd.DataFrame:
        results = []

        # iterate only classified pages
        for page_num, info in self.pages.items():
            role = info.get("role")
            node_number = info.get("node")

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
                        "Role": role,  # ✅ now a real string
                        "Node": node_number,  # ✅ preserved from self.pages
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

            node_value = int(match.group(1))

            if node_value in self.input_node_range:
                role = "Input"
            elif node_value in self.output_node_range:
                role = "Output"
            else:
                role = "Other"

            page_roles[page_num] = {"role": role, "node": node_value}

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
