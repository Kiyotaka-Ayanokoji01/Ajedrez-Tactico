import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps
import collections
from collections import deque
import math

UNDO_LIMIT = 30
DEFAULT_SIZE = (2048, 1536)  # aumentado tamaño por defecto
PALETTE = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#800080"]


class PaintApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyPaint — Colorear y Dibujar")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._make_ui_variables()
        self._build_ui()
        self._bind_shortcuts()
        self._new_canvas(DEFAULT_SIZE)

    def _make_ui_variables(self):
        self.current_color = "#000000"
        self.bg_color = "#FFFFFF"
        self.brush_size = tk.IntVar(value=12)
        self.tool = tk.StringVar(value="brush")  
        self.opacity = tk.DoubleVar(value=1.0)
        self.fill_tolerance = tk.IntVar(value=60)  
        self.undo_stack = collections.deque(maxlen=UNDO_LIMIT)
        self.image = None  
        self.draw = None   
        self.tk_image = None
        self.canvas_image_id = None
        self.last_xy = None
        self.image_path = None

    def _build_ui(self):
    
        self._build_toolbar()
        self._build_canvas_area()
        self._build_statusbar()

    def _build_toolbar(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", padx=6, pady=6)

       
        btn_open = ttk.Button(toolbar, text="Abrir", command=self.open_image)
        btn_open.pack(side="left", padx=2)
        btn_save = ttk.Button(toolbar, text="Guardar", command=self.save_image)
        btn_save.pack(side="left", padx=2)
        btn_new = ttk.Button(toolbar, text="Nuevo", command=self.action_new)
        btn_new.pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)

        
        tools = [("Pincel", "brush"), ("Borrador", "eraser"), ("Rellenar", "fill"), ("Cuentagotas", "picker")]
        for text, val in tools:
            rb = ttk.Radiobutton(toolbar, text=text, variable=self.tool, value=val)
            rb.pack(side="left", padx=4)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)

        color_frame = ttk.Frame(toolbar)
        color_frame.pack(side="left", padx=4)
        self.color_btn = ttk.Button(color_frame, text="Color", command=self.choose_color)
        self.color_btn.grid(row=0, column=0, padx=2)
        self.color_label = tk.Label(color_frame, background=self.current_color, width=3, relief="sunken")
        self.color_label.grid(row=0, column=1, padx=2)

        for i, c in enumerate(PALETTE):
            b = tk.Button(color_frame, bg=c, width=2, relief="raised", command=lambda col=c: self.set_color(col))
            b.grid(row=0, column=2 + i, padx=1)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)

        size_frame = ttk.Frame(toolbar)
        size_frame.pack(side="left", padx=4)
        ttk.Label(size_frame, text="Tamaño:").grid(row=0, column=0, padx=2)
        size_slider = ttk.Scale(size_frame, from_=1, to=200, variable=self.brush_size, orient="horizontal")
        size_slider.grid(row=0, column=1, padx=4)
        self.size_label = ttk.Label(size_frame, text=str(self.brush_size.get()))
        self.size_label.grid(row=0, column=2, padx=4)
        self.brush_size.trace("w", lambda *args: self.size_label.config(text=str(self.brush_size.get())))

        ttk.Label(toolbar, text=" Opacidad:").pack(side="left")
        opac_slider = ttk.Scale(toolbar, from_=0.1, to=1.0, variable=self.opacity, orient="horizontal", length=120)
        opac_slider.pack(side="left", padx=6)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)

        tol_frame = ttk.Frame(toolbar)
        tol_frame.pack(side="left", padx=6)
        ttk.Label(tol_frame, text="Tolerancia:").grid(row=0, column=0, padx=2)
        tol_slider = ttk.Scale(tol_frame, from_=0, to=200, variable=self.fill_tolerance, orient="horizontal", length=140)
        tol_slider.grid(row=0, column=1, padx=4)
        self.tol_label = ttk.Label(tol_frame, text=str(self.fill_tolerance.get()))
        self.tol_label.grid(row=0, column=2, padx=4)
        self.fill_tolerance.trace("w", lambda *args: self.tol_label.config(text=str(self.fill_tolerance.get())))

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)

        btn_undo = ttk.Button(toolbar, text="Deshacer", command=self.undo)
        btn_undo.pack(side="left", padx=2)
        btn_clear = ttk.Button(toolbar, text="Limpiar", command=self.clear_canvas)
        btn_clear.pack(side="left", padx=2)

    def _build_canvas_area(self):
        
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=6, pady=(0,6))

        vbar = ttk.Scrollbar(frame, orient="vertical")
        vbar.pack(side="right", fill="y")
        hbar = ttk.Scrollbar(frame, orient="horizontal")
        hbar.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(frame, bg=self.bg_color, cursor="cross",
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        hbar.config(command=self.canvas.xview)
        vbar.config(command=self.canvas.yview)

        self.canvas.bind("<ButtonPress-1>", self.on_pointer_down)
        self.canvas.bind("<B1-Motion>", self.on_pointer_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_pointer_up)
        self.canvas.bind("<Motion>", self.on_pointer_motion)
        self.canvas.bind("<Leave>", lambda e: self._hide_cursor_preview())

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def _build_statusbar(self):
        status = ttk.Frame(self)
        status.pack(side="bottom", fill="x")
        self.status_label = ttk.Label(status, text="Listo")
        self.status_label.pack(side="left", padx=6)
        self.coords_label = ttk.Label(status, text="")
        self.coords_label.pack(side="right", padx=6)

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: self.open_image())
        self.bind("<Control-s>", lambda e: self.save_image())
        self.bind("<Control-n>", lambda e: self.action_new())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("b", lambda e: self.tool.set("brush"))
        self.bind("e", lambda e: self.tool.set("eraser"))
        self.bind("f", lambda e: self.tool.set("fill"))
        self.bind("p", lambda e: self.tool.set("picker"))

    def _new_canvas(self, size):
        w, h = size
        self.image = Image.new("RGBA", (w, h), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        self._reset_canvas_view()
        self.save_state("Nuevo lienzo")
        self.image_path = None
        self.title("PyPaint — Nuevo")

    def _reset_canvas_view(self):
        win_w = min(self.image.width, 1400)
        win_h = min(self.image.height, 900)
        self.canvas.config(width=win_w, height=win_h)
        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)
            self.canvas_image_id = None
        self._update_tk_image()
        self.canvas_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))
       
        self._create_cursor_preview()

        left = max(0, (self.image.width - win_w) / 2)
        top = max(0, (self.image.height - win_h) / 2)
      
        if self.image.width > 0:
            try:
                self.canvas.xview_moveto(left / self.image.width)
            except Exception:
                pass
        if self.image.height > 0:
            try:
                self.canvas.yview_moveto(top / self.image.height)
            except Exception:
                pass

    def _update_tk_image(self):
        
        self.tk_image = ImageTk.PhotoImage(self.image)
    
        if self.canvas_image_id:
            self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("Todos", "*.*")])
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")
            return
        self.image = img.copy()
        self.draw = ImageDraw.Draw(self.image)
        self.image_path = path
        self._reset_canvas_view()
        self.save_state(f"Abrir: {os.path.basename(path)}")
        self.title(f"PyPaint — {os.path.basename(path)}")

    def save_image(self):
        if self.image_path:
            path = filedialog.asksaveasfilename(initialfile=os.path.basename(self.image_path), defaultextension=".png",
                                                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")])
        else:
            path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")])
        if not path:
            return
        try:
            
            ext = os.path.splitext(path)[1].lower()
            out = self.image
            if ext in (".jpg", ".jpeg"):
                bg = Image.new("RGB", self.image.size, self.bg_color)
                bg.paste(self.image, mask=self.image.split()[3] if self.image.mode == "RGBA" else None)
                out = bg
            out.save(path)
            self.status_label.config(text=f"Guardado: {os.path.basename(path)}")
            self.image_path = path
            self.title(f"PyPaint — {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def action_new(self):
        
        size = self._ask_new_size()
        if size:
            self._new_canvas(size)

    def _ask_new_size(self):
        d = tk.Toplevel(self)
        d.title("Nuevo lienzo")
        d.transient(self)
        ttk.Label(d, text="Ancho:").grid(row=0, column=0, padx=6, pady=6)
        w_var = tk.IntVar(value=DEFAULT_SIZE[0])
        ttk.Entry(d, textvariable=w_var).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(d, text="Alto:").grid(row=1, column=0, padx=6, pady=6)
        h_var = tk.IntVar(value=DEFAULT_SIZE[1])
        ttk.Entry(d, textvariable=h_var).grid(row=1, column=1, padx=6, pady=6)
        ok = tk.BooleanVar(value=False)

        def on_ok():
            ok.set(True)
            d.destroy()

        def on_cancel():
            d.destroy()

        ttk.Button(d, text="Crear", command=on_ok).grid(row=2, column=0, padx=6, pady=6)
        ttk.Button(d, text="Cancelar", command=on_cancel).grid(row=2, column=1, padx=6, pady=6)
        d.wait_window()
        if ok.get():
            return (max(1, w_var.get()), max(1, h_var.get()))
        return None

 
    def save_state(self, hint=None):
      
        self.undo_stack.append(self.image.copy())
        self.status_label.config(text=f"Estado guardado: {hint or 'acción'} (historial: {len(self.undo_stack)})")

    def undo(self):
        if len(self.undo_stack) <= 1:
            self.status_label.config(text="Nada para deshacer")
            return
   
        self.undo_stack.pop()
        img = self.undo_stack[-1].copy()
        self.image = img
        self.draw = ImageDraw.Draw(self.image)
        self._update_tk_image()
        self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
        self.status_label.config(text=f"Deshacer (restaurado, pasos restantes: {len(self.undo_stack)-1})")

    def clear_canvas(self):
        if messagebox.askyesno("Confirmar", "Borrar todo el contenido del lienzo?"):
            self.save_state("Limpiar")
            self.draw.rectangle([(0, 0), self.image.size], fill=self.bg_color)
            self._update_tk_image()
            self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)

    def on_pointer_down(self, event):
        x, y = self._canvas_to_image_coords(event.x, event.y)
        self.last_xy = (x, y)
        current_tool = self.tool.get()
        if current_tool == "fill":
            self.save_state("Relleno")
            tol = int(self.fill_tolerance.get())
            self._flood_fill(int(x), int(y), self._get_painted_color(), tolerance=tol)
            self._update_tk_image()
            self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
        elif current_tool == "picker":
            color = self._get_pixel_color(int(x), int(y))
            if color:
                self.set_color(color)
                self.status_label.config(text=f"Cuentagotas: {color}")
        else:
          
            self.save_state("Trazo")
            self._draw_point(x, y)
        self._show_cursor_preview()

    def on_pointer_move(self, event):
        x, y = self._canvas_to_image_coords(event.x, event.y)
        self.coords_label.config(text=f"{int(x)} x {int(y)}")
        current_tool = self.tool.get()
        if current_tool in ("brush", "eraser"):
            if self.last_xy is None:
                self.last_xy = (x, y)
            self._draw_line(self.last_xy, (x, y))
            self.last_xy = (x, y)
            self._update_tk_image()
            self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
       
        self._update_cursor_preview(event.x, event.y)

    def on_pointer_up(self, event):
        self.last_xy = None
        self._hide_cursor_preview()

    def on_pointer_motion(self, event):
      
        self._update_cursor_preview(event.x, event.y)
        x, y = self._canvas_to_image_coords(event.x, event.y)
        self.coords_label.config(text=f"{int(x)} x {int(y)}")


    def _draw_point(self, x, y):
      
        r = max(1, self.brush_size.get() / 2)
        bbox = [x - r, y - r, x + r, y + r]
        color = self._get_painted_color()
        if self.tool.get() == "eraser":
            
            self.draw.ellipse(bbox, fill=self.bg_color)
        else:
            if self.opacity.get() >= 0.999:
                self.draw.ellipse(bbox, fill=color)
            else:
               
                tmp = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
                td = ImageDraw.Draw(tmp)
                td.ellipse(bbox, fill=self._hex_to_rgba(color, int(255 * self.opacity.get())))
                self.image = Image.alpha_composite(self.image, tmp)
                self.draw = ImageDraw.Draw(self.image)

    def _draw_line(self, p0, p1):
        x0, y0 = p0
        x1, y1 = p1
        width = max(1, int(self.brush_size.get()))
        color = self._get_painted_color()
        if self.tool.get() == "eraser":
            self.draw.line([x0, y0, x1, y1], fill=self.bg_color, width=width)
        else:
            if self.opacity.get() >= 0.999:
                self.draw.line([x0, y0, x1, y1], fill=color, width=width)
               
                r = width // 2
                self.draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color)
            else:
                tmp = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
                td = ImageDraw.Draw(tmp)
                td.line([x0, y0, x1, y1], fill=self._hex_to_rgba(color, int(255 * self.opacity.get())), width=width)
                r = width // 2
                td.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=self._hex_to_rgba(color, int(255 * self.opacity.get())))
                self.image = Image.alpha_composite(self.image, tmp)
                self.draw = ImageDraw.Draw(self.image)


    def _flood_fill(self, x, y, fill_color_hex, tolerance=60):
       
        w, h = self.image.size
        if x < 0 or y < 0 or x >= w or y >= h:
            return

        pixels = self.image.load()
        target = pixels[x, y]  
        fill_rgba = self._hex_to_rgba(fill_color_hex, int(255 * self.opacity.get()))
        
        tgt_rgb = (target[0], target[1], target[2])

        
        def color_distance_sq(c1, c2):
            return (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2

        
        dist_to_fill = math.sqrt(color_distance_sq(tgt_rgb, (fill_rgba[0], fill_rgba[1], fill_rgba[2])))
        if dist_to_fill <= tolerance:
            return

        tol_sq = tolerance * tolerance

       
        def blend_pixel(old, fill):
            fa = fill[3] / 255.0
            oa = old[3] / 255.0
            out_a = fa + oa * (1 - fa)
            if out_a == 0:
                return (0, 0, 0, 0)
            
            r = int((fill[0] * fa + old[0] * oa * (1 - fa)) / out_a)
            g = int((fill[1] * fa + old[1] * oa * (1 - fa)) / out_a)
            b = int((fill[2] * fa + old[2] * oa * (1 - fa)) / out_a)
            a = int(out_a * 255)
            return (r, g, b, a)

     
        q = deque()
        q.append((x, y))
        visited = set()
        while q:
            px, py = q.popleft()
            if (px, py) in visited:
                continue
            visited.add((px, py))
            try:
                cur = pixels[px, py]
            except IndexError:
                continue
            cur_rgb = (cur[0], cur[1], cur[2])
            if color_distance_sq(cur_rgb, tgt_rgb) > tol_sq:
                continue
           
            if fill_rgba[3] >= 255:
                pixels[px, py] = fill_rgba
            else:
                pixels[px, py] = blend_pixel(cur, fill_rgba)
           
            if px > 0:
                q.append((px - 1, py))
            if px < w - 1:
                q.append((px + 1, py))
            if py > 0:
                q.append((px, py - 1))
            if py < h - 1:
                q.append((px, py + 1))


    def _create_cursor_preview(self):
      
        try:
            self.canvas.delete("cursor_preview")
        except Exception:
            pass
      
        self.cursor_id = self.canvas.create_oval(-1000, -1000, -950, -950, outline="black", width=1, tags="cursor_preview")
        self.canvas.tag_raise(self.cursor_id)
       
        self.brush_size.trace("w", lambda *a: None)

    def _refresh_cursor_preview(self):
       
        pass

    def _update_cursor_preview(self, canvas_x, canvas_y):
       
        try:
            cx = self.canvas.canvasx(canvas_x)
            cy = self.canvas.canvasy(canvas_y)
        except Exception:
            
            cx = canvas_x
            cy = canvas_y

        # radio basado en tamaño de pincel (en pixeles sobre el canvas)
        r = max(1, float(self.brush_size.get()) / 2.0)

        # limitar radio a un máximo razonable (evita problemas si variable se corrompe)
        MAX_RADIUS = 2000.0
        if r > MAX_RADIUS:
            r = MAX_RADIUS

        x0 = cx - r
        y0 = cy - r
        x1 = cx + r
        y1 = cy + r

        outline = "white" if self._is_dark(self.current_color) else "black"

        bbox = self.canvas.bbox(self.canvas_image_id) if self.canvas_image_id else None
        if bbox:
           
            img_x0, img_y0, img_x1, img_y1 = bbox
            
            if cx < img_x0 - (img_x1 - img_x0) or cx > img_x1 + (img_x1 - img_x0) or cy < img_y0 - (img_y1 - img_y0) or cy > img_y1 + (img_y1 - img_y0):
                try:
                    self.canvas.itemconfigure(self.cursor_id, state="hidden")
                except Exception:
                    pass
                return


        try:
            self.canvas.coords(self.cursor_id, x0, y0, x1, y1)
            self.canvas.itemconfig(self.cursor_id, outline=outline, width=1, dash=())
            self.canvas.itemconfigure(self.cursor_id, state="normal")
        except Exception:
           
            try:
                self.canvas.itemconfigure(self.cursor_id, state="hidden")
            except Exception:
                pass

    def _show_cursor_preview(self):
        try:
            self.canvas.itemconfigure(self.cursor_id, state="normal")
        except Exception:
            pass

    def _hide_cursor_preview(self):
        try:
            self.canvas.itemconfigure(self.cursor_id, state="hidden")
        except Exception:
            pass

    
    def _canvas_to_image_coords(self, canvas_x, canvas_y):
        return (int(self.canvas.canvasx(canvas_x)), int(self.canvas.canvasy(canvas_y)))

    def choose_color(self):
        c = colorchooser.askcolor(color=self.current_color, title="Elegir color")
        if c and c[1]:
            self.set_color(c[1])

    def set_color(self, hexcolor):
        self.current_color = hexcolor
        self.color_label.config(bg=hexcolor)
        self.status_label.config(text=f"Color {hexcolor}")

    def _get_painted_color(self):
        return self.current_color

    def _get_pixel_color(self, x, y):
        if x < 0 or y < 0 or x >= self.image.width or y >= self.image.height:
            return None
        c = self.image.getpixel((x, y))
        return "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])

    def _hex_to_rgba(self, hexcolor, a=255):
        hexcolor = hexcolor.lstrip("#")
        lv = len(hexcolor)
        if lv == 3:
            r = int(hexcolor[0] * 2, 16)
            g = int(hexcolor[1] * 2, 16)
            b = int(hexcolor[2] * 2, 16)
        else:
            r = int(hexcolor[0:2], 16)
            g = int(hexcolor[2:4], 16)
            b = int(hexcolor[4:6], 16)
        return (r, g, b, a)

    def _is_dark(self, hexcolor):
        hexcolor = hexcolor.lstrip("#")
        r = int(hexcolor[0:2], 16)
        g = int(hexcolor[2:4], 16)
        b = int(hexcolor[4:6], 16)
        luminance = (0.299*r + 0.587*g + 0.114*b) / 255
        return luminance < 0.5

    def on_close(self):
        if messagebox.askokcancel("Salir", "¿Salir sin guardar?"):
            self.destroy()


def main():
    app = PaintApp()
    app.geometry("1200x800")
    app.mainloop()


if __name__ == "__main__":
    main()