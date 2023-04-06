import pyvisa

import npyscreen as nps
import 


class Keithley(nps.NPSAppManaged):
    """Managed Application. Contains the Praktimatika PKTSession, so that all forms and widgets can access it."""
    def onStart(self):
        self.version = "alpha 1"
        self.settings = {
            "print_output":    True,
            "copy_clip":    True,
            "dec_sep":      ",",
            "theme":        "Default"
        }
        self.load_settings()
        self.themes = {
            "Default": nps.Themes.DefaultTheme,
            "Colourful": nps.Themes.ColorfulTheme,
            "Elegant": nps.Themes.ElegantTheme,
            "Transparent-Light Font":  nps.Themes.TransparentThemeLightText,
            "Transparent-Dark Font":   nps.Themes.TransparentThemeDarkText,
        }

        theme = nps.Themes.DefaultTheme
        if self.settings["theme"] in self.themes:
            theme = self.themes[self.settings["theme"]]

        nps.setTheme(theme)

        # stores a selected ... to be accessible for all forms: (name, value)
        self.function = ("", None)
        self.variable = ("", None)
        self.array = ("", None)
        self.constant = ("", None)


        self.start = self.addForm("MAIN", StartupMenu, name='Praktimatika Startup')
        # self.addForm("start", StartupMenu, name='Praktimatika Startup')
        self.home = self.addForm("home", tui_home.HomeMenu, name=f"Praktimatika Home (Version {self.version})")
        # APP MENUS
        self.f_settings = self.addForm("settings", tui_home.Settings, name="Praktimatika Settings")
        self.save = self.addForm("save", SaveMenu, name="Save Praktimatika PKTSession")
        self.impor = self.addForm("import", tui_import.ImportMenu, name="Import Arrays from a spreadsheet")

        # FUNCTION MENUS
        self.func = self.addForm("m_fun", tui_user_functions.UserFuncMenu, name="Function Menu")
        self.func_calc = self.addForm("m_fun_calc", tui_user_functions.UserFuncCalc2, name="Calculation Menu")

        # BUILTIN FUNCTION MENUS
        self.weighted_median = self.addForm("weighted_median", tui_functions.WeightedMedian, name="Weighted Median")
        self.error_prop = self.addForm("error_prop", tui_user_functions.ErrorPropagation, name="Error Propagation")
        self.curve_fit = self.addForm("curve_fit", tui_user_functions.CurveFit, name="Curve Fitting")
        # PLOT MENUS
        self.plot = self.addForm("plot", tui_plot.AxesMenu, name="Plot Menu")   # remove!
        self.pl_fig = self.addForm("pl_fig", tui_plot.FigMenu, name="Plot Menu - Figure")
        self.pl_ax = self.addForm("pl_ax", tui_plot.AxesMenu, name="Plot Menu - Axis")
        self.pl_pl = self.addForm("pl_pl", tui_plot.PlotMenu, name="Plot Menu - Data")
        # Add Menus
        self.add_fun = self.addForm("add_fun", tui_add.AddFun, name="Add Functions")
        self.edit_fun = self.addForm("edit_fun", tui_add.EditFunc, name="Edit Function")
        self.add_arr = self.addForm("add_arr", tui_add.AddArr, name="Add Arrays & Values")
        self.save_arr = self.addForm("save_arr", tui_functions.SaveVec, name="Save Array")
        # TOOLS
        self.latex = self.addForm("latex_table", tui_tools.LatexTable, name="Create Latex Table")


    @staticmethod
    def exit_app():
        if nps.notify_yes_no("Are you sure you want to exit?", title='Exit'):
            sys.exit()


    #
    # Settings
    #
    def load_settings(self):
        try:
            with open("keithley.conf", "r") as file:
                raw_list = file.readlines()
                file.close()
                for line in raw_list:
                    if "#" in line:  # ignore commented lines
                        continue
                    line = line.replace("\n", "")
                    temp_list = line.split(" = ")
                    if temp_list[1] == "True":
                        temp_list[1] = True
                    elif temp_list[1] == "False":
                        temp_list[1] = False
                    self.settings.update({temp_list[0]: temp_list[1]})
        except FileNotFoundError:
            nps.notify_confirm("Could not load settings from 'keithley.conf'. File not found.")
        except IndexError:
            nps.notify_confirm("Could not load settings from 'keithley.conf'. Invalid file structure")

    def save_settings(self):
        with open("praktimatika.conf", "w") as file:
            text = "# Praktimatika Config File. \n" \
                   "# Content here will be overwritten when the settings are saved.\n"
            for key, val in self.settings.items():
                text += f"{key} = {val}\n"
            file.write(text)

    @staticmethod
    def show_error(message, exception: BaseException):
        """
        Shows an Error Message in an nps.notify_confirm Form
        :param message:     string, message
        :param exception:   Exception
        :return:
        """
        nps.notify_confirm(f"{message}:\n{exception}\nin file {exception.__traceback__.tb_frame.f_code.co_filename}\n"
                           f"in line {exception.__traceback__.tb_lineno}")

if __name__ == '__main__':
    TestApp = Keithley().run()
