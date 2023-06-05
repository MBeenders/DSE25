import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("tudelft_ctk.json")  # Themes: "blue" (standard), "green", "dark-blue"


class Tabs(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

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

        self.options_frame = customtkinter.CTkFrame(self.tab("Sizing"), corner_radius=0, fg_color="gray16")
        self.options_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.run_frame = customtkinter.CTkFrame(self.tab("Sizing"), corner_radius=0, fg_color="gray16")
        self.run_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")

        self.selection_frame = customtkinter.CTkScrollableFrame(self.tab("Sizing"), label_text="Subsystems", corner_radius=0, width=150)
        self.selection_frame.grid(row=0, column=3, rowspan=3, sticky="nsew")
        self.selection_frame.grid_columnconfigure(0, weight=1)

        subsystems = ["engine_1", "engine_2", "recovery_1"]
        self.switches = []
        for i, subsystem in enumerate(subsystems):
            switch = customtkinter.CTkSwitch(self.selection_frame, text=subsystem, width=140)
            switch.grid(row=i, column=0, padx=5)
            switch.select()
            self.switches.append(switch)


class App(customtkinter.CTk):
    def __init__(self):
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
        self.logo_label = customtkinter.CTkLabel(self, text="Altus", font=customtkinter.CTkFont(size=30, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=5, sticky="w")

        # Tabs
        self.tabview = Tabs(master=self,
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
    app = App()
    app.mainloop()
