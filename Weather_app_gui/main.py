import tkinter as tk
from tkinter import ttk, messagebox
from weather_api import WeatherAPI
from PIL import Image, ImageTk
import io
import requests

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Replace with your actual API key
        self.api = WeatherAPI("f5a22ba720d2cc38bca1d3cebdcb073f")
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Temp.TLabel', font=('Arial', 24, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Location:").pack(side=tk.LEFT)
        
        self.location_entry = ttk.Entry(search_frame, width=30)
        self.location_entry.pack(side=tk.LEFT, padx=5)
        self.location_entry.bind('<Return>', lambda e: self.get_weather())
        
        ttk.Button(search_frame, text="Search", command=self.get_weather).pack(side=tk.LEFT)
        
        # Unit selection
        self.unit_var = tk.StringVar(value='metric')
        unit_frame = ttk.Frame(main_frame)
        unit_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(unit_frame, text="Celsius", variable=self.unit_var, 
                      value='metric').pack(side=tk.LEFT)
        ttk.Radiobutton(unit_frame, text="Fahrenheit", variable=self.unit_var,
                      value='imperial').pack(side=tk.LEFT, padx=10)
        
        # Weather display frame
        self.weather_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, padding=10)
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Initially hide weather frame
        self.weather_frame.pack_forget()
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var, 
                relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)
    
    def get_weather(self):
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showwarning("Input Error", "Please enter a location")
            return
        
        self.status_var.set("Fetching weather data...")
        self.root.update()
        
        # Try to parse as coordinates
        if ',' in location:
            try:
                lat, lon = map(float, location.split(','))
                weather_data = self.api.get_readable_weather((lat, lon), self.unit_var.get())
            except ValueError:
                weather_data = {'error': "Invalid coordinates format. Use 'lat,lon'"}
        else:
            weather_data = self.api.get_readable_weather(location, self.unit_var.get())
        
        if 'error' in weather_data:
            messagebox.showerror("Error", weather_data['error'])
            self.status_var.set("Error fetching weather data")
            return
        
        self.display_weather(weather_data)
        self.status_var.set(f"Weather data for {weather_data['location']} loaded successfully")
    
    def display_weather(self, data):
        # Clear previous weather display
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
        
        # Show weather frame
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Location header
        ttk.Label(self.weather_frame, text=data['location'], 
                style='Header.TLabel').pack(pady=5)
        
        # Weather icon
        if data.get('icon'):
            try:
                icon_url = f"https://openweathermap.org/img/wn/{data['icon']}@2x.png"
                response = requests.get(icon_url, stream=True)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((100, 100), Image.LANCZOS)
                self.weather_icon = ImageTk.PhotoImage(img)
                icon_label = ttk.Label(self.weather_frame, image=self.weather_icon)
                icon_label.image = self.weather_icon
                icon_label.pack()
            except:
                pass  # Skip icon if there's an error
        
        # Temperature
        temp_frame = ttk.Frame(self.weather_frame)
        temp_frame.pack(pady=10)
        
        ttk.Label(temp_frame, text=f"{data['temperature']:.1f}°", 
                style='Temp.TLabel').pack(side=tk.LEFT)
        
        unit = 'C' if self.unit_var.get() == 'metric' else 'F'
        ttk.Label(temp_frame, text=unit, style='Temp.TLabel').pack(side=tk.LEFT, padx=5)
        
        # Conditions
        ttk.Label(self.weather_frame, 
                text=f"Conditions: {data['conditions']}").pack(anchor=tk.W)
        
        # Feels like
        ttk.Label(self.weather_frame, 
                text=f"Feels like: {data['feels_like']:.1f}°{unit}").pack(anchor=tk.W)
        
        # Humidity
        ttk.Label(self.weather_frame, 
                text=f"Humidity: {data['humidity']}%").pack(anchor=tk.W)
        
        # Wind speed
        wind_unit = 'm/s' if self.unit_var.get() == 'metric' else 'mph'
        ttk.Label(self.weather_frame, 
                text=f"Wind Speed: {data['wind_speed']} {wind_unit}").pack(anchor=tk.W)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()