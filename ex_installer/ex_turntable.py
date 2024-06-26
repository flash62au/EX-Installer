"""
Module for the EX-Turntable page view

© 2023, Peter Cole. All rights reserved.

This file is part of EX-Installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CommandStation.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import Python modules
import customtkinter as ctk
import logging
import webbrowser

# Import local modules
from .common_widgets import WindowLayout, CreateToolTip
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXTurntable(WindowLayout):
    """
    Class for the EX-Turntable view
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Get the local directory to work in
        self.product = "ex_turntable"
        self.product_name = pd[self.product]["product_name"]
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_turntable_dir = fm.get_install_dir(local_repo_dir)

        # Set up title
        self.set_title_logo(pd[self.product]["product_logo"])
        self.set_title_text("Install EX-Turntable")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Version")
        self.next_back.set_back_command(lambda view="select_version_config",
                                        product="ex_turntable": parent.switch_view(view, product))
        self.next_back.set_next_text("Compile and load")
        self.next_back.set_next_command(self.generate_config)
        self.next_back.hide_monitor_button()
        self.next_back.hide_log_button()

        # Set up and grid container frames
        self.config_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.config_frame.grid(column=0, row=0, sticky="nsew")

        # Setup the screen
        self.setup_config_frame()

    def set_product_version(self, version, major=None, minor=None, patch=None):
        """
        Function to be called by the switch_frame function to set the chosen version

        This allows configuration options to be set based on the chosen version

        Eg.
        if self.product_major_version >=4 and self.product_minor_version >= 2:
        -    function_enables_track_manager()
        else:
        -    function_disables_track_manager()
        """
        self.product_version_name = version
        self.get_steppers()
        if major is not None:
            self.product_major_version = major
            if minor is not None:
                self.product_minor_version = minor
                if patch is not None:
                    self.product_patch_version = patch
        # Disable pre 0.6.0 features
        if self.product_major_version == 0 and self.product_minor_version < 6:
            self.gearing_label.configure(state="disabled", font=self.italic_instruction_font)
            self.gearing_entry.configure(state="disabled", font=self.italic_instruction_font)
            self.gearing.set(1)
        else:
            self.gearing_label.configure(state="normal", font=self.instruction_font)
            self.gearing_entry.configure(state="normal", font=self.instruction_font)
        # Disable pre 0.7.0 features
        if self.product_major_version == 0 and self.product_minor_version < 7:
            self.invert_dir_switch.deselect()
            self.invert_dir_switch.configure(state="disabled")
            self.invert_step_switch.deselect()
            self.invert_step_switch.configure(state="disabled")
            self.invert_enable_switch.deselect()
            self.invert_enable_switch.configure(state="disabled")
            self.forward_only_switch.deselect()
            self.forward_only_switch.configure(state="disabled")
            self.reverse_only_switch.deselect()
            self.reverse_only_switch.configure(state="disabled")
        else:
            self.invert_dir_switch.configure(state="normal")
            self.invert_step_switch.configure(state="normal")
            self.invert_enable_switch.configure(state="normal")
            self.forward_only_switch.configure(state="normal")
            self.reverse_only_switch.configure(state="normal")

    def setup_config_frame(self):
        """
        Setup the container frame for configuration options

        Default config parameters from config.example.h:
        - #define I2C_ADDRESS 0x60                  - General
        - #define TURNTABLE_EX_MODE TURNTABLE       - General
        - // #define TURNTABLE_EX_MODE TRAVERSER    - General
        - // #define SENSOR_TESTING                 - General
        - #define HOME_SENSOR_ACTIVE_STATE LOW      - General
        - #define LIMIT_SENSOR_ACTIVE_STATE LOW     - General
        - #define RELAY_ACTIVE_STATE HIGH           - General
        - #define PHASE_SWITCHING AUTO              - General
        - #define PHASE_SWITCH_ANGLE 45             - General
        - #define STEPPER_DRIVER ULN2003_HALF_CW    - Stepper
        - #define DISABLE_OUTPUTS_IDLE              - Stepper
        - #define STEPPER_MAX_SPEED 200             - Stepper
        - #define STEPPER_ACCELERATION 25           - Stepper

        New in 0.6.0:
        - #define STEPPER_GEARING_FACTOR 1          - Stepper

        New in 0.7.0:
        - // #define INVERT_DIRECTION               - Stepper
        - // #define INVERT_STEP                    - Stepper
        - // #define INVERT_ENABLE                  - Stepper
        - // #define ROTATE_FORWARD_ONLY            - Stepper
        - // #define ROTATE_REVERSE_ONLY            - Stepper

        Advanced:
        - #define LED_FAST 100                      - Advanced
        - #define LED_SLOW 500                      - Advanced
        - // #define DEBUG                          - Advanced
        - // #define SANITY_STEPS 10000             - Advanced
        - // #define HOME_SENSITIVITY 300           - Advanced
        - // #define FULL_STEP_COUNT 4096           - Advanced
        - // #define DEBOUNCE_DELAY 10              - Advanced
        """
        grid_options = {"padx": 5, "pady": 5}
        toggle_options = {"text": None, "fg_color": "#00A3B9", "progress_color": "#00A3B9",
                          "width": 30, "bg_color": "#D9D9D9"}
        toggle_label_options = {"width": 80, "bg_color": "#D9D9D9"}
        subframe_options = {"border_width": 0}

        # Instructions
        instructions = ("You must select the appropriate options on the General and Stepper Options tab before " +
                        "you can continue. Please also ensure you read the documentation prior to installing.")

        # Tooltip text
        i2c_tip = ("You need to specify an available, valid I\u00B2C address for EX-Turntable. Valid values are " +
                   "from 0x08 to 0x77. Click this tip to open the EX-Turntable documentation")
        stepper_tip = ("Selecting the correct stepper driver is imperative for the correct operation of your " +
                       "turntable. Click this tip to open the stepper information in the documentation.")
        mode_tip = ("EX-Turntable can operate in either turntable (continuous rotation) or traverser ( limited " +
                    "rotation) mode. Click this tip to open the traverser documentation for more information.")
        relay_tip = ("When using relays, active low means the relays are activated when the input is set to 0V " +
                     "or ground, and deactivated when set to 5V. The inverse is true for active high relays.")
        home_tip = ("Active low sensors set their output to 0V or ground when activated, whereas active high " +
                    "sensors set their output to 5V.")
        limit_tip = ("Setting the limit sensor type is only valid when in traverser mode. " +
                     "Active low sensors set their output to 0V or ground when activated, whereas active high " +
                     "sensors set their output to 5V.")
        sensor_test_tip = ("When running EX-Turntable in traverser mode, it is recommended to run in sensor testing " +
                           "mode initially to ensure the home and limit sensors are configured correctly. Failure " +
                           "to check your sensors may lead to mechanical damage should the traverser be driven " +
                           "beyond the physical design limitations. Click this tip to open the relevant documentation.")
        phase_tip = ("By default, EX-Turntable will use attached relays to invert the polarity or phase of the " +
                     "turntable bridge track at the angle specified. Click this tip to open the relevant " +
                     "documentation.")
        idle_tip = ("By default, the stepper is disabled when idle. This prevents the driver from over heating and " +
                    "consuming excess power. If your configuration requires the stepper to forcibly maintain " +
                    "position when idle, disable this option.")
        speed_tip = ("This defines the top speed of the stepper. The limit here is determined by the Arduino " +
                     "device. A sensible max speed for Nanos/Unos would be 4000.")
        accel_tip = ("This defines the rate at which the stepper speed increases to the top speed, and decreases " +
                     "until it stops.")
        advanced_tip = ("Enable this option to be able to directly edit the configuration file on the next screen.")
        gear_factor_tip = ("For step counts larger than 32767 you must set an appropriate gearing factor. Click this " +
                           "tip to open the EX-Turntable documentation (From version 0.6.0).")
        invert_direction_tip = ("Enable this to invert the direction pin for two wire stepper drivers. This does not " +
                                "to ULN2003 (from version 0.7.0).")
        invert_step_tip = ("Enable this to invert the step pin for two wire stepper drivers. This does not " +
                           "to ULN2003 (from version 0.7.0).")
        invert_enable_tip = ("Enable this to invert the enable pin for two wire stepper drivers. This does not " +
                             "to ULN2003. Enable this if you previously used the A4988_INV stepper option " +
                             "(from version 0.7.0).")
        forward_only_tip = ("Enable this to force the stepper to rotate in the forward direction only. This can be " +
                            "useful to work around stepper or gearbox slop (from version 0.7.0).")
        reverse_only_tip = ("Enable this to force the stepper to rotate in the reverse direction only. This can be " +
                            "useful to work around stepper or gearbox slop (from version 0.7.0).")
        advanced_tip = ("Refer to the EX-Turntable documentation for information on advanced options. Click this tip " +
                        "to open the relevant documentation.")

        # Setup tabview for config options
        self.config_tabview = ctk.CTkTabview(self.config_frame, border_width=2,
                                             segmented_button_fg_color="#00A3B9",
                                             segmented_button_unselected_color="#00A3B9",
                                             segmented_button_selected_color="#00353D",
                                             segmented_button_selected_hover_color="#017E8F",
                                             text_color="white")

        tab_list = [
            "General",
            "Stepper Options",
            "Advanced"
        ]
        for tab in tab_list:
            self.config_tabview.add(tab)
            self.config_tabview.tab(tab).grid_columnconfigure(0, weight=1)
            self.config_tabview.tab(tab).grid_rowconfigure(0, weight=1)

        # Tab frames
        tab_frame_options = {"column": 0, "row": 0, "sticky": "nsew"}
        self.general_tab_frame = ctk.CTkFrame(self.config_tabview.tab("General"), border_width=0)
        self.general_tab_frame.grid(**tab_frame_options)
        self.stepper_tab_frame = ctk.CTkFrame(self.config_tabview.tab("Stepper Options"), border_width=0)
        self.stepper_tab_frame.grid(**tab_frame_options)
        self.advanced_tab_frame = ctk.CTkFrame(self.config_tabview.tab("Advanced"), border_width=0)
        self.advanced_tab_frame.grid(**tab_frame_options)

        # Instruction widget
        self.instruction_label = ctk.CTkLabel(self.config_frame, text=instructions, width=780, wraplength=760,
                                              font=self.instruction_font)
        self.instruction_label.bind("<Button-1>", lambda x:
                                    webbrowser.open_new("https://dcc-ex.com/ex-turntable/index.html"))

        # Create general subframes for grouping
        self.main_options_frame = ctk.CTkFrame(self.general_tab_frame, width=760, border_width=0)
        self.phase_frame = ctk.CTkFrame(self.general_tab_frame, width=760, border_width=0)
        self.sensor_frame = ctk.CTkFrame(self.general_tab_frame, width=760, border_width=0)

        # Create I2C widgets
        self.i2c_address = ctk.StringVar(self, value=60)
        self.i2c_address_frame = ctk.CTkFrame(self.main_options_frame, border_width=0)
        self.i2c_address_label = ctk.CTkLabel(self.i2c_address_frame, text="Set I\u00B2C address:",
                                              font=self.instruction_font)
        CreateToolTip(self.i2c_address_label, i2c_tip, "https://dcc-ex.com/ex-turntable/configure.html#i2c-address")
        self.set_i2c_frame = ctk.CTkFrame(self.i2c_address_frame, border_width=2)
        self.i2c_address_minus = ctk.CTkButton(self.set_i2c_frame, text="-", width=30,
                                               command=self.decrement_address)
        self.i2c_entry_frame = ctk.CTkFrame(self.set_i2c_frame, border_width=0)
        self.i2c_0x_label = ctk.CTkLabel(self.i2c_entry_frame, text="0x", font=self.instruction_font,
                                         width=20, padx=0, pady=0)
        self.i2c_address_entry = ctk.CTkEntry(self.i2c_entry_frame, textvariable=self.i2c_address,
                                              width=30, border_width=0, justify="left",
                                              font=self.instruction_font)
        self.i2c_address_plus = ctk.CTkButton(self.set_i2c_frame, text="+", width=30,
                                              command=self.increment_address)

        # Validate I2C address if entered manually
        self.i2c_address_entry.bind("<FocusOut>", self.validate_i2c_address)

        # Layout I2C address frame
        self.i2c_address_frame.grid_columnconfigure((0, 1), weight=1)
        self.i2c_address_frame.grid_rowconfigure(0, weight=1)
        self.i2c_entry_frame.grid_columnconfigure((0, 1), weight=1)
        self.i2c_entry_frame.grid_rowconfigure(0, weight=1)
        self.set_i2c_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.set_i2c_frame.grid_rowconfigure(0, weight=1)
        self.set_i2c_frame.grid(column=1, row=0, **grid_options)
        self.i2c_0x_label.grid(column=0, row=0, sticky="e", pady=2)
        self.i2c_address_entry.grid(column=1, row=0, padx=0, pady=2)
        self.i2c_address_label.grid(column=0, row=0, **grid_options)
        self.i2c_address_minus.grid(column=1, row=0, padx=(4, 0), pady=2)
        self.i2c_entry_frame.grid(column=2, row=0, pady=2)
        self.i2c_address_plus.grid(column=3, row=0, sticky="w", padx=(0, 4), pady=2)

        # Create mode widgets
        self.mode_frame = ctk.CTkFrame(self.main_options_frame, **subframe_options)
        self.mode_frame.grid_columnconfigure((0, 1), weight=1)
        self.mode_frame.grid_rowconfigure(0, weight=1)
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Select the operating mode:",
                                       font=self.instruction_font)
        CreateToolTip(self.mode_label, mode_tip,
                      "https://dcc-ex.com/ex-turntable/traverser.html")
        self.mode_switch_frame = ctk.CTkFrame(self.mode_frame, border_width=2)
        self.mode_switch_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.mode_switch_frame.grid_rowconfigure(0, weight=1)
        self.turntable_label = ctk.CTkLabel(self.mode_switch_frame, text="Turntable", **toggle_label_options)
        self.mode_switch = ctk.CTkSwitch(self.mode_switch_frame, onvalue="TRAVERSER", offvalue="TURNTABLE",
                                         command=self.set_mode, **toggle_options)
        self.traverser_label = ctk.CTkLabel(self.mode_switch_frame, text="Traverser", **toggle_label_options)

        # Layout mode frame
        self.mode_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.mode_switch_frame.grid(column=1, row=0, **grid_options)
        self.turntable_label.grid(column=0, row=0, sticky="nse", padx=(5, 0), pady=5)
        self.mode_switch.grid(column=1, row=0, sticky="nsew", padx=0, pady=5)
        self.traverser_label.grid(column=2, row=0, sticky="nsw", padx=(0, 5), pady=5)

        # Create phase switch widgets
        self.auto_switch = ctk.CTkSwitch(self.phase_frame, text="Automatic phase switch at angle:",
                                         onvalue="AUTO", offvalue="MANUAL", font=self.instruction_font,
                                         command=self.set_phase_switching)
        CreateToolTip(self.auto_switch, phase_tip,
                      "https://dcc-ex.com/ex-turntable/overview.html#important-phase-or-polarity-switching")
        self.auto_switch.select()
        self.phase_angle = ctk.StringVar(self, value="45")
        self.phase_angle_entry = ctk.CTkEntry(self.phase_frame, textvariable=self.phase_angle, width=40,
                                              font=self.instruction_font)

        # Create relay widgets
        self.relay_frame = ctk.CTkFrame(self.phase_frame, **subframe_options)
        self.relay_frame.grid_columnconfigure((0, 1), weight=1)
        self.relay_frame.grid_rowconfigure(0, weight=1)
        self.relay_label = ctk.CTkLabel(self.relay_frame, text="Relay type:",
                                        font=self.instruction_font)
        CreateToolTip(self.relay_label, relay_tip)
        self.relay_switch_frame = ctk.CTkFrame(self.relay_frame, border_width=2)
        self.relay_switch_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.relay_switch_frame.grid_rowconfigure(0, weight=1)
        self.relay_low_label = ctk.CTkLabel(self.relay_switch_frame, text="Active Low", **toggle_label_options)
        self.relay_switch = ctk.CTkSwitch(self.relay_switch_frame, onvalue="HIGH", offvalue="LOW",
                                          command=self.set_relay, **toggle_options)
        self.relay_switch.select()
        self.relay_high_label = ctk.CTkLabel(self.relay_switch_frame, text="Active High", **toggle_label_options)

        # Layout relay frame
        self.relay_label.grid(column=0, row=0, sticky="e", padx=(5, 1), pady=5)
        self.relay_switch_frame.grid(column=1, row=0, **grid_options)
        self.relay_low_label.grid(column=0, row=0, sticky="nse", padx=(5, 0), pady=5)
        self.relay_switch.grid(column=1, row=0, sticky="nsew", padx=0, pady=5)
        self.relay_high_label.grid(column=2, row=0, sticky="nsw", padx=(0, 5), pady=5)

        # Create sensor widgets
        self.home_sensor_frame = ctk.CTkFrame(self.sensor_frame, **subframe_options)
        self.limit_sensor_frame = ctk.CTkFrame(self.sensor_frame, **subframe_options)
        self.home_sensor_frame.grid_columnconfigure((0, 1), weight=1)
        self.home_sensor_frame.grid_rowconfigure(0, weight=1)
        self.limit_sensor_frame.grid_columnconfigure((0, 1), weight=1)
        self.limit_sensor_frame.grid_rowconfigure(0, weight=1)
        self.home_label = ctk.CTkLabel(self.home_sensor_frame, text="Home sensor type:",
                                       font=self.instruction_font)
        CreateToolTip(self.home_label, home_tip)
        self.limit_label = ctk.CTkLabel(self.limit_sensor_frame, text="Limit sensor type:",
                                        font=self.instruction_font)
        CreateToolTip(self.limit_label, limit_tip)
        self.home_switch_frame = ctk.CTkFrame(self.home_sensor_frame, border_width=2)
        self.home_switch_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.home_switch_frame.grid_rowconfigure(0, weight=1)
        self.home_low_label = ctk.CTkLabel(self.home_switch_frame, text="Active Low", **toggle_label_options)
        self.home_switch = ctk.CTkSwitch(self.home_switch_frame, onvalue="HIGH", offvalue="LOW",
                                         command=self.set_home, **toggle_options)
        self.home_high_label = ctk.CTkLabel(self.home_switch_frame, text="Active High", **toggle_label_options)
        self.limit_switch_frame = ctk.CTkFrame(self.limit_sensor_frame, border_width=2)
        self.limit_switch_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.limit_switch_frame.grid_rowconfigure(0, weight=1)
        self.limit_low_label = ctk.CTkLabel(self.limit_switch_frame, text="Active Low", **toggle_label_options)
        self.limit_switch = ctk.CTkSwitch(self.limit_switch_frame, onvalue="HIGH", offvalue="LOW",
                                          command=self.set_limit, **toggle_options)
        self.limit_high_label = ctk.CTkLabel(self.limit_switch_frame, text="Active High", **toggle_label_options)

        # Layout sensor frames
        self.home_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.home_switch_frame.grid(column=1, row=0, **grid_options)
        self.home_low_label.grid(column=0, row=0, sticky="nse", padx=(5, 0), pady=5)
        self.home_switch.grid(column=1, row=0, sticky="nsew", padx=0, pady=5)
        self.home_high_label.grid(column=2, row=0, sticky="nww", padx=(0, 5), pady=5)
        self.limit_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.limit_switch_frame.grid(column=1, row=0, **grid_options)
        self.limit_low_label.grid(column=0, row=0, sticky="nse", padx=(5, 0), pady=5)
        self.limit_switch.grid(column=1, row=0, sticky="nsew", padx=0, pady=5)
        self.limit_high_label.grid(column=2, row=0, sticky="nsw", padx=(0, 5), pady=5)

        # Create sensor test widget
        self.sensor_test_switch = ctk.CTkSwitch(self.sensor_frame, text="Enable sensor testing mode",
                                                onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.sensor_test_switch, sensor_test_tip,
                      "https://dcc-ex.com/ex-turntable/traverser.html#considerations-turntable-vs-traverser")

        # Edit config widget
        self.advanced_config_enabled = ctk.CTkSwitch(self.config_frame, text="Edit Config",
                                                     onvalue="on", offvalue="off",
                                                     font=self.instruction_font,
                                                     command=self.set_advanced_config)
        CreateToolTip(self.advanced_config_enabled, advanced_tip)

        # Layout main options frame
        self.main_options_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_options_frame.grid_rowconfigure(0, weight=1)
        self.i2c_address_frame.grid(column=0, row=0, **grid_options)
        self.mode_frame.grid(column=1, row=0, **grid_options)

        # Layout phase frame
        self.phase_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.phase_frame.grid_rowconfigure(0, weight=1)
        self.auto_switch.grid(column=0, row=0, sticky="e", padx=(5, 1), pady=5)
        self.phase_angle_entry.grid(column=1, row=0, sticky="w", padx=(1, 5), pady=5)
        self.relay_frame.grid(column=2, row=0, **grid_options)

        # Layout sensor frame
        self.sensor_frame.grid_columnconfigure(0, weight=1)
        self.sensor_frame.grid_rowconfigure(0, weight=1)
        self.home_sensor_frame.grid(column=0, row=0, **grid_options)
        self.limit_sensor_frame.grid(column=1, row=0, **grid_options)
        self.sensor_test_switch.grid(column=0, row=1, columnspan=2, **grid_options)

        # Layout general tab frame
        self.general_tab_frame.grid_columnconfigure((0, 1), weight=1)
        self.general_tab_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.main_options_frame.grid(column=0, row=0)
        self.phase_frame.grid(column=0, row=1)
        self.sensor_frame.grid(column=0, row=2)

        # Create stepper frames for grouping
        self.stepper_frame = ctk.CTkFrame(self.stepper_tab_frame, width=760, border_width=0)
        self.stepper_speed_frame = ctk.CTkFrame(self.stepper_tab_frame, width=760, border_width=0)
        self.stepper_switch_frame = ctk.CTkFrame(self.stepper_tab_frame, width=760, border_width=0)

        # Create stepper selection widgets
        self.stepper_label = ctk.CTkLabel(self.stepper_frame, text="Select the stepper driver:",
                                          font=self.instruction_font)
        CreateToolTip(self.stepper_label, stepper_tip,
                      "https://dcc-ex.com/ex-turntable/purchasing.html#supported-stepper-drivers-and-motors")
        self.stepper_combo = ctk.CTkComboBox(self.stepper_frame, values=["Select stepper driver"],
                                             width=200, command=self.check_stepper)
        self.gearing_label = ctk.CTkLabel(self.stepper_frame, text="Set the gearing factor",
                                          font=self.instruction_font)
        CreateToolTip(self.gearing_label, gear_factor_tip,
                      "https://dcc-ex.com/ex-turntable/configure.html#stepper-gearing-factor")
        self.gearing = ctk.StringVar(self, value="1")
        self.gearing_entry = ctk.CTkEntry(self.stepper_frame, textvariable=self.gearing, font=self.instruction_font,
                                          width=40)

        # Create stepper tuning widgets
        self.speed_label = ctk.CTkLabel(self.stepper_speed_frame, text="Set the stepper top speed",
                                        font=self.instruction_font)
        CreateToolTip(self.speed_label, speed_tip)
        self.speed = ctk.StringVar(self, value="200")
        self.speed_entry = ctk.CTkEntry(self.stepper_speed_frame, textvariable=self.speed, font=self.instruction_font,
                                        width=60)
        self.accel_label = ctk.CTkLabel(self.stepper_speed_frame, text="Set acceleration rate",
                                        font=self.instruction_font)
        CreateToolTip(self.accel_label, accel_tip)
        self.accel = ctk.StringVar(self, value="25")
        self.accel_entry = ctk.CTkEntry(self.stepper_speed_frame, textvariable=self.accel, font=self.instruction_font,
                                        width=40)

        # Create other stepper switch widgets
        stepper_switch_width = 220
        self.disable_idle_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Disable stepper when idle",
                                                 onvalue="on", offvalue="off", font=self.instruction_font,
                                                 width=stepper_switch_width)
        self.disable_idle_switch.select()
        CreateToolTip(self.disable_idle_switch, idle_tip)
        self.invert_dir_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Invert direction pin",
                                               onvalue="on", offvalue="off", font=self.instruction_font,
                                               width=stepper_switch_width)
        CreateToolTip(self.invert_dir_switch, invert_direction_tip)
        self.invert_step_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Invert step pin",
                                                onvalue="on", offvalue="off", font=self.instruction_font,
                                                width=stepper_switch_width)
        CreateToolTip(self.invert_step_switch, invert_step_tip)
        self.invert_enable_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Invert enable pin",
                                                  onvalue="on", offvalue="off", font=self.instruction_font,
                                                  width=stepper_switch_width)
        CreateToolTip(self.invert_enable_switch, invert_enable_tip)
        self.forward_only_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Force forward rotation only",
                                                 onvalue="on", offvalue="off", font=self.instruction_font,
                                                 width=stepper_switch_width, command=self.set_forward_only)
        CreateToolTip(self.forward_only_switch, forward_only_tip)
        self.reverse_only_switch = ctk.CTkSwitch(self.stepper_switch_frame, text="Force reverse rotation only",
                                                 onvalue="on", offvalue="off", font=self.instruction_font,
                                                 width=stepper_switch_width, command=self.set_reverse_only)
        CreateToolTip(self.reverse_only_switch, reverse_only_tip)

        # Layout stepper frame
        self.stepper_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.stepper_frame.grid_rowconfigure((0, 1), weight=1)
        self.stepper_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.stepper_combo.grid(column=1, row=0, columnspan=2, sticky="w", **grid_options)
        self.gearing_label.grid(column=2, row=0, sticky="e", **grid_options)
        self.gearing_entry.grid(column=3, row=0, sticky="w", **grid_options)

        # Layout stepper speed frame
        self.stepper_speed_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.stepper_speed_frame.grid_rowconfigure(0, weight=1)
        self.speed_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.speed_entry.grid(column=1, row=0, sticky="w", **grid_options)
        self.accel_label.grid(column=2, row=0, sticky="e", **grid_options)
        self.accel_entry.grid(column=3, row=0, sticky="w", **grid_options)

        # Layout stepper switches
        self.stepper_switch_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.stepper_switch_frame.grid_rowconfigure((0, 1), weight=1)
        self.disable_idle_switch.grid(column=0, row=0, **grid_options)
        self.forward_only_switch.grid(column=1, row=0, **grid_options)
        self.reverse_only_switch.grid(column=2, row=0, **grid_options)
        self.invert_dir_switch.grid(column=0, row=1, **grid_options)
        self.invert_step_switch.grid(column=1, row=1, **grid_options)
        self.invert_enable_switch.grid(column=2, row=1, **grid_options)

        # Create advanced widgets
        adv_switch_width = 220
        self.led_fast = ctk.StringVar(self, value=100)
        self.led_fast_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override fast LED blink rate",
                                             onvalue="on", offvalue="off", font=self.instruction_font,
                                             width=adv_switch_width)
        CreateToolTip(self.led_fast_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.led_fast_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.led_fast,
                                           font=self.instruction_font, width=60)
        self.led_slow = ctk.StringVar(self, value=500)
        self.led_slow_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override slow LED blink rate",
                                             onvalue="on", offvalue="off", font=self.instruction_font,
                                             width=adv_switch_width)
        CreateToolTip(self.led_slow_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.led_slow_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.led_slow,
                                           font=self.instruction_font, width=60)
        self.sanity_steps = ctk.StringVar(self, value=10000)
        self.sanity_steps_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override sanity step count",
                                                 onvalue="on", offvalue="off", font=self.instruction_font,
                                                 width=adv_switch_width)
        CreateToolTip(self.sanity_steps_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.sanity_steps_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.sanity_steps,
                                               font=self.instruction_font, width=60)
        self.home_sensitivity = ctk.StringVar(self, value=300)
        self.home_sensitivity_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override homing sensitivity",
                                                     onvalue="on", offvalue="off", font=self.instruction_font,
                                                     width=adv_switch_width)
        CreateToolTip(self.home_sensitivity_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.home_sensitivity_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.home_sensitivity,
                                                   font=self.instruction_font, width=60)
        self.full_step_count = ctk.StringVar(self, value=4096)
        self.full_step_count_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override full step count",
                                                    onvalue="on", offvalue="off", font=self.instruction_font,
                                                    width=adv_switch_width)
        CreateToolTip(self.full_step_count_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.full_step_count_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.full_step_count,
                                                  font=self.instruction_font, width=60)
        self.debounce_delay = ctk.StringVar(self, value=10)
        self.debounce_delay_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Override debounce delay",
                                                   onvalue="on", offvalue="off", font=self.instruction_font,
                                                   width=adv_switch_width)
        CreateToolTip(self.debounce_delay_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")
        self.debounce_delay_entry = ctk.CTkEntry(self.advanced_tab_frame, textvariable=self.debounce_delay,
                                                 font=self.instruction_font, width=60)
        self.debug_switch = ctk.CTkSwitch(self.advanced_tab_frame, text="Enable debug output",
                                          onvalue="on", offvalue="off", font=self.instruction_font,
                                          width=adv_switch_width)
        CreateToolTip(self.debug_switch, text=advanced_tip,
                      url="https://dcc-ex.com/ex-turntable/configure.html#advanced-configuration-options")

        # Layout advanced tab frame
        self.advanced_tab_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.advanced_tab_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.led_fast_switch.grid(column=0, row=0, sticky="e", **grid_options)
        self.led_fast_entry.grid(column=1, row=0, sticky="w", **grid_options)
        self.led_slow_switch.grid(column=2, row=0, sticky="e", **grid_options)
        self.led_slow_entry.grid(column=3, row=0, sticky="w", **grid_options)
        self.sanity_steps_switch.grid(column=0, row=1, sticky="e", **grid_options)
        self.sanity_steps_entry.grid(column=1, row=1, sticky="w", **grid_options)
        self.home_sensitivity_switch.grid(column=2, row=1, sticky="e", **grid_options)
        self.home_sensitivity_entry.grid(column=3, row=1, sticky="w", **grid_options)
        self.full_step_count_switch.grid(column=0, row=2, sticky="e", **grid_options)
        self.full_step_count_entry.grid(column=1, row=2, sticky="w", **grid_options)
        self.debounce_delay_switch.grid(column=2, row=2, sticky="e", **grid_options)
        self.debounce_delay_entry.grid(column=3, row=2, sticky="w", **grid_options)
        self.debug_switch.grid(column=0, row=3, sticky="e", **grid_options)

        # Layout main config frame
        frame_grid_options = {"sticky": "ew", "padx": 30, "pady": 5}
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_rowconfigure(1, weight=1)
        self.instruction_label.grid(column=0, row=0, **grid_options)
        self.stepper_tab_frame.grid_columnconfigure(0, weight=1)
        self.stepper_tab_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.stepper_frame.grid(column=0, row=0, **frame_grid_options)
        self.stepper_speed_frame.grid(column=0, row=1, **frame_grid_options)
        self.stepper_switch_frame.grid(column=0, row=2, **frame_grid_options)
        self.advanced_config_enabled.grid(column=0, row=5, sticky="e", **grid_options)
        self.config_tabview.grid(column=0, row=1, sticky="nsew", **grid_options)

        # Set toggles
        self.check_stepper(self.stepper_combo.get())
        self.set_home()
        self.set_limit()
        self.set_mode()
        self.set_relay()

    def decrement_address(self):
        """
        Function to decrement the I2C address
        """
        value = int(self.i2c_address.get())
        if value > 8:
            value -= 1
            self.i2c_address.set(value)
        self.validate_i2c_address()

    def increment_address(self):
        """
        Function to increment the I2C address
        """
        value = int(self.i2c_address.get())
        if value < 77:
            value += 1
            self.i2c_address.set(value)
        self.validate_i2c_address()

    def validate_i2c_address(self, event=None):
        """
        Function to validate the I2C address
        """
        if int(self.i2c_address.get()) < 8:
            self.process_error("I\u00B2C address must be between 0x8 and 0x77")
            self.i2c_address.set(8)
            self.i2c_address_entry.configure(text_color="red")
            self.next_back.disable_next()
        elif int(self.i2c_address.get()) > 77:
            self.process_error("I\u00B2C address must be between 0x8 and 0x77")
            self.i2c_address.set(77)
            self.i2c_address_entry.configure(text_color="red")
            self.next_back.disable_next()
        else:
            self.process_stop()
            self.i2c_address_entry.configure(text_color="#00353D")
            self.next_back.enable_next()

    def set_mode(self):
        """
        Highlight the chosen option for the mode toggle switch

        In traverser mode, ensure forward/reverse only options are deselected and disabled
        """
        if self.mode_switch.get() == "TURNTABLE":
            self.turntable_label.configure(font=self.bold_instruction_font)
            self.traverser_label.configure(font=self.small_italic_instruction_font)
            self.limit_switch.configure(state="disabled")
            self.limit_switch.configure(fg_color="#939BA2", progress_color="#939BA2")
            self.limit_high_label.configure(font=self.small_italic_instruction_font, text_color="white")
            self.limit_low_label.configure(font=self.small_italic_instruction_font, text_color="white")
            self.forward_only_switch.configure(state="normal")
            self.reverse_only_switch.configure(state="normal")
        else:
            self.turntable_label.configure(font=self.small_italic_instruction_font)
            self.traverser_label.configure(font=self.bold_instruction_font)
            self.limit_switch.configure(state="normal")
            self.limit_switch.configure(fg_color="#00A3B9", progress_color="#00A3B9")
            self.limit_high_label.configure(text_color="#00353D")
            self.limit_low_label.configure(text_color="#00353D")
            self.forward_only_switch.deselect()
            self.forward_only_switch.configure(state="disabled")
            self.reverse_only_switch.deselect()
            self.reverse_only_switch.configure(state="disabled")
            self.set_limit()

    def set_home(self):
        """
        Highlight the chosen option for the home sensor toggle switch
        """
        if self.home_switch.get() == "LOW":
            self.home_low_label.configure(font=self.bold_instruction_font)
            self.home_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.home_low_label.configure(font=self.small_italic_instruction_font)
            self.home_high_label.configure(font=self.bold_instruction_font)

    def set_limit(self):
        """
        Highlight the chosen option for the limit sensor toggle switch
        """
        if self.limit_switch.get() == "LOW":
            self.limit_low_label.configure(font=self.bold_instruction_font)
            self.limit_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.limit_low_label.configure(font=self.small_italic_instruction_font)
            self.limit_high_label.configure(font=self.bold_instruction_font)

    def set_relay(self):
        """
        Highlight the chosen option for the relay toggle switch
        """
        if self.relay_switch.get() == "LOW":
            self.relay_low_label.configure(font=self.bold_instruction_font)
            self.relay_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.relay_low_label.configure(font=self.small_italic_instruction_font)
            self.relay_high_label.configure(font=self.bold_instruction_font)

    def set_phase_switching(self):
        """
        Function to hide/display phase switching angle
        """
        if self.auto_switch.get() == "AUTO":
            self.phase_angle_entry.configure(border_color="#00A3B9", text_color="#00353D", state="normal")
        else:
            self.phase_angle_entry.configure(border_color="#979DA2", text_color="white", state="disabled")

    def get_steppers(self):
        """
        Function to read the defined stepper definitions from standard_steppers.h
        """
        self.stepper_list = []
        match = r'^#define\s(.+?)\sAccelStepper.*$'
        definition_file = fm.get_filepath(self.ex_turntable_dir, "standard_steppers.h")
        def_list = fm.get_list_from_file(definition_file, match)
        if def_list:
            self.stepper_list += def_list
            self.log.debug("Found stepper list %s", def_list)
        else:
            self.log.error("Could not get list of steppers")
        self.stepper_combo.configure(values=self.stepper_list)

    def check_stepper(self, value):
        """
        Function to ensure a motor driver has been selected
        """
        if value == "Select stepper driver":
            self.next_back.disable_next()
        else:
            self.next_back.enable_next()

    def set_advanced_config(self):
        """
        Sets next screen to be config editing rather than compile/upload
        """
        if self.advanced_config_enabled.get() == "on":
            self.next_back.set_next_text("Edit config")
        else:
            self.next_back.set_next_text("Compile and load")

    def set_forward_only(self):
        """
        Ensures reverse only switch is deselected if forward only is set
        """
        if self.reverse_only_switch.get() == "on":
            self.reverse_only_switch.deselect()

    def set_reverse_only(self):
        """
        Ensures forward only switch is deselected if reverse only is set
        """
        if self.forward_only_switch.get() == "on":
            self.forward_only_switch.deselect()

    def generate_config(self):
        """
        Validates all configuration parameters and if valid generates myConfig.h

        Any invalid parameters will prevent continuing and flag as errors
        """
        param_errors = []
        config_list = []
        if int(self.i2c_address.get()) < 8 or int(self.i2c_address.get()) > 77:
            param_errors.append("I\u00B2C address must be between 0x8 and 0x77")
        else:
            line = f"#define I2C_ADDRESS 0x{self.i2c_address.get()}\n"
            config_list.append(line)
        config_list.append(f"#define TURNTABLE_EX_MODE {self.mode_switch.get()}\n")
        if self.sensor_test_switch.get() == "on":
            config_list.append("#define SENSOR_TESTING\n")
        else:
            config_list.append("// #define SENSOR_TESTING\n")
        config_list.append(f"#define HOME_SENSOR_ACTIVE_STATE {self.home_switch.get()}\n")
        config_list.append(f"#define LIMIT_SENSOR_ACTIVE_STATE {self.limit_switch.get()}\n")
        config_list.append(f"#define RELAY_ACTIVE_STATE {self.relay_switch.get()}\n")
        config_list.append(f"#define PHASE_SWITCHING {self.auto_switch.get()}\n")
        if self.auto_switch.get() == "AUTO":
            try:
                int(self.phase_angle.get())
            except Exception:
                param_errors.append("Phase switch angle must be between 0 and 180")
            else:
                if (int(self.phase_angle.get()) < 0 or int(self.phase_angle.get()) > 180):
                    param_errors.append("Phase switch angle must be between 0 and 180")
                else:
                    line = f"#define PHASE_SWITCH_ANGLE {self.phase_angle.get()}\n"
                    config_list.append(line)
        if self.stepper_combo.get() == "Select stepper driver":
            param_errors.append("You must select a stepper driver")
        else:
            config_list.append(f"#define STEPPER_DRIVER {self.stepper_combo.get()}\n")
        if self.disable_idle_switch.get() == "on":
            config_list.append("#define DISABLE_OUTPUTS_IDLE\n")
        try:
            int(self.speed.get())
        except Exception:
            param_errors.append("You must provide a numeric speed value")
        else:
            if (int(self.speed.get()) < 10 or int(self.speed.get()) > 20000):
                param_errors.append("Speed must be between 10 and 20000")
            else:
                config_list.append(f"#define STEPPER_MAX_SPEED {self.speed.get()}\n")
        try:
            int(self.accel.get())
        except Exception:
            param_errors.append("You must provide a numeric acceleration value")
        else:
            if (int(self.accel.get()) < 1 or int(self.accel.get()) > 1000):
                param_errors.append("Acceleration must be between 1 and 1000")
            else:
                config_list.append(f"#define STEPPER_ACCELERATION {self.accel.get()}\n")
        if self.gearing_entry.cget("state") == "normal":
            try:
                int(self.gearing.get())
            except Exception:
                param_errors.append("You must provide a numeric gearing factor")
            else:
                if (int(self.gearing.get()) < 1 or int(self.gearing.get()) > 10):
                    param_errors.append("Gearing factor must be between 1 and 10")
                else:
                    config_list.append(f"#define STEPPER_GEARING_FACTOR {self.gearing.get()}\n")
        if self.invert_dir_switch.cget("state") == "normal":
            if self.invert_dir_switch.get() == "on":
                config_list.append("#define INVERT_DIRECTION\n")
            else:
                config_list.append("// #define INVERT_DIRECTION\n")
        if self.invert_step_switch.cget("state") == "normal":
            if self.invert_step_switch.get() == "on":
                config_list.append("#define INVERT_STEP\n")
            else:
                config_list.append("// #define INVERT_STEP\n")
        if self.invert_enable_switch.cget("state") == "normal":
            if self.invert_enable_switch.get() == "on":
                config_list.append("#define INVERT_ENABLE\n")
            else:
                config_list.append("// #define INVERT_ENABLE\n")
        if self.forward_only_switch.cget("state") == "normal":
            if self.forward_only_switch.get() == "on":
                if self.mode_switch.get() == "TRAVERSER":
                    param_errors.append("Traverser mode is incompatible with forward only rotation")
                else:
                    config_list.append("#define ROTATE_FORWARD_ONLY\n")
            else:
                config_list.append("// #define ROTATE_FORWARD_ONLY\n")
        if self.reverse_only_switch.cget("state") == "normal":
            if self.reverse_only_switch.get() == "on":
                if self.mode_switch.get() == "TRAVERSER":
                    param_errors.append("Traverser mode is incompatible with reverse only rotation")
                else:
                    config_list.append("#define ROTATE_REVERSE_ONLY\n")
            else:
                config_list.append("// #define ROTATE_REVERSE_ONLY\n")
        if self.led_fast_switch.get() == "on":
            try:
                int(self.led_fast.get())
            except Exception:
                param_errors.append("Fast LED delay must be numeric")
            else:
                config_list.append(f"#define LED_FAST {self.led_fast.get()}\n")
        else:
            config_list.append("#define LED_FAST 100\n")
        if self.led_slow_switch.get() == "on":
            try:
                int(self.led_slow.get())
            except Exception:
                param_errors.append("Slow LED delay must be numeric")
            else:
                config_list.append(f"#define LED_SLOW {self.led_slow.get()}\n")
        else:
            config_list.append("#define LED_SLOW 500\n")
        if self.debug_switch.get() == "on":
            config_list.append("#define DEBUG\n")
        else:
            config_list.append("// #define DEBUG\n")
        if self.sanity_steps_switch.get() == "on":
            try:
                int(self.sanity_steps.get())
            except Exception:
                param_errors.append("Sanity step count must be numeric")
            else:
                config_list.append(f"#define SANITY_STEPS {self.sanity_steps.get()}\n")
        else:
            config_list.append("// #define SANITY_STEPS 10000\n")
        if self.home_sensitivity_switch.get() == "on":
            try:
                int(self.home_sensitivity.get())
            except Exception:
                param_errors.append("Home sensitivity step count must be numeric")
            else:
                config_list.append(f"#define HOME_SENSITIVITY {self.home_sensitivity.get()}\n")
        else:
            config_list.append("// #define HOME_SENSITIVITY 300\n")
        if self.full_step_count_switch.get() == "on":
            try:
                int(self.full_step_count.get())
            except Exception:
                param_errors.append("Full step count must be numeric")
            else:
                config_list.append(f"#define FULL_STEP_COUNT {self.full_step_count.get()}\n")
        else:
            config_list.append("// #define FULL_STEP_COUNT 4096\n")
        if self.debounce_delay_switch.get() == "on":
            try:
                int(self.debounce_delay.get())
            except Exception:
                param_errors.append("Debounce delay must be numeric")
            else:
                config_list.append(f"#define DEBOUNCE_DELAY {self.debounce_delay.get()}\n")
        else:
            config_list.append("// #define DEBOUNCE_DELAY 10\n")
        if len(param_errors) > 0:
            message = ", ".join(param_errors)
            self.process_error(message)
        else:
            self.process_stop()
            file_contents = [("// config.h - Generated by EX-Installer " +
                              f"v{self.app_version} for {self.product_name} " +
                              f"{self.product_version_name}\n\n")]
            file_contents += config_list
            config_file_path = fm.get_filepath(self.ex_turntable_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config != config_file_path:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
            else:
                if self.advanced_config_enabled.get() == "on":
                    self.master.switch_view("advanced_config", self.product)
                else:
                    self.master.switch_view("compile_upload", self.product)
