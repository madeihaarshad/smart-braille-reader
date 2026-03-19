"""
Braille Recognition System GUI
Professional, minimal, and academically appealing interface
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import re
import traceback
from braille_logic import BrailleTranslator


class BrailleApp:
    def __init__(self, root):
        """Initialize the main application window and components"""
        self.root = root
        self.root.title("Braille Recognition System - Academic Project")
        self.root.geometry("1300x800")
        self.root.configure(bg="#f8f9fa")

        self.logic = BrailleTranslator()
        self.decoded_text = ""
        self.gt_path = ""
        self.reference_image = None
        self.reference_photo = None
        self.reference_loaded = False

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.create_left_panel()
        self.create_right_panel()

        self.root.after(100, self.load_default_reference)

    # ──────────────────────────────────────────────────────────────────────────
    # Reference image helpers
    # ──────────────────────────────────────────────────────────────────────────

    def load_default_reference(self):
        """Scan current directory and load reference image if found"""
        current_dir = os.getcwd()
        print(f"\n=== Reference Image Loader ===")
        print(f"Current directory: {current_dir}")

        try:
            files = os.listdir(current_dir)
            print(f"Files in directory: {files}")
        except:
            print("Could not list directory contents")

        possible_files = [
            "decode_pattern.jpg", "decode_pattern.jpeg",
            "decode_pattern.png", "decode_pattern.JPG",
            "decode_pattern.JPEG", "decode_pattern.PNG",
            "reference.jpg", "reference.png",
            "braille_reference.jpg", "braille_alphabet.jpg",
            "braille_chart.jpg", "decode_pattern.gif",
            "decode_pattern.bmp"
        ]

        for filename in possible_files:
            if os.path.exists(filename):
                try:
                    print(f"Attempting to load: {filename}")
                    test_img = Image.open(filename)
                    print(f"Image format: {test_img.format}")
                    print(f"Image size: {test_img.size}")
                    test_img.close()

                    success = self.display_reference_image(filename)
                    if success:
                        self.ref_label.configure(
                            text=f"✅ Reference: {filename}",
                            fg="#27ae60"
                        )
                        self.reference_loaded = True
                        print(f"Successfully loaded: {filename}")
                        return True
                    else:
                        print(f"Failed to display {filename}")

                except Exception as e:
                    print(f"Error with {filename}: {str(e)}")
                    traceback.print_exc()
                    continue

        print("No reference image could be loaded")
        self.show_no_reference_message()
        return False

    def show_no_reference_message(self):
        """Display user-friendly message when no reference image is available"""
        try:
            for widget in self.image_frame.winfo_children():
                widget.destroy()
        except:
            pass

        try:
            message_frame = tk.Frame(self.image_frame, bg="#f8f9fa")
            message_frame.pack(expand=True, fill="both")

            current_dir = os.getcwd()

            tk.Label(
                message_frame,
                text="ℹ️ Reference Chart Status",
                font=("Helvetica", 16, "bold"),
                bg="#f8f9fa", fg="#3498db"
            ).pack(pady=(20, 15))

            tk.Label(
                message_frame,
                text="You can still use the Braille decoder without a reference chart.\n"
                     "The reference chart is optional for learning purposes.",
                font=("Helvetica", 11),
                bg="#f8f9fa", fg="#2c3e50", justify="center"
            ).pack(pady=(0, 20))

            tk.Label(
                message_frame,
                text="Current Directory:",
                font=("Helvetica", 10, "bold"),
                bg="#f8f9fa", fg="#34495e"
            ).pack(pady=(5, 2))

            tk.Label(
                message_frame,
                text=current_dir,
                font=("Helvetica", 9),
                bg="#f8f9fa", fg="#7f8c8d", wraplength=400
            ).pack()

            tk.Label(
                message_frame,
                text="\nTo add a reference chart later, place an image named\n"
                     "'decode_pattern.jpg' in this directory and restart.",
                font=("Helvetica", 9, "italic"),
                bg="#f8f9fa", fg="#7f8c8d", justify="center"
            ).pack(pady=(20, 10))

            self.image_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        except Exception as e:
            print(f"Error showing message: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # Panel builders
    # ──────────────────────────────────────────────────────────────────────────

    def create_left_panel(self):
        """Build the left panel containing controls and output displays"""
        left_frame = tk.Frame(self.root, bg="#ffffff", relief="solid", bd=1)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = tk.Frame(left_frame, bg="#2c3e50", height=60)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        tk.Label(
            header_frame, text="Braille Decoder",
            font=("Helvetica", 18, "bold"),
            bg="#2c3e50", fg="white"
        ).pack(expand=True)

        # Controls
        control_frame = tk.Frame(left_frame, bg="#f8f9fa", relief="flat", bd=1)
        control_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        button_style = {
            "font": ("Helvetica", 10),
            "height": 1, "width": 22,
            "relief": "flat", "cursor": "hand2", "borderwidth": 0
        }

        tk.Button(
            control_frame, text="📷 Select Braille Image",
            command=self.process,
            bg="#3498db", fg="white",
            activebackground="#2980b9", activeforeground="white",
            **button_style
        ).pack(pady=5)

        tk.Button(
            control_frame, text="📄 Load Ground Truth",
            command=self.load_gt,
            bg="#95a5a6", fg="white",
            activebackground="#7f8c8d", activeforeground="white",
            **button_style
        ).pack(pady=5)

        tk.Button(
            control_frame, text="📊 Calculate Accuracy",
            command=self.calc_accuracy,
            bg="#27ae60", fg="white",
            activebackground="#229954", activeforeground="white",
            **button_style
        ).pack(pady=5)

        self.gt_label = tk.Label(
            control_frame, text="⚫ Ground Truth: Not loaded",
            font=("Helvetica", 9), bg="#f8f9fa", fg="#7f8c8d"
        )
        self.gt_label.pack(pady=5)

        self.ref_label = tk.Label(
            control_frame, text="🖼️ Reference: Optional",
            font=("Helvetica", 9), bg="#f8f9fa", fg="#7f8c8d"
        )
        self.ref_label.pack(pady=5)

        # Decoded text output
        output_frame = tk.Frame(left_frame, bg="#ffffff")
        output_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        output_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            output_frame, text="Decoded Text",
            font=("Helvetica", 12, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(anchor="w")

        text_frame = tk.Frame(output_frame, bg="#ecf0f1", relief="flat", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.result_text = tk.Text(
            text_frame, height=6, width=40,
            font=("Consolas", 11),
            bg="#ffffff", fg="#2c3e50",
            relief="flat", bd=0, wrap="word"
        )
        self.result_text.pack(fill="both", expand=True, padx=1, pady=1)

        scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)

        # Accuracy metric tiles
        metrics_frame = tk.Frame(left_frame, bg="#ffffff")
        metrics_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        tk.Label(
            metrics_frame, text="Accuracy Metrics",
            font=("Helvetica", 12, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(anchor="w")

        cards_frame = tk.Frame(metrics_frame, bg="#ffffff")
        cards_frame.pack(fill="x", pady=(10, 0))

        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.tile_char    = self._create_metric_card(cards_frame, "Character\nAccuracy", 0)
        self.tile_full    = self._create_metric_card(cards_frame, "Full Word\nAccuracy", 1)
        self.tile_partial = self._create_metric_card(cards_frame, "Partial Word\nAccuracy", 2)
        self.tile_sent    = self._create_metric_card(cards_frame, "Sentence\nAccuracy", 3)

        # Detailed report
        details_frame = tk.Frame(left_frame, bg="#ffffff")
        details_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        details_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            details_frame, text="Detailed Report",
            font=("Helvetica", 12, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(anchor="w")

        details_text_frame = tk.Frame(details_frame, bg="#ecf0f1", relief="flat", bd=1)
        details_text_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.acc_text = tk.Text(
            details_text_frame, height=6, width=40,
            font=("Consolas", 10),
            bg="#f8f9fa", fg="#2c3e50",
            relief="flat", bd=0, state="disabled"
        )
        self.acc_text.pack(fill="both", expand=True, padx=1, pady=1)

        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_rowconfigure(4, weight=1)

    def _create_metric_card(self, parent, label, col):
        """Create a styled card for displaying a single accuracy metric"""
        card = tk.Frame(parent, bg="#3498db", relief="flat", bd=0)
        card.grid(row=0, column=col, sticky="ew", padx=5)
        card.grid_propagate(False)
        card.configure(width=110, height=100)

        tk.Label(
            card, text=label,
            font=("Helvetica", 7, "bold"),
            bg="#3498db", fg="white", justify="center"
        ).pack(expand=True)

        val = tk.Label(
            card, text="—",
            font=("Helvetica", 16, "bold"),
            bg="#3498db", fg="white"
        )
        val.pack(expand=True)

        card._val_label = val
        return card

    def create_right_panel(self):
        """Build the right panel for displaying the Braille reference chart"""
        right_frame = tk.Frame(self.root, bg="#ffffff", relief="solid", bd=1)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        header_frame = tk.Frame(right_frame, bg="#34495e", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        tk.Label(
            header_frame, text="Braille Reference Chart",
            font=("Helvetica", 16, "bold"),
            bg="#34495e", fg="white"
        ).pack(expand=True)

        main_container = tk.Frame(right_frame, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        center_frame = tk.Frame(main_container, bg="#f8f9fa")
        center_frame.pack(expand=True, fill="both")

        canvas_container = tk.Frame(center_frame, bg="#f8f9fa")
        canvas_container.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(
            canvas_container, bg="#f8f9fa", highlightthickness=0
        )
        v_scrollbar = tk.Scrollbar(
            canvas_container, orient="vertical", command=self.canvas.yview
        )
        h_scrollbar = tk.Scrollbar(
            canvas_container, orient="horizontal", command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        self.image_frame = tk.Frame(self.canvas, bg="#f8f9fa")
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.image_frame, anchor="center"
        )

        self.image_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.placeholder = tk.Label(
            self.image_frame,
            text="Loading reference chart...",
            font=("Helvetica", 12),
            bg="#f8f9fa", fg="#7f8c8d", justify="center"
        )
        self.placeholder.pack(expand=True, padx=50, pady=50)

    # ──────────────────────────────────────────────────────────────────────────
    # Canvas / scroll helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        try:
            canvas_width  = event.width
            canvas_height = event.height
            frame_width   = self.image_frame.winfo_reqwidth()
            frame_height  = self.image_frame.winfo_reqheight()
            x = max((canvas_width  - frame_width)  // 2, 0)
            y = max((canvas_height - frame_height) // 2, 0)
            self.canvas.coords(self.canvas_window, x, y)
        except:
            pass

    def display_reference_image(self, image_path):
        """Load and display the reference image in the right panel"""
        try:
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            pil_image = Image.open(image_path)

            if pil_image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                if pil_image.mode == 'RGBA':
                    background.paste(pil_image, mask=pil_image.split()[3])
                    pil_image = background
                else:
                    pil_image = pil_image.convert('RGB')

            orig_width, orig_height = pil_image.size
            max_width, max_height = 600, 700
            scale = min(max_width / orig_width, max_height / orig_height, 1.0)
            new_width  = int(orig_width  * scale)
            new_height = int(orig_height * scale)

            if scale < 1.0:
                pil_image = pil_image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

            self.reference_image = ImageTk.PhotoImage(pil_image)

            content_frame = tk.Frame(self.image_frame, bg="#f8f9fa")
            content_frame.pack(expand=True)

            tk.Label(
                content_frame,
                image=self.reference_image,
                bg="#f8f9fa"
            ).pack(pady=(10, 10))

            info_text = (
                f"File: {os.path.basename(image_path)} "
                f"• {orig_width} x {orig_height}"
            )
            tk.Label(
                content_frame, text=info_text,
                font=("Helvetica", 9),
                bg="#f8f9fa", fg="#7f8c8d"
            ).pack()

            self.image_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self._on_canvas_configure(tk.Event())
            return True

        except Exception as e:
            print(f"Error displaying image: {e}")
            traceback.print_exc()

            error_frame = tk.Frame(self.image_frame, bg="#f8f9fa")
            error_frame.pack(expand=True)
            tk.Label(
                error_frame, text="⚠️ Could not display image",
                font=("Helvetica", 12, "bold"),
                bg="#f8f9fa", fg="#e74c3c"
            ).pack(pady=10)
            tk.Label(
                error_frame, text=f"Error: {str(e)}",
                font=("Helvetica", 10),
                bg="#f8f9fa", fg="#7f8c8d", wraplength=400
            ).pack()
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Tile helper
    # ──────────────────────────────────────────────────────────────────────────

    def _set_tile(self, tile, value, good):
        """Update a metric card — green for good (>=60%), red for poor"""
        color = "#27ae60" if good else "#e74c3c"
        tile.configure(bg=color)
        for child in tile.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=color)
        tile._val_label.configure(text=value)

    # ──────────────────────────────────────────────────────────────────────────
    # Core actions
    # ──────────────────────────────────────────────────────────────────────────

    def process(self):
        """Handle selection and decoding of Braille image"""
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All", "*.*")]
        )
        if not path:
            return

        try:
            result = self.logic.solve(path)
            self.decoded_text = result

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)

            # Reset all four tiles to default blue
            for tile in (self.tile_char, self.tile_full,
                         self.tile_partial, self.tile_sent):
                tile.configure(bg="#3498db")
                for child in tile.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg="#3498db")
                tile._val_label.configure(text="—")

            self._write_acc("")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def load_gt(self):
        """Load ground truth text file for accuracy comparison"""
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All", "*.*")]
        )
        if path:
            self.gt_path = path
            self.gt_label.configure(
                text=f"✅ Ground Truth: {os.path.basename(path)}",
                fg="#27ae60"
            )

    def calc_accuracy(self):
        """Calculate and display all accuracy metrics including sentence accuracy"""
        if not self.decoded_text:
            messagebox.showwarning(
                "No Output", "Please decode a Braille image first."
            )
            return

        if not self.gt_path:
            messagebox.showwarning(
                "No Ground Truth", "Please load a ground truth .txt file first."
            )
            return

        try:
            with open(self.gt_path, encoding="utf-8") as f:
                gt_raw = f.read()

            # Normalise both texts — lowercase and strip outer whitespace
            pred  = self.decoded_text.lower().strip()
            truth = gt_raw.lower().strip()

            # ── Word lists (used by word AND character accuracy) ───────────
            truth_words = truth.split()
            pred_words  = pred.split()

            # ── Character Accuracy ─────────────────────────────────────────
            # Compare characters within each aligned word pair to avoid
            # positional drift caused by length differences between words
            total_truth_chars   = 0
            total_matched_chars = 0

            for pw, tw in zip(pred_words, truth_words):
                total_truth_chars += len(tw)
                matched = sum(pc == tc for pc, tc in zip(pw, tw))
                total_matched_chars += matched

            char_acc = round(
                total_matched_chars / max(total_truth_chars, 1) * 100, 1
            )

            # ── Full Word Accuracy ─────────────────────────────────────────
            full_matches = sum(
                pw == tw
                for pw, tw in zip(pred_words, truth_words)
            )
            full_acc = round(
                full_matches / max(len(truth_words), 1) * 100, 1
            )

            # ── Partial Word Accuracy ──────────────────────────────────────
            # Word counted as partial match if >=60% of characters match
            partial_matches = 0
            for pw, tw in zip(pred_words, truth_words):
                if len(pw) == len(tw):
                    overlap = sum(pc == tc for pc, tc in zip(pw, tw))
                    if overlap / max(len(tw), 1) >= 0.6:
                        partial_matches += 1
            partial_acc = round(
                partial_matches / max(len(truth_words), 1) * 100, 1
            )

            # ── Sentence Accuracy ──────────────────────────────────────────
            def split_sentences(text):
                """
                Split text into sentences on . ! ?
                Normalise each sentence: lowercase + collapse whitespace.
                """
                parts = re.split(r'(?<=[.!?])\s+', text.strip())
                return [
                    ' '.join(s.lower().split())
                    for s in parts if s.strip()
                ]

            truth_sents = split_sentences(truth)
            pred_sents  = split_sentences(pred)

            matched_sents = sum(
                ps == ts
                for ps, ts in zip(pred_sents, truth_sents)
            )
            sent_acc = round(
                matched_sents / max(len(truth_sents), 1) * 100, 1
            )

            # ── Update tiles ───────────────────────────────────────────────
            self._set_tile(self.tile_char,    f"{char_acc}%",    char_acc    >= 60)
            self._set_tile(self.tile_full,    f"{full_acc}%",    full_acc    >= 60)
            self._set_tile(self.tile_partial, f"{partial_acc}%", partial_acc >= 60)
            self._set_tile(self.tile_sent,    f"{sent_acc}%",    sent_acc    >= 60)

            # ── Detailed report ────────────────────────────────────────────
            lines = [
                "=" * 50,
                "              ACCURACY REPORT",
                "=" * 50,
                f"  Character Accuracy  : {char_acc}%",
                f"    Matched chars     : {total_matched_chars} / {total_truth_chars}",
                "",
                f"  Full Word Accuracy  : {full_acc}%",
                f"    Matched words     : {full_matches} / {len(truth_words)}",
                "",
                f"  Partial Word Acc.   : {partial_acc}%",
                f"    Partial matches   : {partial_matches} / {len(truth_words)}",
                "",
                f"  Sentence Accuracy   : {sent_acc}%",
                f"    Matched sentences : {matched_sents} / {len(truth_sents)}",
                f"    Predicted sents   : {len(pred_sents)}",
                f"    GT sentences      : {len(truth_sents)}",
                "",
                f"  Predicted  : {len(pred_words)} words | "
                f"{len(pred_sents)} sentences",
                f"  Ground truth: {len(truth_words)} words | "
                f"{len(truth_sents)} sentences",
                "=" * 50,
            ]
            self._write_acc('\n'.join(lines))

        except Exception as e:
            messagebox.showerror(
                "Error", f"Accuracy calculation failed: {str(e)}"
            )

    def _write_acc(self, text):
        """Write text to the accuracy details box"""
        self.acc_text.configure(state="normal")
        self.acc_text.delete(1.0, tk.END)
        self.acc_text.insert(tk.END, text)
        self.acc_text.configure(state="disabled")


# ──────────────────────────────────────────────────────────────────────────────

def main():
    """Application entry point"""
    root = tk.Tk()
    app = BrailleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
