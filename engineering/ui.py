import tkinter
import tkinter.messagebox
import customtkinter
from main import Runner
from os import listdir

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class Tabs(customtkinter.CTkTabview):
    def __init__(self, master, main_program: Runner, **kwargs):
        super().__init__(master, **kwargs)

        self.main_program = main_program

        # Create tabs
        self.add("Homepage")
        self.add("Sizing")
        self.add("Simulation")
        self.add("Summary")

        # Homepage
        self.label = customtkinter.CTkLabel(master=self.tab("Homepage"))

        self.logo_label = customtkinter.CTkLabel(self.tab("Homepage"), text="Homepage", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=30)

        # Sizing
        self.tab("Sizing").grid_columnconfigure(2, weight=1)
        self.tab("Sizing").grid_rowconfigure(2, weight=1)

        # Options
        self.options_frame = customtkinter.CTkFrame(self.tab("Sizing"), corner_radius=0, fg_color="gray14", width=120)
        self.options_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.options_frame.grid_rowconfigure(8, weight=1)

        # Run
        self.run_button = customtkinter.CTkButton(self.options_frame,
                                                  command=self.run,
                                                  text="Run",
                                                  corner_radius=0,
                                                  fg_color="transparent",
                                                  hover_color="#0C2340",
                                                  font=customtkinter.CTkFont(size=15))
        self.run_button.grid(row=8, column=0, sticky="s")

        self.information_frame = customtkinter.CTkFrame(self.tab("Sizing"), corner_radius=0, fg_color="gray16")
        self.information_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")

        self.selection_frame = customtkinter.CTkScrollableFrame(self.tab("Sizing"), label_text="Subsystems", corner_radius=0, width=150, height=200)
        self.selection_frame.grid(row=0, column=3)

        # Subsystem sizing selection
        subsystems = ["engine_1", "engine_2", "recovery_1", "recovery_2", "structure", "electronics", "payload"]
        self.switches = {}
        for i, subsystem in enumerate(subsystems):
            switch = customtkinter.CTkSwitch(self.selection_frame, text=subsystem, width=140)
            switch.grid(row=i, column=0, padx=5)
            switch.select()
            self.switches[subsystem] = switch

        # File selection
        self.files_frame = customtkinter.CTkScrollableFrame(self.tab("Sizing"), label_text="Files", corner_radius=0, width=150, height=200)
        self.files_frame.grid(row=1, column=3)

        files = listdir("files/archive")
        self.radio_variable = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.files_frame, text="Files")
        self.label_radio_group.grid(row=0, column=0)

        self.radio_buttons = []
        for i, file in enumerate(files):
            radio_button = customtkinter.CTkRadioButton(master=self.label_radio_group,
                                                        text=file,
                                                        variable=self.radio_variable,
                                                        value=i,
                                                        radiobutton_width=15,
                                                        radiobutton_height=15)
            radio_button.grid(row=i, column=0, padx=5)
            self.radio_buttons.append(radio_button)

    def run(self):
        self.main_program.run_sizing()


class App(customtkinter.CTk):
    def __init__(self, main_program: Runner):
        super().__init__()

        # Configure window
        self.title("Altus Sim")
        self.geometry(f"{1100}x{580}")
        self.configure(fg_color="#00A6D6")

        # Configure layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color="gray10")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, pady=(36, 0), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,
                                                        command=self.sidebar_button_event,
                                                        text="Sizing",
                                                        corner_radius=0,
                                                        fg_color="transparent",
                                                        hover_color="#0C2340",
                                                        height=40,
                                                        font=customtkinter.CTkFont(size=20))
        self.sidebar_button_1.grid(row=0, column=0)

        self.logo_label = customtkinter.CTkLabel(self, text="Altus", font=customtkinter.CTkFont(size=28, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=5, sticky="w")

        # Tabs
        self.tabview = Tabs(master=self,
                            main_program=main_program,
                            corner_radius=0,
                            fg_color="#00A6D6",
                            segmented_button_fg_color="#00A6D6",
                            segmented_button_selected_color="#E03C31",
                            segmented_button_selected_hover_color="#EC6842",
                            segmented_button_unselected_color="#00A6D6",
                            segmented_button_unselected_hover_color="#0C2340")
        self.tabview.grid(row=0, column=1, rowspan=2, sticky="nsew")

    def sidebar_button_event(self):
        self.tabview.set("Sizing")
        print("click")


if __name__ == "__main__":
    runner = Runner()
    app = App(runner)
    app.mainloop()
