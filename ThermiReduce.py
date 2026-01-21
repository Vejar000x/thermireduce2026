import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import os
from pathlib import Path
import threading
import math
from typing import List, Tuple
import json
# Jhon Jairo Vejar 
"""Programa para reducir peso de imagenes"""

"""thermireduce se crea para ahorrar almacenamiento que es un activo limitado"""
class GlowButton(tk.Canvas):
    """Botón con efecto glow animado"""
    def __init__(self, parent, text, command, color='#ff6b35', **kwargs):
        super().__init__(parent, highlightthickness=0, bg='#0a0e27', **kwargs)
        self.command = command
        self.color = color
        self.text = text
        self.is_hovered = False
        self.is_disabled = False
        
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        self.draw()
    
    def _on_click(self, e):
        if not self.is_disabled:
            self.command()
    
    def set_disabled(self, disabled: bool):
        self.is_disabled = disabled
        self.draw()
    
    def draw(self):
        self.delete('all')
        w = self.winfo_reqwidth() or 200
        h = self.winfo_reqheight() or 50
        
        opacity_color = self.color if not self.is_disabled else '#4a5568'
        
        if self.is_hovered and not self.is_disabled:
            # Efecto glow más pronunciado
            for i in range(3, 0, -1):
                alpha = 20 * (4 - i)
                self.create_rectangle(5-i, 5-i, w-5+i, h-5+i, 
                                    fill='', outline=opacity_color, 
                                    width=1, tags='glow')
            self.create_rectangle(5, 5, w-5, h-5, fill=opacity_color, 
                                outline='', tags='button')
            text_color = 'white'
        else:
            self.create_rectangle(5, 5, w-5, h-5, fill='', 
                                outline=opacity_color, width=2, tags='button')
            text_color = '#cbd5e0' if self.is_disabled else 'white'
        
        self.create_text(w/2, h/2, text=self.text, fill=text_color, 
                        font=('Consolas', 11, 'bold'))
    
    def on_enter(self, e):
        if not self.is_disabled:
            self.is_hovered = True
            self.draw()
            self.config(cursor='hand2')
    
    def on_leave(self, e):
        self.is_hovered = False
        self.draw()
        self.config(cursor='')


class CircularProgress(tk.Canvas):
    """Indicador circular de progreso con animación suave"""
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, bg='#0a0e27', **kwargs)
        self.size = size
        self.percentage = 0
        self.target = 0
        self.animating = False
        self.animation_speed = 0.15
        
    def set_percentage(self, value):
        self.target = min(100, max(0, value))
        if not self.animating:
            self.animate()
    
    def animate(self):
        self.animating = True
        diff = self.target - self.percentage
        
        if abs(diff) < 0.5:
            self.percentage = self.target
            self.animating = False
            self.draw()
            return
        
        self.percentage += diff * self.animation_speed
        self.draw()
        self.after(20, self.animate)
    
    def draw(self):
        self.delete('all')
        center = self.size / 2
        radius = (self.size - 40) / 2
        
        # Círculos de fondo con efecto neón mejorado
        for i in range(4, 0, -1):
            self.create_oval(center - radius - i*3, center - radius - i*3,
                           center + radius + i*3, center + radius + i*3,
                           outline='#1a1f3a', width=1)
        
        # Arco de fondo
        self.create_arc(20, 20, self.size-20, self.size-20,
                       start=90, extent=359.99, width=14,
                       outline='#1a1f3a', style='arc')
        
        # Arco de progreso con gradiente
        if self.percentage > 0:
            extent = -(self.percentage * 3.6)
            segments = max(int(self.percentage / 4), 1)
            
            for i in range(segments):
                seg_extent = min(-14.4, extent + (i * 14.4))
                if seg_extent < 0:
                    color = self.get_gradient_color(i / max(segments-1, 1))
                    self.create_arc(20, 20, self.size-20, self.size-20,
                                   start=90 - (i * 14.4), extent=seg_extent, 
                                   width=14, outline=color, style='arc')
        
        # Punto indicador en el extremo del arco
        if self.percentage > 0:
            angle = 90 - (self.percentage * 3.6)
            rad = math.radians(angle)
            px = center + radius * math.cos(rad)
            py = center - radius * math.sin(rad)
            
            self.create_oval(px-7, py-7, px+7, py+7, 
                           fill='#00f5ff', outline='#00b8d4', width=2)
            self.create_oval(px-3, py-3, px+3, py+3, 
                           fill='white', outline='')
        
        # Texto central con sombra
        self.create_text(center+2, center - 13, 
                        text=f'{int(self.percentage)}%',
                        font=('Consolas', 40, 'bold'),
                        fill='#0a0e27')
        self.create_text(center, center - 15, 
                        text=f'{int(self.percentage)}%',
                        font=('Consolas', 40, 'bold'),
                        fill='#00f5ff')
        
        self.create_text(center, center + 20,
                        text='REDUCCIÓN',
                        font=('Consolas', 11, 'bold'),
                        fill='#6c7a89')
        
        # Marcadores decorativos
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = center + (radius + 10) * math.cos(rad)
            y1 = center + (radius + 10) * math.sin(rad)
            x2 = center + (radius + 15) * math.cos(rad)
            y2 = center + (radius + 15) * math.sin(rad)
            self.create_line(x1, y1, x2, y2, fill='#2d3748', width=2)
    
    def get_gradient_color(self, ratio):
        """Gradiente de color basado en el porcentaje"""
        if ratio < 0.25:
            return '#ff6b35'
        elif ratio < 0.5:
            return '#f7931e'
        elif ratio < 0.75:
            return '#ffd700'
        else:
            return '#00f5ff'


