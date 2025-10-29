import customtkinter as ctk
import secrets
import string
import pyperclip
import time
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PasswordApp(ctk.CTk):
    """
    Clase principal de la aplicación Generador de Contraseñas.
    Utiliza CustomTkinter para una interfaz moderna.
    """
    def __init__(self):
        super().__init__()

        self.password_history = []
        self.clipboard_flash_job = None

        self.title("🔐 Generador de Contraseñas Seguras - CTk")
        self.geometry("800x650")
        self.minsize(650, 550)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Generador de Contraseñas Criptográficas", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.theme_toggle = ctk.CTkSwitch(self.header_frame, text="Tema Oscuro/Claro", command=self.change_appearance_mode)
        self.theme_toggle.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        if ctk.get_appearance_mode() == "Dark":
            self.theme_toggle.select()
        else:
            self.theme_toggle.deselect()

        self.main_content_frame = ctk.CTkFrame(self)
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(5, weight=1)

        self._create_controls()
        self._create_output_area()
        self._create_history_area()

        self.bind('<Control-g>', lambda event: self.generate_and_display_password())
        self.bind('<Control-c>', lambda event: self.copy_to_clipboard())
        self.bind('<Control-t>', lambda event: self.theme_toggle.toggle())
        
        self.generate_and_display_password(initial_load=True)

    def _create_controls(self):
        """Crea y posiciona los sliders y checkboxes para personalizar la contraseña."""

        length_label = ctk.CTkLabel(self.main_content_frame, text="Longitud de Contraseña (8 - 64):")
        length_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.length_var = ctk.IntVar(value=16)
        self.length_display = ctk.CTkLabel(self.main_content_frame, text=str(self.length_var.get()), width=30)
        self.length_display.grid(row=0, column=0, padx=(20, 20), pady=(15, 5), sticky="e")
        
        self.length_slider = ctk.CTkSlider(self.main_content_frame, from_=8, to=64, number_of_steps=56, 
                                           variable=self.length_var, command=self._update_length_display)
        self.length_slider.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        char_frame = ctk.CTkFrame(self.main_content_frame)
        char_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        char_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.digit_var = ctk.BooleanVar(value=True)
        self.symbol_var = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(char_frame, text="Mayúsculas (A-Z)", variable=self.upper_var).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(char_frame, text="Minúsculas (a-z)", variable=self.lower_var).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(char_frame, text="Números (0-9)", variable=self.digit_var).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(char_frame, text="Símbolos (!@#...)", variable=self.symbol_var).grid(row=0, column=3, padx=10, pady=10, sticky="w")

        generate_button = ctk.CTkButton(self.main_content_frame, text="🔄 Generar Nueva Contraseña (Ctrl+G)", 
                                        command=self.generate_and_display_password, 
                                        font=ctk.CTkFont(size=16, weight="bold"), height=40)
        generate_button.grid(row=3, column=0, padx=20, pady=(10, 15), sticky="ew")


    def _create_output_area(self):
        """Crea el área de visualización de la contraseña y el medidor de fortaleza."""

        output_frame = ctk.CTkFrame(self.main_content_frame)
        output_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.password_text = ctk.StringVar()
        
        self.password_entry = ctk.CTkEntry(output_frame, textvariable=self.password_text, 
                                          font=ctk.CTkFont('Courier New', size=18), 
                                          state="readonly",
                                          justify='center')
        self.password_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew", ipady=5)
        
        self.copy_button = ctk.CTkButton(output_frame, text="📋 Copiar (Ctrl+C)", command=self.copy_to_clipboard)
        self.copy_button.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="e")
        
        strength_frame = ctk.CTkFrame(self.main_content_frame)
        strength_frame.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")
        strength_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(strength_frame, text="Fortaleza:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.strength_bar = ctk.CTkProgressBar(strength_frame, orientation="horizontal")
        self.strength_bar.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")
        self.strength_bar.set(0)
        
        self.strength_label = ctk.CTkLabel(strength_frame, text="Muy Débil", width=70)
        self.strength_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="e")
        

    def _create_history_area(self):
        """Crea la lista y controles para el historial de contraseñas de la sesión."""
        
        history_title = ctk.CTkLabel(self.main_content_frame, text="Historial de Contraseñas de la Sesión:", 
                                     font=ctk.CTkFont(weight="bold"))
        history_title.grid(row=6, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.history_listbox = ctk.CTkScrollableFrame(self.main_content_frame, label_text="Últimas 10 Contraseñas")
        self.history_listbox.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.history_listbox.grid_columnconfigure(0, weight=1)

        self.save_button = ctk.CTkButton(self.main_content_frame, text="💾 Guardar Historial en Archivo", 
                                         command=self.save_history_to_file)
        self.save_button.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")


    def _update_length_display(self, value):
        """Actualiza la etiqueta de longitud del slider."""
        self.length_display.configure(text=str(int(value)))
        
        
    def _get_default_copy_button_color(self):
        """
        [CORRECCIÓN] Retorna el color de acento del botón de copiar.
        Usar 'blue' o 'default_theme' evita el error 'unknown color name "dark"'.
        """
        return "blue" 


    def generate_password(self):
        """Genera una contraseña criptográficamente segura."""
        
        characters = ""
        if self.upper_var.get():
            characters += string.ascii_uppercase
        if self.lower_var.get():
            characters += string.ascii_lowercase
        if self.digit_var.get():
            characters += string.digits
        if self.symbol_var.get():
            symbols = "!@#$%^&*()_-+=[]{};:<>,./?|`~"
            characters += symbols 
            
        password_length = self.length_var.get()

        if not characters:
            self.password_text.set("Error: Selecciona al menos un tipo de carácter.")
            self._update_strength_indicator(0)
            return None

        try:
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
            return password
        except Exception as e:
            self.password_text.set(f"Error de generación: {e}")
            self._update_strength_indicator(0)
            return None


    def generate_and_display_password(self, initial_load=False):
        """Genera y muestra la contraseña, actualizando el indicador y el historial."""
        
        new_password = self.generate_password()
        
        if new_password:
            self.password_text.set(new_password)
            
            strength = self.calculate_strength(new_password)
            self._update_strength_indicator(strength)
            
            if not initial_load:
                self.password_history.insert(0, new_password)
                if len(self.password_history) > 10:
                    self.password_history.pop()
                self._update_history_display()
        
        self._reset_copy_button()

    
    def calculate_strength(self, password):
        """
        Calcula la fortaleza de la contraseña basada en una heurística simple.
        Retorna un valor entre 0 y 1.0.
        """
        score = 0
        length = len(password)
        
        if length >= 8: score += 0.1
        if length >= 12: score += 0.15
        if length >= 16: score += 0.2
        if length >= 24: score += 0.2
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        
        type_count = sum([has_lower, has_upper, has_digit, has_symbol])
        
        if type_count == 2: score += 0.1
        if type_count == 3: score += 0.15
        if type_count == 4: score += 0.25
        
        return min(1.0, score)


    def _update_strength_indicator(self, strength):
        """Actualiza la barra de progreso y la etiqueta de color."""
        
        color = ""
        label_text = ""
        
        if strength < 0.3:
            color = "red"
            label_text = "Débil"
        elif strength < 0.6:
            color = "orange"
            label_text = "Media"
        elif strength < 0.9:
            color = "yellow"
            label_text = "Fuerte"
        else:
            color = "green"
            label_text = "Excelente"
            
        self.strength_bar.set(strength)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=label_text, text_color=color)
        

    def copy_to_clipboard(self, password=None):
        """Copia la contraseña mostrada o una específica al portapapeles con confirmación visual."""
        
        pw_to_copy = password if password is not None else self.password_text.get()
        
        if not pw_to_copy or "Error" in pw_to_copy:
            
             self.password_entry.focus_set()
             self.password_entry.select_range(0, 'end')
             return

        try:
            pyperclip.copy(pw_to_copy)
            
            self.copy_button.configure(text="✅ ¡Copiado!", fg_color="green")
            
            if self.clipboard_flash_job:
                self.after_cancel(self.clipboard_flash_job)

            self.clipboard_flash_job = self.after(1500, self._reset_copy_button)
            
        except pyperclip.PyperclipException as e:
            print(f"Error al copiar al portapapeles: {e}")
            self.copy_button.configure(text="❌ Error Copiar", fg_color="red")
            self.clipboard_flash_job = self.after(2500, self._reset_copy_button)
            
            
    def _reset_copy_button(self):
        """[CORRECCIÓN] Restablece el texto y color del botón de copiar al color de acento por defecto."""
        self.copy_button.configure(text="📋 Copiar (Ctrl+C)", fg_color=self._get_default_copy_button_color())
        self.clipboard_flash_job = None
        

    def _update_history_display(self):
        """Vuelve a dibujar el historial de contraseñas en el frame scrollable."""
        
        for widget in self.history_listbox.winfo_children():
            widget.destroy()
        
        for i, pw in enumerate(self.password_history):
            history_item_frame = ctk.CTkFrame(self.history_listbox)
            history_item_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            history_item_frame.grid_columnconfigure(0, weight=1)
            
            pw_label = ctk.CTkLabel(history_item_frame, text=pw, font=ctk.CTkFont('Courier New', size=12), anchor="w")
            pw_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
            
            copy_btn = ctk.CTkButton(history_item_frame, text="Copiar", width=60, 
                                     command=lambda p=pw: self.copy_to_clipboard(p))
            copy_btn.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="e")
            

    def save_history_to_file(self):
        """Guarda el historial de la sesión en un archivo de texto con timestamp."""
        
        if not self.password_history:
            self.save_button_flash("⚠️ Historial Vacío", "orange") 
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"password_history_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("--- Historial de Contraseñas Generadas ---\n")
                f.write(f"Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for pw in self.password_history:
                    f.write(f"{pw}\n")
            
            self.save_button_flash(f"💾 Guardado como {filename}", "green")
            
        except IOError as e:
            print(f"Error al escribir en el archivo: {e}")
            self.save_button_flash("❌ Error al Guardar", "red")
            
            
    def save_button_flash(self, text, color):
        """Cambio de color temporal del botón de guardar."""
        
        save_button = self.save_button
        original_text = save_button.cget("text")
        original_color = save_button.cget("fg_color")
        
        save_button.configure(text=text, fg_color=color)
        
        self.after(2000, lambda: save_button.configure(text=original_text, fg_color=original_color))
        

    def change_appearance_mode(self):
        """Cambia entre tema oscuro y claro."""
        
        new_mode = "Dark" if self.theme_toggle.get() == 1 else "Light"
        ctk.set_appearance_mode(new_mode)
        
        self._reset_copy_button()


if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()
