import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, filedialog
import threading
from tqdm import tqdm

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper")

        self.url_label = ttk.Label(root, text="Enter URL:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.choose_elements_button = ttk.Button(root, text="Choose Elements for Scraping", command=self.choose_elements)
        self.choose_elements_button.pack(pady=10)

        self.start_button = ttk.Button(root, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(pady=10)

        self.log_listbox = tk.Listbox(root, height=10, width=60)
        self.log_listbox.pack(pady=10, fill=tk.X)

        self.progress_bar = ttk.Progressbar(root, mode="indeterminate")
        self.progress_bar.pack(pady=5)

        self.save_path = ""

        self.selected_elements = []
        self.is_choosing_elements = False
        self.is_scraping = False
        self.lock = threading.Lock()
        self.scraping_thread = None

    def choose_elements(self):
        with self.lock:
            if self.is_scraping:
                self.log("Scraping is in progress. Please wait or cancel the process.")
                return

            self.is_choosing_elements = True
            self.element_input_window()

    def element_input_window(self):
        elements_window = tk.Toplevel(self.root)
        elements_window.title("Choose Elements for Scraping")

        ttk.Label(elements_window, text="Enter CSS Selectors (e.g., 'div#id, p.class'). Enter 'done' to finish.").pack(pady=10)

        elements_text = tk.Text(elements_window, height=10, width=40)
        elements_text.pack(pady=10)

        def confirm_selection():
            elements = elements_text.get("1.0", tk.END).strip().splitlines()
            elements = [elem.strip() for elem in elements if elem.strip()]
            self.selected_elements = elements
            self.log("Selected Elements: {}".format(", ".join(self.selected_elements)))
            elements_window.destroy()

        ttk.Button(elements_window, text="Confirm Selection", command=confirm_selection).pack(pady=10)

    def start_scraping(self):
        with self.lock:
            if self.is_scraping:
                self.log("Scraping is already in progress.")
                return

            url = self.url_entry.get()

            if not url:
                self.log("Please enter a valid URL.")
                return

            if not self.selected_elements:
                self.log("Please choose elements for scraping.")
                return

            self.save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

            if not self.save_path:
                self.log("Please choose a valid save path.")
                return

            self.is_scraping = True
            self.scraping_thread = threading.Thread(target=self.scrape_website, args=(url,))
            self.scraping_thread.start()

    def scrape_website(self, url):
        try:
            self.progress_bar.start()
            with open(self.save_path, "w", encoding="utf-8") as file:
                for _ in tqdm(range(100), desc="Scraping Progress", position=0):
                    response = requests.get(url)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        for element in self.selected_elements:
                            selected_data = soup.select(element)
                            file.write(f"Selected Data for '{element}': {selected_data}\n")
                            self.log(f"Selected Data for '{element}': {selected_data}")

                    else:
                        self.log(f"Error: {response.status_code}")
        except Exception as e:
            self.log(f"An error occurred: {e}")
        finally:
            self.is_scraping = False
            self.progress_bar.stop()

    def log(self, message):
        self.log_listbox.insert(tk.END, message)
        self.log_listbox.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