class SettingsManager:
    """Gestiona la persistencia de configuraciones"""
    def __init__(self):
        self.config_file = Path.home() / '.thermireduce_config.json'
        self.default_config = {
            'last_quality': 85,
            'last_output_path': '',
            'preserve_metadata': False,
            'auto_backup': True
        }
    
    def load(self) -> dict:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
        except Exception:
            pass
        return self.default_config.copy()
    
    def save(self, config: dict):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass


class ThermiReduceApp:
    """Aplicación principal de optimización de imágenes"""
    def __init__(self, root):
        self.root = root
        self.root.title("ThermiReduce - Advanced Image Optimizer")
        
        # Configurar ventana
        self._setup_window()
        
        # Variables de estado
        self.selected_path = tk.StringVar(value="No hay archivos seleccionados")
        self.output_path = tk.StringVar(value="Misma ubicación que origen")
        self.original_size_var = tk.StringVar(value="0.00")
        self.optimized_size_var = tk.StringVar(value="0.00")
        self.saved_size_var = tk.StringVar(value="0.00")
        self.quality = tk.IntVar(value=85)
        self.files_count = tk.StringVar(value="0")
        self.original_unit = tk.StringVar(value="MB")
        self.optimized_unit = tk.StringVar(value="MB")
        self.saved_unit = tk.StringVar(value="MB")
        self.current_file = tk.StringVar(value="")
        self.preserve_metadata = tk.BooleanVar(value=False)
        
        self.is_processing = False
        self.settings = SettingsManager()
        self.logo_image = None
        
        # Cargar logo si existe
        self._load_logo()
        
        # Cargar configuraciones guardadas
        self._load_settings()
        
        # Construir interfaz
        self._setup_ui()
        
        # Vincular eventos de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_window(self):
        """Configura las dimensiones y posición de la ventana"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = min(1200, int(screen_width * 0.85))
        window_height = min(850, int(screen_height * 0.85))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#0a0e27')
        self.root.resizable(True, True)
        self.root.minsize(1000, 750)
    
    def _load_settings(self):
        """Carga configuraciones guardadas"""
        config = self.settings.load()
        self.quality.set(config['last_quality'])
        if config['last_output_path']:
            self.output_path.set(config['last_output_path'])
        self.preserve_metadata.set(config['preserve_metadata'])
    
    def _load_logo(self):
        """Carga el logo si existe en la carpeta de la aplicación"""
        try:
            # Buscar logo en varias ubicaciones y formatos
            logo_paths = [
                'logo.png',
                'logo.jpg',
                'logo.jpeg',
                'assets/logo.png',
                'assets/logo.jpg',
                'images/logo.png',
                'images/logo.jpg'
            ]
            
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    img = Image.open(logo_path)
                    # Redimensionar el logo a un tamaño apropiado (máximo 80x80)
                    img.thumbnail((80, 80), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)
                    return
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            self.logo_image = None
    
    def _save_settings(self):
        """Guarda las configuraciones actuales"""
        config = {
            'last_quality': self.quality.get(),
            'last_output_path': self.output_path.get() if self.output_path.get() != "Misma ubicación que origen" else '',
            'preserve_metadata': self.preserve_metadata.get(),
            'auto_backup': True
        }
        self.settings.save(config)
    
    def _on_closing(self):
        """Maneja el cierre de la aplicación"""
        self._save_settings()
        self.root.destroy()
    
    def _setup_ui(self):
        """Construye toda la interfaz de usuario"""
        # Header
        self._create_header()
        
        # Container principal con scroll
        self.main_container = tk.Frame(self.root, bg='#0a0e27')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(self.main_container, bg='#0a0e27', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#0a0e27')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind scroll con mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Main frame
        main = tk.Frame(self.scrollable_frame, bg='#0a0e27')
        main.pack(fill=tk.BOTH, expand=True, padx=40, pady=25)
        
        # Paneles izquierdo y derecho
        left_panel = tk.Frame(main, bg='#0a0e27')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 25))
        
        right_panel = tk.Frame(main, bg='#0a0e27')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Construir secciones
        self._create_input_section(left_panel)
        self._create_output_section(left_panel)
        self._create_settings_section(left_panel)
        self._create_action_button(left_panel)
        
        self._create_progress_section(right_panel)
        self._create_stats_section(right_panel)
        
        # Barra de progreso inferior
        self._create_progress_bar()
        
        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(self, event):
        """Maneja el scroll con la rueda del mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_header(self):
        """Crea el header de la aplicación"""
        header = tk.Canvas(self.root, height=140, bg='#0a0e27', highlightthickness=0)
        header.pack(fill=tk.X)
        
        # Líneas decorativas animadas
        for i in range(6):
            y = 12 + i * 4
            gradient = 15 + i * 15
            header.create_line(0, y, 2000, y, 
                             fill=f'#{gradient:02x}{gradient:02x}{min(gradient+20, 60):02x}', 
                             width=1)
        
        # Logo (si existe)
        logo_x = 280
        if self.logo_image:
            header.create_image(logo_x, 60, image=self.logo_image)
            logo_x += 100  # Ajustar posición del texto si hay logo
        
        # Calcular centro para el texto
        text_start_x = logo_x + 70
        
        # Logo con efectos (versión texto)
        header.create_text(text_start_x + 2, 63, text='THERMI', 
                         font=('Consolas', 34, 'bold'),
                         fill='#1a1f3a')
        header.create_text(text_start_x, 60, text='THERMI', 
                         font=('Consolas', 34, 'bold'),
                         fill='#ff6b35')
        
        header.create_text(text_start_x + 142, 63, text='REDUCE', 
                         font=('Consolas', 22, 'bold'),
                         fill='#0a0e27')
        header.create_text(text_start_x + 140, 60, text='REDUCE', 
                         font=('Consolas', 22, 'bold'),
                         fill='#00f5ff')
        
        # Subtítulo
        header.create_text(text_start_x + 70, 95, text='Advanced Image Compression System',
                         font=('Consolas', 9),
                         fill='#6c7a89')
        
        # Línea decorativa inferior (ajustada si hay logo)
        line_start = 320 if self.logo_image else 320
        line_end = 720 if self.logo_image else 720
        header.create_rectangle(line_start, 120, line_end, 123, fill='#ff6b35', outline='')
        header.create_rectangle(line_start + 2, 125, line_end - 2, 126, fill='#00f5ff', outline='')
    
    def _create_input_section(self, parent):
        """Crea la sección de entrada de archivos"""
        self._create_section_title(parent, '[ ARCHIVOS DE ENTRADA ]')
        
        files_card = self._create_card(parent)
        files_card.pack(fill=tk.X, pady=(0, 20))
        
        # Display del path
        path_display = tk.Frame(files_card, bg='#0d1129', bd=1, relief=tk.SOLID)
        path_display.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(path_display, textvariable=self.selected_path,
                bg='#0d1129', fg='#00f5ff', font=('Consolas', 9),
                wraplength=450, justify=tk.LEFT, anchor=tk.W).pack(padx=12, pady=12)
        
        # Botones de selección
        btn_frame = tk.Frame(files_card, bg='#121835')
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.btn_image = GlowButton(btn_frame, '[ IMAGEN ]', self.select_image, 
                                    '#ff6b35', width=190, height=48)
        self.btn_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        
        self.btn_folder = GlowButton(btn_frame, '[ CARPETA ]', self.select_folder,
                                     '#9b59b6', width=190, height=48)
        self.btn_folder.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))
    
    def _create_output_section(self, parent):
        """Crea la sección de salida"""
        self._create_section_title(parent, '[ DESTINO DE SALIDA ]')
        
        output_card = self._create_card(parent)
        output_card.pack(fill=tk.X, pady=(0, 20))
        
        output_display = tk.Frame(output_card, bg='#0d1129', bd=1, relief=tk.SOLID)
        output_display.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(output_display, textvariable=self.output_path,
                bg='#0d1129', fg='#6c7a89', font=('Consolas', 9),
                wraplength=450, justify=tk.LEFT, anchor=tk.W).pack(padx=12, pady=12)
        
        self.btn_output = GlowButton(output_card, '[ SELECCIONAR DESTINO ]', 
                                     self.select_output, '#3498db', width=200, height=48)
        self.btn_output.pack(fill=tk.X, padx=15, pady=(0, 15))
    
    def _create_settings_section(self, parent):
        """Crea la sección de configuración"""
        self._create_section_title(parent, '[ CONFIGURACIÓN ]')
        
        quality_card = self._create_card(parent)
        quality_card.pack(fill=tk.X, pady=(0, 20))
        
        quality_inner = tk.Frame(quality_card, bg='#121835')
        quality_inner.pack(fill=tk.X, padx=15, pady=15)
        
        # Header de calidad
        q_header = tk.Frame(quality_inner, bg='#121835')
        q_header.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(q_header, text='CALIDAD:', font=('Consolas', 11, 'bold'),
                bg='#121835', fg='#6c7a89').pack(side=tk.LEFT)
        
        self.quality_display = tk.Label(q_header, text='85%',
                                       font=('Consolas', 24, 'bold'),
                                       bg='#121835', fg='#00f5ff')
        self.quality_display.pack(side=tk.RIGHT)
        
        # Slider mejorado
        slider_frame = tk.Frame(quality_inner, bg='#0d1129', height=45)
        slider_frame.pack(fill=tk.X, pady=(0, 10))
        slider_frame.pack_propagate(False)
        
        self.quality_slider = tk.Scale(slider_frame, from_=50, to=100,
                                      orient=tk.HORIZONTAL, variable=self.quality,
                                      command=self.update_quality,
                                      bg='#0d1129', fg='#00f5ff',
                                      troughcolor="#dfe0e6", bd=0,
                                      highlightthickness=0, sliderrelief=tk.FLAT,
                                      font=('Consolas', 8), activebackground='#ff6b35',
                                      showvalue=False)
        self.quality_slider.pack(fill=tk.BOTH, expand=True, padx=12)
        
        # Indicadores de calidad
        indicators = tk.Frame(quality_inner, bg='#121835')
        indicators.pack(fill=tk.X)
        
        tk.Label(indicators, text='Menor tamaño', font=('Consolas', 7),
                bg='#121835', fg='#ff6b35').pack(side=tk.LEFT)
        tk.Label(indicators, text='Mayor calidad', font=('Consolas', 7),
                bg='#121835', fg='#00ff88').pack(side=tk.RIGHT)
        
        # Checkbox de metadata
        meta_frame = tk.Frame(quality_card, bg='#121835')
        meta_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        tk.Checkbutton(meta_frame, text='Preservar metadata (EXIF)', 
                      variable=self.preserve_metadata,
                      bg='#121835', fg='#6c7a89', selectcolor='#0d1129',
                      activebackground='#121835', activeforeground='#00f5ff',
                      font=('Consolas', 9)).pack(anchor=tk.W)
    
    def _create_action_button(self, parent):
        """Crea el botón principal de acción"""
        self.btn_optimize = GlowButton(parent, '⚡ INICIAR OPTIMIZACIÓN ⚡', 
                                      self.optimize_images, '#00f5ff', 
                                      width=200, height=65)
        self.btn_optimize.pack(fill=tk.X, pady=15)
    
    def _create_progress_section(self, parent):
        """Crea la sección de progreso visual"""
        self._create_section_title(parent, '[ ANÁLISIS EN TIEMPO REAL ]')
        
        ring_container = tk.Frame(parent, bg='#0a0e27')
        ring_container.pack(pady=25)
        
        self.progress_ring = CircularProgress(ring_container, size=220)
        self.progress_ring.pack()
        
        # Label de archivo actual
        current_file_frame = self._create_card(parent)
        current_file_frame.pack(fill=tk.X, pady=(15, 0), padx=10)
        
        tk.Label(current_file_frame, text='PROCESANDO:',
                font=('Consolas', 8, 'bold'), bg='#121835',
                fg='#6c7a89').pack(pady=(10, 5))
        
        tk.Label(current_file_frame, textvariable=self.current_file,
                font=('Consolas', 8), bg='#121835', fg='#00f5ff',
                wraplength=300).pack(pady=(0, 10), padx=10)
    
    def _create_stats_section(self, parent):
        """Crea la sección de estadísticas"""
        self._create_section_title(parent, '[ ESTADÍSTICAS ]')
        
        stats_container = tk.Frame(parent, bg='#0a0e27')
        stats_container.pack(fill=tk.X, pady=12)
        
        self._create_stat_display(stats_container, 'ORIGINAL', 
                                 self.original_size_var, self.original_unit,
                                 '#ff6b35', 0)
        self._create_stat_display(stats_container, 'OPTIMIZADO',
                                 self.optimized_size_var, self.optimized_unit,
                                 '#00f5ff', 1)
        self._create_stat_display(stats_container, 'AHORRADO',
                                 self.saved_size_var, self.saved_unit,
                                 '#00ff88', 2)
        
        # Contador de archivos
        files_stat = self._create_card(stats_container)
        files_stat.pack(fill=tk.X, pady=8, padx=10)
        
        tk.Label(files_stat, text='ARCHIVOS PROCESADOS',
                font=('Consolas', 9, 'bold'), bg='#121835', 
                fg='#6c7a89').pack(pady=(12, 6))
        
        tk.Label(files_stat, textvariable=self.files_count,
                font=('Consolas', 32, 'bold'), bg='#121835',
                fg='#f7931e').pack(pady=(0, 12))
    
    def _create_progress_bar(self):
        """Crea la barra de progreso inferior"""
        progress_container = tk.Frame(self.root, bg='#1a1f3a', height=10)
        progress_container.pack(fill=tk.X, side=tk.BOTTOM)
        progress_container.pack_propagate(False)
        
        self.progress_bar = tk.Frame(progress_container, bg='#00f5ff', width=0)
        self.progress_bar.place(x=0, y=0, relheight=1)
    
    def _create_card(self, parent):
        """Crea una tarjeta (card) con estilo"""
        card = tk.Frame(parent, bg='#121835', bd=1, relief=tk.SOLID,
                       highlightbackground='#1a1f3a', highlightthickness=1)
        return card
    
    def _create_section_title(self, parent, text):
        """Crea un título de sección"""
        title_frame = tk.Frame(parent, bg='#0a0e27')
        title_frame.pack(fill=tk.X, pady=(15, 8))
        
        tk.Label(title_frame, text=text, font=('Consolas', 10, 'bold'),
                bg='#0a0e27', fg='#6c7a89').pack(anchor=tk.W)
    
    def _create_stat_display(self, parent, label, value_var, unit_var, color, index):
        """Crea un display de estadística"""
        stat_card = self._create_card(parent)
        stat_card.pack(fill=tk.X, pady=6, padx=10)
        
        tk.Label(stat_card, text=label, font=('Consolas', 9, 'bold'),
                bg='#121835', fg='#6c7a89').pack(pady=(12, 6))
        
        value_frame = tk.Frame(stat_card, bg='#121835')
        value_frame.pack()
        
        tk.Label(value_frame, textvariable=value_var,
                font=('Consolas', 28, 'bold'), bg='#121835',
                fg=color).pack(side=tk.LEFT)
        
        tk.Label(value_frame, textvariable=unit_var,
                font=('Consolas', 13, 'bold'), bg='#121835',
                fg=color).pack(side=tk.LEFT, padx=(6, 0))
        
        stat_card.pack(pady=(0, 6), padx=10)
    
    def update_quality(self, value):
        """Actualiza el display de calidad"""
        val = int(float(value))
        self.quality_display.config(text=f'{val}%')
        
        if val < 70:
            color = '#ff6b35'
        elif val < 85:
            color = '#f7931e'
        else:
            color = '#00ff88'
        self.quality_display.config(fg=color)
    
    def select_image(self):
        """Selecciona una imagen individual"""
        if self.is_processing:
            return
            
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
                ("Todos", "*.*")
            ]
        )
        if filepath:
            self.selected_path.set(filepath)
            self._reset_results()
    
    def select_folder(self):
        """Selecciona una carpeta"""
        if self.is_processing:
            return
            
        folder = filedialog.askdirectory(title="Seleccionar carpeta con imágenes")
        if folder:
            self.selected_path.set(folder)
            self._reset_results()
    
    def select_output(self):
        """Selecciona carpeta de destino"""
        if self.is_processing:
            return
            
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self.output_path.set(folder)
    
    def _reset_results(self):
        """Reinicia los resultados a valores iniciales"""
        self.original_size_var.set("0.00")
        self.optimized_size_var.set("0.00")
        self.saved_size_var.set("0.00")
        self.files_count.set("0")
        self.current_file.set("Esperando...")
        self.progress_ring.set_percentage(0)
    
    def format_size(self, size_bytes: float) -> Tuple[str, str]:
        """Retorna el tamaño formateado y la unidad apropiada"""
        if size_bytes < 1024:
            return f"{size_bytes:.2f}", "B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f}", "KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f}", "MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f}", "GB"
    
    def animate_progress_bar(self, duration: float = 2.0):
        """Anima la barra de progreso inferior"""
        steps = 50
        step_duration = int((duration * 1000) / steps)
        
        def get_width():
            self.root.update_idletasks()
            return self.root.winfo_width()
        
        def step(current):
            if current <= steps and self.is_processing:
                width = get_width()
                progress = (current / steps) * width
                self.progress_bar.place(width=progress)
                self.root.after(step_duration, lambda: step(current + 1))
            elif not self.is_processing:
                # Completar la barra
                self.progress_bar.place(width=get_width())
                self.root.after(300, lambda: self.progress_bar.place(width=0))
        
        step(0)
    
    def set_processing_state(self, processing: bool):
        """Cambia el estado de procesamiento y actualiza la UI"""
        self.is_processing = processing
        self.btn_optimize.set_disabled(processing)
        self.btn_image.set_disabled(processing)
        self.btn_folder.set_disabled(processing)
        self.btn_output.set_disabled(processing)
        
        if not processing:
            self.current_file.set("Completado")
    
    def optimize_images(self):
        """Inicia el proceso de optimización"""
        path = self.selected_path.get()
        if path == "No hay archivos seleccionados":
            messagebox.showwarning("Advertencia", 
                                 "Por favor selecciona una imagen o carpeta primero")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", 
                               "La ruta seleccionada no existe")
            return
        
        if self.is_processing:
            return
        
        # Iniciar en thread separado
        thread = threading.Thread(target=self._process_optimization, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _process_optimization(self, path: str):
        """Procesa la optimización de imágenes (ejecuta en thread separado)"""
        self.root.after(0, lambda: self.set_processing_state(True))
        self.root.after(0, lambda: self.animate_progress_bar())
        
        try:
            # Obtener lista de imágenes
            if os.path.isfile(path):
                images = [path]
            else:
                images = []
                supported_formats = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp',
                                   '*.JPG', '*.JPEG', '*.PNG', '*.WEBP', '*.BMP']
                for ext in supported_formats:
                    images.extend(Path(path).glob(ext))
                images = [str(img) for img in images]
            
            if not images:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sin resultados", 
                    "No se encontraron imágenes válidas en la ubicación seleccionada.\n\n"
                    "Formatos soportados: JPG, PNG, WebP, BMP"))
                return
            
            # Determinar carpeta de salida
            output_base = self.output_path.get()
            if output_base == "Misma ubicación que origen":
                if os.path.isfile(path):
                    output_dir = os.path.join(os.path.dirname(path), "ThermiReduce_Output")
                else:
                    output_dir = os.path.join(path, "ThermiReduce_Output")
            else:
                output_dir = os.path.join(output_base, "ThermiReduce_Output")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Variables de seguimiento
            total_original = 0
            total_optimized = 0
            processed_count = 0
            errors = []
            
            # Procesar cada imagen
            for i, img_path in enumerate(images):
                try:
                    # Actualizar UI con archivo actual
                    filename = os.path.basename(img_path)
                    self.root.after(0, lambda f=filename: self.current_file.set(f))
                    
                    # Obtener tamaño original
                    original_size = os.path.getsize(img_path)
                    total_original += original_size
                    
                    # Abrir imagen
                    img = Image.open(img_path)
                    
                    # Guardar metadata si está habilitado
                    exif_data = None
                    if self.preserve_metadata.get():
                        try:
                            exif_data = img.info.get('exif')
                        except:
                            pass
                    
                    # Preparar nombre de salida
                    name, ext = os.path.splitext(filename)
                    
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if 'A' in img.mode:
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Definir ruta de salida (convertir PNG y WebP a JPG)
                    if ext.lower() in ['.png', '.webp', '.bmp']:
                        output_path = os.path.join(output_dir, f"{name}.jpg")
                    else:
                        output_path = os.path.join(output_dir, filename)
                    
                    # Guardar con compresión
                    save_kwargs = {
                        'format': 'JPEG',
                        'optimize': True,
                        'quality': self.quality.get()
                    }
                    
                    if exif_data:
                        save_kwargs['exif'] = exif_data
                    
                    img.save(output_path, **save_kwargs)
                    
                    # Actualizar tamaño optimizado
                    total_optimized += os.path.getsize(output_path)
                    processed_count += 1
                    
                    # Actualizar contador
                    self.root.after(0, lambda c=processed_count: self.files_count.set(str(c)))
                    
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")
                    continue
            
            # Calcular estadísticas finales
            saved = total_original - total_optimized
            percent = (saved / total_original * 100) if total_original > 0 else 0
            
            # Actualizar UI con resultados
            self.root.after(0, lambda: self._animate_results(
                total_original, total_optimized, saved, percent))
            
            # Mostrar mensaje de completado
            success_msg = (
                f"✓ Proceso completado exitosamente\n\n"
                f"► {processed_count} de {len(images)} imagen(es) procesada(s)\n"
                f"► Guardadas en:\n  {output_dir}\n"
                f"► Reducción total: {percent:.1f}%\n"
                f"► Espacio ahorrado: {self.format_size(saved)[0]} {self.format_size(saved)[1]}"
            )
            
            if errors:
                success_msg += f"\n\n⚠ {len(errors)} archivo(s) con errores"
            
            self.root.after(500, lambda: messagebox.showinfo(
                "OPTIMIZACIÓN COMPLETADA", success_msg))
            
            # Mostrar errores si los hay
            if errors and len(errors) <= 5:
                error_msg = "Errores encontrados:\n\n" + "\n".join(errors[:5])
                self.root.after(1000, lambda: messagebox.showwarning(
                    "Advertencias", error_msg))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "ERROR CRÍTICO", 
                f"Error durante la optimización:\n\n{str(e)}\n\n"
                f"Por favor verifica que los archivos no estén en uso."))
        
        finally:
            self.root.after(0, lambda: self.set_processing_state(False))
    
    def _animate_results(self, original: float, optimized: float, 
                        saved: float, percent: float):
        """Anima la actualización de resultados en la UI"""
        # Formatear tamaños
        orig_val, orig_unit = self.format_size(original)
        opt_val, opt_unit = self.format_size(optimized)
        saved_val, saved_unit = self.format_size(saved)
        
        # Actualizar variables
        self.original_size_var.set(orig_val)
        self.original_unit.set(orig_unit)
        self.optimized_size_var.set(opt_val)
        self.optimized_unit.set(opt_unit)
        self.saved_size_var.set(saved_val)
        self.saved_unit.set(saved_unit)
        
        # Animar el anillo de progreso
        self.progress_ring.set_percentage(percent)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThermiReduceApp(root)
    root.mainloop()