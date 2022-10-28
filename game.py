from constants_and_imports import *
from game_model import *
from game_view import *
from game_controller import *

class ConfigureUserForm(tk.Toplevel):

    def submit(self):
        entries = [int(field.get()) for _, field in self.input_fields]
        print(f"We received the following input: {entries}")
        for entry in entries:
            if not entry:
                messagebox.showerror(title = "Error", message = "You didn't fill in the form properly!")
                break
        else:
            print("Woohoo!")
            print(f"Custom Game Height: {entries[0]}, Custom Game Width: {entries[1]}, Custom Game Mines: {entries[2]}")
            # Once we have our settings, we should write them down in our config file.
            ConfigEditor().edit_cfg("difficulty_settings.Custom", {"height": entries[0], "width": entries[1], "mines": entries[2], "algorithm": self.algorithm.get()})
            messagebox.showinfo(title = "Configuration Success!", message = "Custom Difficulty configured successfully!")
            self.destroy()

    def __init__(self, master: tk.Tk, header = "Custom Difficulty Entry"):
        tk.Toplevel.__init__(self, master = master)
        self.title("Customise Game")

        # Define all our window elements.
        self.heading = tk.Label(self, text = header)
        self.heading.grid(row = 0, column = 1)

        self.algorithm = tk.IntVar()

        self.input_fields=[]
        for field in CUSTOM_ENTRY_FIELDS:
            field_title = tk.Label(self, text = field)
            field_input = tk.Entry(self)
            self.input_fields.append((field_title, field_input))

        self.input_fields.append((tk.Label(self, text = "Use Harder Algorithm?"), tk.Checkbutton(self, var = self.algorithm)))

        self.key_in_button = tk.Button(self, text = "Submit", bg = "grey", relief = tk.RAISED)
    
        self.key_in_button.bind("<Button>", on_click(self.submit), "GUI")
        self.key_in_button.bind("<Return>", on_click(self.submit))

        # Emplace them within our UserForm.
        for i in range(1, len(self.input_fields) + 1):
            title, input = self.input_fields[i - 1]
            if i < len(self.input_fields):
                _, next_input = self.input_fields[i]
                input.bind("<Return>", on_click(next_input.focus_set))
            else:
                input.bind("<Return>", on_click(self.key_in_button.focus_set))
            title.grid(row = i, column = 0)
            input.grid(row = i, column = 1)

        self.key_in_button.grid(row = len(self.input_fields) + 1, column = 1)
        self.input_fields.pop()

class Game(tk.Frame):

    # Using our model, view, and controller, we construct the game GUI.

    def init_game(self, difficulty):
        try:
            for child in self.root.winfo_children():
                child.grid_forget()
            diff_data = ConfigEditor().options_dict["difficulty_settings"][difficulty]
            print(diff_data)
            controller = Controller(diff_data["height"], diff_data["width"], diff_data["mines"], diff_data["algorithm"], self.root)
        except TypeError:
            messagebox.showerror(title = "Error", message = "Did you configure your custom settings properly?")
        else:
            return controller

    def configure_custom_game(self):
        duf = ConfigureUserForm(self.root)

    def bind_widgets(self):

        for i in range(len(self.difficulty_widgets) - 2):
            self.difficulty_widgets[i + 1].bind("<Button>", on_click(self.init_game, self.difficulties[i]), "GUI")
        
        # We also need to bind a configuration screen.
        # I should probably make this flexible but for now hardcoding will do.
        self.difficulty_widgets[len(self.difficulty_widgets) - 1].bind("<Button>", on_click(self.configure_custom_game), "GUI")

    def create_difficulty_widgets(self):
        self.difficulty_label = tk.Label(self.root, text = "Select a difficulty")
        self.difficulties = [difficulty for difficulty in DEFAULT_CONFIG["difficulty_settings"].keys()] + ["Configure"]

        self.difficulty_widgets = [self.difficulty_label] + [tk.Button(self.root, width = 7, bg = "grey", text = difficulty) for difficulty in self.difficulties]
    
    def setup_difficulty_widgets(self):
        for widget in self.difficulty_widgets:
            widget.grid()

        self.bind_widgets()

    def __init__(self):
        self.root = tk.Tk()
        self.create_difficulty_widgets()
        self.setup_difficulty_widgets()
        self.root.mainloop()

if __name__== "__main__":
    game = Game()