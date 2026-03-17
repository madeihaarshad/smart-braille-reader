import PIL.Image

class BrailleTranslator:
    def __init__(self):
        # Dictionary mapping 6-dot Braille patterns to English letters
        self.alphabet = {
            (1,0,0,0,0,0): 'a', (1,0,1,0,0,0): 'b', (1,1,0,0,0,0): 'c', (1,1,0,1,0,0): 'd',
            (1,0,0,1,0,0): 'e', (1,1,1,0,0,0): 'f', (1,1,1,1,0,0): 'g', (1,0,1,1,0,0): 'h',
            (0,1,1,0,0,0): 'i', (0,1,1,1,0,0): 'j', (1,0,0,0,1,0): 'k', (1,0,1,0,1,0): 'l',
            (1,1,0,0,1,0): 'm', (1,1,0,1,1,0): 'n', (1,0,0,1,1,0): 'o', (1,1,1,0,1,0): 'p',
            (1,1,1,1,1,0): 'q', (1,0,1,1,1,0): 'r', (0,1,1,0,1,0): 's', (0,1,1,1,1,0): 't',
            (1,0,0,0,1,1): 'u', (1,0,1,0,1,1): 'v', (0,1,1,1,0,1): 'w', (1,1,0,0,1,1): 'x',
            (1,1,0,1,1,1): 'y', (1,0,0,1,1,1): 'z', (0,0,0,0,0,0): ' '
        }

    def solve(self, img_path):
        # Load image and convert to grayscale (simplifies processing)
        img = PIL.Image.open(img_path).convert('L')
        w, h = img.size
        pixels = img.load()

        # Convert grayscale image to binary:
        # 0 → Braille dot (black), 1 → background (white)
        binary = [[0 if pixels[x, y] < 128 else 1 for x in range(w)] for y in range(h)]

        # Detect connected components (each dot) using BFS
        dots = []
        visited = [[False for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                # Start BFS if pixel is part of a dot and not visited
                if binary[y][x] == 0 and not visited[y][x]:
                    q = [(x, y)]
                    visited[y][x] = True
                    comp = []

                    # BFS to collect all connected pixels of a dot
                    while q:
                        cx, cy = q.pop(0)
                        comp.append((cx, cy))

                        # Check 4-directional neighbors
                        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < w and 0 <= ny < h and binary[ny][nx] == 0 and not visited[ny][nx]:
                                visited[ny][nx] = True
                                q.append((nx, ny))

                    # Compute centroid (center point) of the dot
                    dots.append((sum(p[0] for p in comp)//len(comp), sum(p[1] for p in comp)//len(comp)))

        # If no dots detected, return message
        if not dots:
            return "No dots detected."

        # Sort dots vertically (top to bottom)
        dots.sort(key=lambda p: p[1])

        # Group dots into text lines based on vertical spacing
        lines = []
        curr_line = [dots[0]]
        for i in range(1, len(dots)):
            # If dot is close vertically, same line
            if dots[i][1] - curr_line[-1][1] < 30:
                curr_line.append(dots[i])
            else:
                # Start new line
                lines.append(sorted(curr_line, key=lambda p: p[0]))
                curr_line = [dots[i]]
        lines.append(sorted(curr_line, key=lambda p: p[0]))

        final_output = ""

        # Process each line separately
        for line in lines:
            min_y = min(p[1] for p in line)
            max_y = max(p[1] for p in line)
            line_height = max_y - min_y

            # Estimate vertical spacing between rows of Braille cell
            row_gap = line_height / 2 if line_height > 10 else 15

            # Compute average horizontal spacing between dots
            line_x = [p[0] for p in line]
            if len(line_x) > 1:
                avg_letter_gap = max(
                    sum(line_x[i+1] - line_x[i] for i in range(len(line_x)-1)) / (len(line_x)-1), 1
                )
            else:
                avg_letter_gap = 25  # fallback value

            # Split line into Braille cells based on horizontal gaps
            cells_dots = []
            curr_cell = [line[0]]
            for i in range(1, len(line)):
                # Large gap → new Braille character
                if line[i][0] - line[i-1][0] > avg_letter_gap * 1.2:
                    cells_dots.append(curr_cell)
                    curr_cell = [line[i]]
                else:
                    curr_cell.append(line[i])
            cells_dots.append(curr_cell)

            # Decode each Braille cell
            for i, cell in enumerate(cells_dots):
                c_min_x = min(p[0] for p in cell)
                pattern = [0] * 6  # initialize 6-dot pattern

                for dx, dy in cell:
                    # Determine column (left/right)
                    col = 0 if (dx - c_min_x) < 12 else 1

                    # Determine row (top/middle/bottom)
                    y_off = dy - min_y
                    if y_off < row_gap * 0.7:
                        row_idx = 0
                    elif y_off < row_gap * 1.5:
                        row_idx = 1
                    else:
                        row_idx = 2

                    # Set corresponding dot position
                    pattern[row_idx * 2 + col] = 1

                # Convert pattern to character using dictionary
                final_output += self.alphabet.get(tuple(pattern), "")

                # Detect word spacing dynamically
                if i < len(cells_dots) - 1:
                    next_min_x = min(p[0] for p in cells_dots[i+1])
                    curr_max_x = max(p[0] for p in cell)
                    gap = next_min_x - curr_max_x

                    # Large gap → space between words
                    if gap > avg_letter_gap * 3:
                        final_output += " "

            # New line after processing each text line
            final_output += "\n"

        # Return final decoded text
        return final_output.strip()